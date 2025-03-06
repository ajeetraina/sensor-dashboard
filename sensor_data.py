#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import pandas as pd
from neo4j import GraphDatabase
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sensor_data.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SensorDataFetcher:
    def __init__(self, uri, username, password):
        """Initialize the Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        logger.info("Connected to Neo4j database")
        
    def close(self):
        """Close the Neo4j connection"""
        self.driver.close()
        logger.info("Disconnected from Neo4j database")
        
    def get_all_sensor_readings(self):
        """Fetch all sensor readings from the database"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:SensorReading)
                RETURN s.temperature as temperature, 
                       s.humidity as humidity, 
                       s.pressure as pressure, 
                       s.timestamp as timestamp
                ORDER BY s.timestamp DESC
            """)
            
            # Convert to DataFrame
            data = [{'temperature': record['temperature'],
                     'humidity': record['humidity'],
                     'pressure': record['pressure'],
                     'timestamp': datetime.fromtimestamp(record['timestamp']['low'])} 
                    for record in result]
            
            df = pd.DataFrame(data)
            logger.info(f"Retrieved {len(df)} sensor readings")
            return df
    
    def get_readings_by_classification(self, classification_type, classification_name):
        """Fetch sensor readings by classification"""
        relationship_types = {
            'temperature': 'HAS_TEMPERATURE_CLASS',
            'humidity': 'HAS_HUMIDITY_CLASS',
            'gas': 'HAS_GAS_CLASS'
        }
        
        if classification_type not in relationship_types:
            raise ValueError(f"Invalid classification type: {classification_type}")
        
        rel_type = relationship_types[classification_type]
        
        with self.driver.session() as session:
            result = session.run(f"""
                MATCH (s:SensorReading)-[:{rel_type}]->(c:Classification {{name: $name}})
                RETURN s.temperature as temperature, 
                       s.humidity as humidity, 
                       s.pressure as pressure, 
                       s.timestamp as timestamp
                ORDER BY s.timestamp DESC
            """, name=classification_name)
            
            # Convert to DataFrame
            data = [{'temperature': record['temperature'],
                     'humidity': record['humidity'],
                     'pressure': record['pressure'],
                     'timestamp': datetime.fromtimestamp(record['timestamp']['low'])} 
                    for record in result]
            
            df = pd.DataFrame(data)
            logger.info(f"Retrieved {len(df)} readings with {classification_type} classification '{classification_name}'")
            return df
    
    def get_readings_by_time_group(self, time_group_name):
        """Fetch sensor readings by time group"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:SensorReading)-[:BELONGS_TO_TIME_GROUP]->(t:TimeGroup {name: $name})
                RETURN s.temperature as temperature, 
                       s.humidity as humidity, 
                       s.pressure as pressure, 
                       s.timestamp as timestamp
                ORDER BY s.timestamp DESC
            """, name=time_group_name)
            
            # Convert to DataFrame
            data = [{'temperature': record['temperature'],
                     'humidity': record['humidity'],
                     'pressure': record['pressure'],
                     'timestamp': datetime.fromtimestamp(record['timestamp']['low'])} 
                    for record in result]
            
            df = pd.DataFrame(data)
            logger.info(f"Retrieved {len(df)} readings in time group '{time_group_name}'")
            return df
            
    def get_average_values(self):
        """Calculate average values for all sensor readings"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:SensorReading)
                RETURN avg(s.temperature) as avg_temperature,
                       avg(s.humidity) as avg_humidity,
                       avg(s.pressure) as avg_pressure,
                       count(s) as count
            """)
            
            record = result.single()
            avg_values = {
                'avg_temperature': record['avg_temperature'],
                'avg_humidity': record['avg_humidity'],
                'avg_pressure': record['avg_pressure'],
                'count': record['count']
            }
            
            logger.info(f"Calculated averages from {avg_values['count']} readings")
            return avg_values

if __name__ == "__main__":
    # Environment variables for database connection
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
    
    try:
        # Initialize and connect to database
        fetcher = SensorDataFetcher(neo4j_uri, neo4j_user, neo4j_password)
        
        # Get average values
        avg_values = fetcher.get_average_values()
        print("\n===== AVERAGE SENSOR VALUES =====")
        print(f"Temperature: {avg_values['avg_temperature']:.2f}°C")
        print(f"Humidity: {avg_values['avg_humidity']:.2f}%")
        print(f"Pressure: {avg_values['avg_pressure']:.2f} hPa")
        print(f"Total readings: {avg_values['count']}")
        
        # Get 5 latest readings
        all_readings = fetcher.get_all_sensor_readings()
        if not all_readings.empty:
            print("\n===== 5 LATEST SENSOR READINGS =====")
            print(all_readings.head(5).to_string(index=False))
        
        # Close connection
        fetcher.close()
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        sys.exit(1)
