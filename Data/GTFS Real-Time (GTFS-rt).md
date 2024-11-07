While the GTFS-s feed provides static information about the transit network, the GTFS-rt feed supplies dynamic, real-time data collected during vehicle trips. This data is typically based on GPS tracking and provides up-to-the-minute updates on the status of the transit network. The GTFS-rt feed is used to provide passengers with current information about vehicle positions, service alerts, and trip updates. The real-time data is encoded using the Protocol Buffers (protobuf) format, an open-source standard for efficiently serializing structured data.
 The GTFS-rt feed supports three main types of information:
1.	Trip Updates: Include predicted arrival and/or departure times for stops along each trip. This data helps in estimating real-time ETAs (Estimated Time of Arrival) for each stop a vehicle will serve.
2.	Vehicle Positions: Provide updates on the current location of individual transit vehicles. The data includes the vehicle's geographic coordinates and additional information like bearing and speed, allowing for real-time tracking of vehicles.
3.	Service Alerts: Include updates on disruptions in the transit network, such as delays, detours, or route closures. These alerts are provided as human-readable messages that help passengers understand the current state of the transit network and plan their journeys accordingly.
 By integrating the GTFS-s and GTFS-rt feeds, transit agencies can provide a comprehensive view of their operations, combining scheduled information with real-time updates to deliver accurate and reliable transit data to passengers. 

Below the links for the data stacks:
Static schedule data
https://svc.metrotransit.org/mtgtfs/gtfs.zip 
