#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc

from sensor_data import SensorDataFetcher

# Initialize Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Environment variables for database connection
neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
neo4j_user = os.getenv("NEO4J_USER", "neo4j")
neo4j_password = os.getenv("NEO4J_PASSWORD", "password")

# Initialize the sensor data fetcher
fetcher = SensorDataFetcher(neo4j_uri, neo4j_user, neo4j_password)

# Dashboard layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Environmental Sensor Dashboard", className="mb-4"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Data Refresh"),
                dbc.CardBody([
                    dbc.Button("Refresh Data", id="refresh-button", color="primary", className="me-2"),
                    dcc.Interval(id="interval-component", interval=60000, n_intervals=0),  # 60 seconds
                    html.Div(id="last-update-time")
                ])
            ], className="mb-4")
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Average Sensor Values"),
                dbc.CardBody(id="avg-values-card")
            ], className="mb-4")
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Temperature Over Time"),
                dbc.CardBody([
                    dcc.Graph(id="temperature-graph")
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Humidity Over Time"),
                dbc.CardBody([
                    dcc.Graph(id="humidity-graph")
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Pressure Over Time"),
                dbc.CardBody([
                    dcc.Graph(id="pressure-graph")
                ])
            ])
        ], width=6)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Latest Sensor Readings"),
                dbc.CardBody([
                    html.Div(id="latest-readings-table")
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            html.Footer([
                html.P("Sensor Dashboard - Created with Python, Neo4j, and Dash")
            ], className="text-center text-muted pb-3 pt-3")
        ], width=12)
    ])
], fluid=True)

# Callback to update all visualizations
@app.callback(
    [
        Output("avg-values-card", "children"),
        Output("temperature-graph", "figure"),
        Output("humidity-graph", "figure"),
        Output("pressure-graph", "figure"),
        Output("latest-readings-table", "children"),
        Output("last-update-time", "children")
    ],
    [
        Input("refresh-button", "n_clicks"),
        Input("interval-component", "n_intervals")
    ]
)
def update_dashboard(n_clicks, n_intervals):
    # Get current time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Get average values
        avg_values = fetcher.get_average_values()
        
        # Create average values card content
        avg_card_content = [
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H3(f"{avg_values['avg_temperature']:.2f} °C", className="text-center"),
                        html.P("Avg Temperature", className="text-center text-muted")
                    ], className="p-3")
                ], width=4),
                dbc.Col([
                    html.Div([
                        html.H3(f"{avg_values['avg_humidity']:.2f} %", className="text-center"),
                        html.P("Avg Humidity", className="text-center text-muted")
                    ], className="p-3")
                ], width=4),
                dbc.Col([
                    html.Div([
                        html.H3(f"{avg_values['avg_pressure']:.2f} hPa", className="text-center"),
                        html.P("Avg Pressure", className="text-center text-muted")
                    ], className="p-3")
                ], width=4)
            ])
        ]
        
        # Get sensor readings
        df = fetcher.get_all_sensor_readings()
        
        if not df.empty:
            # Temperature graph
            temp_fig = px.line(
                df.sort_values('timestamp'), 
                x='timestamp', 
                y='temperature',
                title="Temperature Over Time",
                labels={"timestamp": "Time", "temperature": "Temperature (°C)"},
                template="plotly_white"
            )
            temp_fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            
            # Humidity graph
            humidity_fig = px.line(
                df.sort_values('timestamp'), 
                x='timestamp', 
                y='humidity',
                title="Humidity Over Time",
                labels={"timestamp": "Time", "humidity": "Humidity (%)"},
                template="plotly_white"
            )
            humidity_fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            
            # Pressure graph
            pressure_fig = px.line(
                df.sort_values('timestamp'), 
                x='timestamp', 
                y='pressure',
                title="Pressure Over Time",
                labels={"timestamp": "Time", "pressure": "Pressure (hPa)"},
                template="plotly_white"
            )
            pressure_fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            
            # Latest readings table
            latest_readings = df.sort_values('timestamp', ascending=False).head(5)
            table = dbc.Table.from_dataframe(
                latest_readings[['timestamp', 'temperature', 'humidity', 'pressure']],
                striped=True,
                bordered=True,
                hover=True,
                responsive=True
            )
        else:
            # Create empty figures if no data
            temp_fig = go.Figure()
            temp_fig.update_layout(title="No temperature data available")
            
            humidity_fig = go.Figure()
            humidity_fig.update_layout(title="No humidity data available")
            
            pressure_fig = go.Figure()
            pressure_fig.update_layout(title="No pressure data available")
            
            table = html.Div("No sensor readings available")
        
        update_text = html.P(["Last updated: ", html.Strong(current_time)])
        
        return avg_card_content, temp_fig, humidity_fig, pressure_fig, table, update_text
        
    except Exception as e:
        # Handle errors
        error_message = f"Error: {str(e)}"
        return (
            html.Div(error_message, className="text-danger"),
            go.Figure().update_layout(title="Error loading temperature data"),
            go.Figure().update_layout(title="Error loading humidity data"),
            go.Figure().update_layout(title="Error loading pressure data"),
            html.Div(error_message, className="text-danger"),
            html.P(["Error refreshing data at: ", html.Strong(current_time)], className="text-danger")
        )

# Run the app
if __name__ == "__main__":
    try:
        app.run_server(debug=True, host='0.0.0.0', port=8050)
    finally:
        # Close the Neo4j connection when the app is closed
        fetcher.close()
