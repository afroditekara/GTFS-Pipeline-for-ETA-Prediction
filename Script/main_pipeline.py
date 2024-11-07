# Import Libraries and Modules
import re
from sqlalchemy import create_engine, inspect
import pandas as pd
import requests
import threading
import hashlib
from datetime import datetime, timedelta
from io import BytesIO
from zipfile import ZipFile
import gtfs_realtime_pb2
import time
import geopandas as gpd
from shapely.geometry import box
import osmnx as ox
import os
import logging
import gc
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from geoalchemy2 import Geometry
from shapely.wkt import dumps as wkt_dumps
from shapely.geometry import Point
import dask.dataframe as dd
import sys

# Logging and Output Redirection Setup
sys.stdout = open('script_output.log', 'w')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('gtfs_processing.log'),
        logging.StreamHandler()
    ]
)

# Database Connection
DATABASE_URL = "postgresql://postgres:12345@localhost/eta"
engine = create_engine(DATABASE_URL)

# GTFS URLs (Static and Real-time Feeds)
GTFS_STATIC_URL = "https://svc.metrotransit.org/mtgtfs/gtfs.zip"
GTFS_REALTIME_URLS = {
    "TripUpdate": "https://svc.metrotransit.org/mtgtfs/tripupdates.pb",
    "VehiclePosition": "https://svc.metrotransit.org/mtgtfs/vehiclepositions.pb",
    "ServiceAlerts": "https://svc.metrotransit.org/mtgtfs/alerts.pb"
}

