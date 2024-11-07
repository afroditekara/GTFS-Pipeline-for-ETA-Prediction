A.1. GTFS Static (GTFS-s) Feed Files

The GTFS-s feed is typically a collection of comma-separated values (CSV) files containing relatively static information about a public transit (PT) network. This static information includes details that change infrequently, such as routes, stops, and schedules. Updates to these files may occur periodically, for example, when schedules are adjusted seasonally or when a new route is introduced.
 The GTFS-s feed consists of several mandatory and optional files that together provide a comprehensive description of a PT network:
 
1.	agency.txt: This file includes information about the transit agencies providing the data in the feed. Each transit agency is identified by an agency_id. It contains fields such as agency_name, agency_url, and agency_timezone, which describe the agency's name, website, and timezone, respectively.
2.	routes.txt: Contains the routes within the PT network, each identified by a route_id. Routes represent a specific path taken by a PT vehicle, and this file includes fields such as route_short_name, route_long_name, and route_type to provide a more detailed description of each route.
3.	trips.txt: This file lists all the trips that occur on the routes in the PT network, each identified by a trip_id. A trip describes the movement of a PT vehicle along a specific route at a certain time. This file also includes fields such as service_id, trip_headsign, and direction_id.
4.	stops.txt: Details all the stops in the PT network, each identified by a stop_id. This file provides information such as stop_name, stop_lat, and stop_lon, which indicate the stop's name and geographic coordinates (latitude and longitude) based on the WGS 84 datum.
5.	stop_times.txt: Provides detailed scheduling information by listing the times that each trip stops at each stop. Each entry is identified by the associated trip_id and stop_id and includes fields such as arrival_time, departure_time, and stop_sequence.
6.	calendar.txt (Conditionally Required): Defines the days of service for the trips, each identified by a service_id. This file specifies a weekly schedule, with fields indicating whether the service operates on each day of the week.
7.	calendar_dates.txt (Conditionally Required): Provides exceptions to the regular schedule defined in calendar.txt, also associated with a service_id. This file includes fields such as date and exception_type to indicate specific dates when service is added or removed.
8.	shapes.txt (Optional): Defines the physical path that the vehicle travels for each trip, identified by a shape_id. This file contains a series of points defined by shape_pt_lat and shape_pt_lon that outline the route's shape on a map.
9.	feed_info.txt (Optional): Contains metadata about the dataset itself, including information such as feed_publisher_name, feed_publisher_url, and feed_version.

These files, when combined, provide a complete set of static information for a PT network. In a PT network, stops represent specific locations where passengers can board or disembark from PT vehicles. A route is defined by a fixed sequence of stops, and a trip represents a single journey along a route, occurring at a specific time.

Below the links for the data stacks:
Static schedule data
https://svc.metrotransit.org/mtgtfs/gtfs.zip 
