# Sensor Dashboard

A dashboard for monitoring environmental sensor readings from a Neo4j database.

## Overview

This project provides tools to monitor and visualize sensor data stored in a Neo4j database. The system handles temperature, humidity, and pressure readings, and includes an alert system for temperature changes.

## Database Structure

The Neo4j database contains the following node types:

- **SensorReading**: 352 nodes with properties:
  - temperature
  - humidity
  - pressure
  - timestamp

- **Classification**: 3 nodes (High, Medium, Low)

- **TimeGroup**: 3 nodes (Early Readings, Middle Readings, Late Readings)

### Relationships:
- **HAS_TEMPERATURE_CLASS**: Connects SensorReading → Classification (temperature level)
- **HAS_HUMIDITY_CLASS**: Connects SensorReading → Classification (humidity level)
- **HAS_GAS_CLASS**: Connects SensorReading → Classification (gas level)
- **BELONGS_TO_TIME_GROUP**: Connects SensorReading → TimeGroup (time period)

## Features

- Fetch and analyze sensor data from Neo4j database
- Calculate average values for temperature, humidity, and pressure
- Monitor temperature changes and alert when rising above threshold
- Visualize sensor data with graphs and charts

## Installation

```bash
# Clone the repository
git clone https://github.com/ajeetraina/sensor-dashboard.git
cd sensor-dashboard

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Configuration

Set the following environment variables for database connection:

```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your_password"
```

### Fetch Sensor Data

```bash
python sensor_data.py
```

### Temperature Alert System

```bash
# Monitor with default settings (2°C threshold, 60 second interval)
python temperature_alert.py

# Custom threshold and interval
python temperature_alert.py 1.5 30
```

## Project Structure

- `sensor_data.py`: Main script to fetch and analyze sensor data
- `temperature_alert.py`: Temperature monitoring and alert system
- `requirements.txt`: Required Python packages
