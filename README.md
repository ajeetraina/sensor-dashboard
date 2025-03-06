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

[View detailed database structure diagram](database_structure.md)

## Project Components

### 1. Sensor Data Fetcher (`sensor_data.py`)
- Python script to fetch and analyze sensor data from Neo4j
- Calculates average values for temperature, humidity, and pressure
- Extracts readings by classification and time groups

### 2. Temperature Alert System (`temperature_alert.py`)
- Monitors temperature changes in real-time
- Alerts when temperature rises by a configurable threshold (default: 2°C)
- Configurable check interval (default: 60 seconds)

### 3. Web Dashboard (`app.py`)
- Interactive dashboard built with Dash and Plotly
- Visualizes temperature, humidity, and pressure trends
- Displays latest sensor readings and average values
- Auto-refreshes data every minute

### 4. Docker Support
- Dockerfile for containerizing the application
- Docker Compose setup for running the dashboard with Neo4j

## Sample Data

[View sample sensor readings](sample_sensor_values.md)

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

### Run Web Dashboard

```bash
python app.py
```

Then open `http://localhost:8050` in your browser.

### Using Docker Compose

```bash
docker-compose up -d
```

This will start both the dashboard and a Neo4j instance.

## Project Structure

```
sensor-dashboard/
├── README.md                  # Project documentation
├── database_structure.md      # Database diagram and documentation
├── sample_sensor_values.md    # Sample sensor data
├── requirements.txt          # Python dependencies
├── sensor_data.py            # Script to fetch and analyze sensor data
├── temperature_alert.py      # Temperature monitoring and alert system
├── app.py                    # Web dashboard application
├── Dockerfile                # Docker container definition
└── docker-compose.yml        # Docker Compose configuration
```

## Future Enhancements

- Add user authentication for the dashboard
- Implement predictive analytics for sensor readings
- Create mobile notifications for alerts
- Add more visualization types and filtering options
- Support for additional sensor types