# Retry Session Function
def requests_retry_session(retries=5, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Utility Functions (Checksum, Data Change Detection)
def compute_checksum(data):
    """Compute MD5 checksum for the given data."""
    return hashlib.md5(data).hexdigest()

def has_data_changed(data_type, data):
    """Check if the data has changed based on its checksum."""
    checksum_filename = f"{data_type}_checksum.txt"
    new_checksum = compute_checksum(data)
    try:
        with open(checksum_filename, 'r') as f:
            old_checksum = f.read().strip()
    except FileNotFoundError:
        old_checksum = ""
    if new_checksum != old_checksum:
        with open(checksum_filename, 'w') as f:
            f.write(new_checksum)
        return True
    return False

# Load GTFS Static Data in Chunks
def load_gtfs_static_data_chunked(gtfs_static_url, chunk_size=50000):
    try:
        response = requests_retry_session().get(gtfs_static_url)
        if response.status_code == 200:
            content = response.content
            if has_data_changed("gtfs_static", content) or not static_data_exists():
                zipfile = ZipFile(BytesIO(content))
                for filename in zipfile.namelist():
                    if filename.endswith('.txt'):
                        df_chunks = pd.read_csv(zipfile.open(filename), chunksize=chunk_size)
                        table_name = os.path.splitext(filename)[0]
                        
                        for chunk in df_chunks:
                            chunk.to_csv(f'{table_name}.csv', mode='a', index=False)  # Append to CSV file
                            chunk.to_sql(table_name, engine, if_exists='replace', index=False)
                        del df_chunks  # Release memory
                        gc.collect()
    except Exception as e:
        time.sleep(10)  # Wait for 10 seconds before retrying

# Check if Static Data Exists
def static_data_exists():
    """Check if the required static data tables exist in the database."""
    inspector = inspect(engine)
    required_tables = ['trips', 'stops', 'routes', 'shapes', 'agency', 'calendar', 'calendar_dates']
    for table in required_tables:
        if table not in inspector.get_table_names():
            return False
    return True

# Verify Database Contents
def verify_database():
    """Verify the contents of the database tables."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    for table in tables:
        df = pd.read_sql_table(table, engine)
        df.to_csv(f'{table}.csv', mode='a', index=False)  # Save to CSV
        del df  # Release memory
        gc.collect()

# Fetch and Process GTFS Real-Time Data
def fetch_gtfs_realtime_data(url):
    while True:
        try:
            response = requests_retry_session().get(url)
            if response.status_code == 200:
                feed = gtfs_realtime_pb2.FeedMessage()
                try:
                    feed.ParseFromString(response.content)
                    return feed
                except gtfs_realtime_pb2.message.DecodeError as e:
                    pass
            else:
                pass
        except Exception as e:
            time.sleep(10)  # Wait for 10 seconds before retrying
            continue
        break
    return None

# Filter Invalid Timestamps
def filter_invalid_timestamps(df, timestamp_col):
    """Filter out rows with invalid timestamps."""
    invalid_start = datetime(1970, 1, 2)
    df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors='coerce')
    df = df[df[timestamp_col] >= invalid_start]
    return df

# Process Trip Updates
def process_trip_update_feed(feed):
    updates = []
    for entity in feed.entity:
        if entity.HasField('trip_update'):
            for update in entity.trip_update.stop_time_update:
                updates.append({
                    'trip_id': entity.trip_update.trip.trip_id,
                    'vehicle_id': entity.trip_update.vehicle.id,
                    'stop_sequence': update.stop_sequence,
                    'arrival_delay': update.arrival.delay,
                    'departure_delay': update.departure.delay,
                    'timestamp': datetime.utcfromtimestamp(entity.trip_update.timestamp)
                })
    df = pd.DataFrame(updates)
    df = filter_invalid_timestamps(df, 'timestamp')
    return df

# Process Service Alerts
def process_service_alerts_feed(feed):
    alerts = []
    for entity in feed.entity:
        if entity.HasField('alert'):
            for period in entity.alert.active_period:
                start_time = datetime.utcfromtimestamp(period.start) if period.HasField('start') else None
                end_time = datetime.utcfromtimestamp(period.end) if period.HasField('end') else None
                
                alerts.append({
                    'alert_id': entity.id,
                    'start_time': start_time,
                    'end_time': end_time,
                    'cause': entity.alert.cause,
                    'effect': entity.alert.effect,
                    'url': entity.alert.url.translation[0].text if entity.alert.HasField('url') else None,
                    'header_text': entity.alert.header_text.translation[0].text if entity.alert.HasField('header_text') else None,
                    'description_text': entity.alert.description_text.translation[0].text if entity.alert.HasField('description_text') else None
                })
    df = pd.DataFrame(alerts)
    df = filter_invalid_timestamps(df, 'start_time')
    df = filter_invalid_timestamps(df, 'end_time')
    return df

# Process Vehicle Position Data
def process_vehicle_position_feed(feed):
    positions = []
    for entity in feed.entity:
        if entity.HasField('vehicle'):
            vehicle = entity.vehicle
            positions.append({
                'vehicle_id': vehicle.vehicle.id,
                'trip_id': vehicle.trip.trip_id,
                'route_id': vehicle.trip.route_id,
                'direction_id': vehicle.trip.direction_id,
                'latitude': vehicle.position.latitude,
                'longitude': vehicle.position.longitude,
                'bearing': vehicle.position.bearing,
                'speed': vehicle.position.speed,
                'timestamp': datetime.utcfromtimestamp(vehicle.timestamp),
                'congestion_level': vehicle.congestion_level if vehicle.HasField('congestion_level') else None,
                'stop_id': vehicle.stop_id if vehicle.HasField('stop_id') else None,
                'current_stop_sequence': vehicle.current_stop_sequence if vehicle.HasField('current_stop_sequence') else None,
                'current_status': vehicle.current_status if vehicle.HasField('current_status') else None,
                'vehicle_label': vehicle.vehicle.label if vehicle.HasField('vehicle') else None
            })
    df = pd.DataFrame(positions)
    df = filter_invalid_timestamps(df, 'timestamp')
    return df

# Real-Time Data Processing Loop
def process_realtime_data_continuously():
    while True:
        for feed_type, url in GTFS_REALTIME_URLS.items():
            feed = fetch_gtfs_realtime_data(url)
            if feed is not None:
                serialized_feed = feed.SerializeToString()
                if has_data_changed(feed_type, serialized_feed):
                    table_name = f"{feed_type.lower()}"
                    if feed_type == 'TripUpdate':
                        df = process_trip_update_feed(feed)
                        table_name = 'trip_updates'  # Adjust to match your table name
                    elif feed_type == 'VehiclePosition':
                        df = process_vehicle_position_feed(feed)
                        table_name = 'vehicle_positions'  # Adjust to match your table name
                    elif feed_type == 'ServiceAlerts':
                        df = process_service_alerts_feed(feed)
                        table_name = 'service_alerts'  # Adjust to match your table name
                    
                    # Sample 3% of the data
                    df = df.sample(frac=0.02)
                    
                    # Check if DataFrame is not empty before inserting
                    if not df.empty:
                        df.to_csv(f'temp_{table_name}.csv', mode='a', index=False)  # Append to CSV file
                        df.to_sql(table_name, engine, if_exists='append', index=False)
                        os.remove(f'temp_{table_name}.csv')  # Clean up the temporary file
                        del df  # Release memory
                        gc.collect()  # Explicitly call the garbage collector
                del serialized_feed  # Release memory
                del feed  # Release memory
                gc.collect()  # Explicitly call the garbage collector
        time.sleep(5)  # Wait for 5 seconds before the next cycle

# Additional Helper Functions
def extract_detour_points(description_text):
    # Extract start and end points of detour from the description
    pass

def delete_stop_from_route(route_id, stop_id):
    # Delete a stop from the route in the database
    pass

def delete_detoured_route_part(route_id, description_text):
    # Delete the detoured route part from the shapes table
    pass

def update_schedule_data_with_alerts():
    # Update the schedule data with real-time alerts (e.g., detours, no service)
    pass

# GTFS Table Merging 
def merge_gtfs_tables(retry_delay=10):
    # Logic for merging GTFS tables
    pass

def delete_detoured_segments_from_merged_data():
    # Logic to delete detoured segments from merged GTFS data
    pass

def validate_and_correct_realtime_data():
    # Validate and correct real-time data against GTFS static data
    pass

# Periodic and Continuous Tasks
def merge_gtfs_tables_continuously():
    # Continuously merge GTFS tables and handle detours/alerts
    pass

def periodically_update_static_data():
    # Periodically update static GTFS data (every two hours)
    pass

def validate_with_osm():
    # Validate GTFS shapes and stops with OpenStreetMap (OSM) data
    pass

# Main Execution Flow
if __name__ == "__main__":
    # Load GTFS static data initially
    load_gtfs_static_data_chunked(GTFS_STATIC_URL)

    # Verify the initial load
    verify_database()

    # Ensure shapes table exists before proceeding with validation
    inspector = inspect(engine)
    if 'shapes' in inspector.get_table_names():
        # Validate data with OSM
        validate_with_osm()
    else:
        pass

    # Start the continuous processing of real-time data
    threading.Thread(target=process_realtime_data_continuously).start()

    # Add a delay to allow real-time data to be processed
    time.sleep(60)  # Wait for 1 minute to ensure real-time data tables are populated

    # Start continuous merging of GTFS tables, updating schedule data with alerts, and validating data
    threading.Thread(target=merge_gtfs_tables_continuously).start()

    # Start the periodic update of static data
    threading.Thread(target=periodically_update_static_data).start()
