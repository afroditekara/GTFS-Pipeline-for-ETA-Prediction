# GTFS-Pipeline
This project implements a data collection and processing pipeline designed to handle large volumes of static and real-time transit data from urban transit systems, specifically using General Transit Feed Specification (GTFS) data. The pipeline processes and merges this data to predict Estimated Time of Arrival (ETA) more accurately, utilizing a combination of static infrastructure data and dynamic real-time updates. The Pipeline was deployed for a master thesis in University of Piraeus with the Title Traffic Prediction on Road Networks. The thesis pdf can be found on the files section.

## Table of Contents
- Overview
- Data
- Features
- Pipeline Components
- Installation
- Database Setup
- Data Processing
- Results and Output

## Overview
The pipeline was developed to support machine learning models that predict ETAs by handling and processing large datasets. It is inspired by the methodology used in Chondrodima et al. (2022) but adapted to fit the computational constraints of this study.

https://www.sciencedirect.com/science/article/pii/S2667096822000295

## Data 
The transit data used in this pipeline is derived from GTFS (General Transit Feed Specification) feeds:

### Static Data
Contains information on fixed transit infrastructure, such as routes, stops, and schedules.

### Real-time Data
Includes updates on the status of vehicles and trips, enabling dynamic adjustments for ETA predictions.

## Features

- Comprehensive Data Processing:
  - End-to-end pipeline handling both static and real-time data
  - Integrated data quality checks to ensure consistency
  - Geospatial validation for route accuracy
- Real-time Data Integration:
  - Fetches real-time GTFS data every five seconds
  - Refreshes static GTFS data every two hours
- Geospatial Support:
  - Uses PostgreSQL with PostGIS for spatial operations
  - Supports spatial data processing for accurate geographic data handling

 ## Pipeline Components
1. Environment Setup:
  - Python libraries: SQLAlchemy, pandas, dask, GeoPandas, and osmnx.
2. Database Connection:
  - PostgreSQL with PostGIS for spatial data management.
3. Data Retrieval:
  - Static GTFS data fetched periodically.
  - Real-time GTFS data updated every five seconds.
4. Data Processing:
  - Checksum Verification: Detects changes in static and real-time data.
  - Data Quality Checks: Ensures consistency, removes duplicates, and resolves timestamp errors.
  - Spatial Validation: Cross-references routes with OpenStreetMap data.

## Installation
### Prerequisites
Python 3.7+
PostgreSQL with PostGIS

## Database Setup
1. Set up PostgreSQL and enable the PostGIS extension.
2. Configure database connection credentials in the code.

## Data Processing
- Checksum Verification: Detects data changes.
- Data Quality Checks: Ensures data consistency and correctness.
- Merging & Cleaning: Combines static and real-time data with error handling for missing keys.

## Results and Output
- Processed data stored in PostgreSQL for model training.
- Intermediate data saved as CSV files for auditing and debugging.
