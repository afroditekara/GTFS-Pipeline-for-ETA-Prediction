# GTFS-Pipeline
This project implements a data collection and processing pipeline designed to handle large volumes of static and real-time transit data from urban transit systems, specifically using General Transit Feed Specification (GTFS) data. The pipeline processes and merges this data to predict Estimated Time of Arrival (ETA) more accurately, utilizing a combination of static infrastructure data and dynamic real-time updates.

## Table of Contents
- Overview
- Features
- Pipeline Components
- Installation
- Usage
- Data Processing
- Results and Output

## Overview
The pipeline was developed to support machine learning models that predict ETAs by handling and processing large datasets. It is inspired by the methodology used in Chondrodima et al. (2022) but adapted to fit the computational constraints of this study.

## Data 
The transit data used in this pipeline is derived from GTFS (General Transit Feed Specification) feeds:

### Static Data
Contains information on fixed transit infrastructure, such as routes, stops, and schedules.

### Real-time Data
Includes updates on the status of vehicles and trips, enabling dynamic adjustments for ETA predictions.

