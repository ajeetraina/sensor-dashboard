#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import logging
from neo4j import GraphDatabase
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("temperature_alert.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TemperatureMonitor:
    def __init__(self, uri, username, password):
        """Initialize the Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        logger.info("Connected to Neo4j database")
        self.last_temp = None
        
    def close(self):
        """Close the Neo4j connection"""
        self.driver.close()
        logger.info("Disconnected from Neo4j database")
    
    def get_latest_temperature(self):
        """Get the latest temperature reading"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:SensorReading)
                RETURN s.temperature as temperature, s.timestamp as timestamp
                ORDER BY s.timestamp DESC
                LIMIT 1
            """)
            
            record = result.single()
            if record:
                temp = record['temperature']
                timestamp = datetime.fromtimestamp(record['timestamp']['low'])
                return temp, timestamp
            return None, None
    
    def monitor_temperature(self, threshold=2.0, interval=60):
        """Monitor temperature and alert when it rises by the threshold"""
        logger.info(f"Starting temperature monitoring (threshold: {threshold}°C, interval: {interval}s)")
        
        try:
            while True:
                current_temp, timestamp = self.get_latest_temperature()
                
                if current_temp is not None:
                    logger.info(f"Current temperature: {current_temp:.2f}°C at {timestamp}")
                    
                    # Check if we have a previous temperature to compare with
                    if self.last_temp is not None:
                        # Calculate the temperature difference
                        temp_diff = current_temp - self.last_temp
                        
                        # Alert if temperature has risen by more than the threshold
                        if temp_diff >= threshold:
                            logger.warning(f"ALERT: Temperature rose by {temp_diff:.2f}°C from {self.last_temp:.2f}°C to {current_temp:.2f}°C")
                            print(f"\n🔥 ALERT: Temperature rose by {temp_diff:.2f}°C from {self.last_temp:.2f}°C to {current_temp:.2f}°C at {timestamp}")
                    
                    # Update the last temperature
                    self.last_temp = current_temp
                else:
                    logger.warning("No temperature readings found")
                
                # Wait for the next check
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Temperature monitoring stopped by user")
        except Exception as e:
            logger.error(f"Error in temperature monitoring: {str(e)}", exc_info=True)

if __name__ == "__main__":
    # Environment variables for database connection
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
    
    # Get threshold from command line argument or use default
    threshold = 2.0
    if len(sys.argv) > 1:
        try:
            threshold = float(sys.argv[1])
        except ValueError:
            logger.error(f"Invalid threshold value: {sys.argv[1]}")
            print(f"Invalid threshold value: {sys.argv[1]}. Using default: {threshold}°C")
    
    # Get check interval from command line argument or use default
    interval = 60  # seconds
    if len(sys.argv) > 2:
        try:
            interval = int(sys.argv[2])
        except ValueError:
            logger.error(f"Invalid interval value: {sys.argv[2]}")
            print(f"Invalid interval value: {sys.argv[2]}. Using default: {interval}s")
    
    try:
        # Initialize and connect to database
        monitor = TemperatureMonitor(neo4j_uri, neo4j_user, neo4j_password)
        
        # Start monitoring
        print(f"Starting temperature monitoring (threshold: {threshold}°C, interval: {interval}s)")
        print("Press Ctrl+C to stop")
        monitor.monitor_temperature(threshold, interval)
        
        # Close connection
        monitor.close()
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        sys.exit(1)