import requests
import json
import pandas as pd 
from datetime import datetime, date, timedelta
import pytz
import os
import time

def get_token():
    """Get authentication token for AlertLab API."""
    request_url = "https://api.alertaq.com/api/v4/public/login"
    request_body = {
        "user": os.getenv("ALERTLAB_USER"),
        "password": os.getenv("ALERTLAB_PASSWORD"),
    }

    response = requests.post(request_url, json=request_body)

    if response.status_code == 200:
        return response.json().get("token")
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


def get_property_name_list(token):
    """
    Fetches the list of property names from the AlertAQ API, saves them into a text file,
    and returns the list of names.

    Parameters:
        token (str): The API token for authentication.

    Returns:
        list: A list of property names.
    """
    # API endpoint
    url = "https://api.alertaq.com/api/v4/public/locations"
    
    # Request headers
    headers = {"Token": token}
    
    try:
        # Fetch the response
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse the response JSON
        locations = response.json()
        
        # Extract the list of property names
        names = [location['name'] for location in locations['dataModel']]
        
        # Save the names into a text file
        with open("alert_lab_property_list.txt", "w") as file:
            for name in names:
                file.write(name + "\n")
        
        return names
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching property names: {e}")
        return []


def get_property_id(token, property_name):
    """
    Fetches the property ID for a given property name from the AlertAQ API.

    Parameters:
        token (str): The API token for authentication.
        property_name (str): The name of the property to search for.

    Returns:
        str: The property ID if found, else None.
    """
    url = "https://api.alertaq.com/api/v4/public/locations"
    
    try:
        response = requests.get(url, headers={"Token": token})
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        locations = response.json()
        properties = locations.get('dataModel', [])  # Safely access 'dataModel'
        
        # Find the matching property
        matching_entries = [entry for entry in properties if entry.get('name') == property_name]
        #print(matching_entries)
        if matching_entries:
            return matching_entries[0]['_id']  # Return the first match
        
        else:
            print(f"Property not found.")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching property data: {e}")
        return None

def get_sensorlist(token, property_id):
    # Get locations by id
    sensors_url = f"https://api.alertaq.com/api/v4/public/sensors?locationID={property_id}"
    response = requests.get(sensors_url, headers={"Token": token})
    sensors = json.loads(response.text)
    sensor_list_df = pd.DataFrame(sensors['dataModel'])
    # Filter only "Flowie-O" sensors, and Flowie sensors
    flowie_sensors = sensor_list_df[(sensor_list_df['friendlyType'] == "Flowie-O") | (sensor_list_df['friendlyType'] == "Flowie")]

    return flowie_sensors


def get_timeseries_data(token, sensor_id, sensorstoquery, month_start, month_end): 
    rate = "d"
    series = "W"
    #month_start, month_end = get_firstandlastdayofpreviousmonth()
    # Convert to datetime objects and add timezone
    eastern = pytz.timezone('America/New_York')
    start_dt = eastern.localize(datetime.strptime(month_start, "%Y-%m-%d"))
    end_dt = eastern.localize(datetime.strptime(month_end, "%Y-%m-%d"))
    
    start_time_unix = int(start_dt.timestamp())
    end_time_unix = int(end_dt.timestamp())
        
    timeseriesurl = f"https://api.alertaq.com/api/v4/public/timeseries?from={start_time_unix}&to={end_time_unix}&rate={rate}&series={series}&sensorID={sensor_id}"

    response = requests.get(timeseriesurl, headers={"Token": token})
    timeseries = json.loads(response.text)
    timeseries['dataModel'] = {
        sensorstoquery.get(sensor_id, sensor_id): data for sensor_id, data in timeseries['dataModel'].items()
    }
    sensor_id = list(timeseries['dataModel'].keys())[0]  # Assuming only one sensor ID
    # Get the corresponding sensor name or keep the ID if not found
    sensor_name = sensorstoquery.get(sensor_id, sensor_id)
    # Create the DataFrame
    timeseries_df = pd.DataFrame(timeseries['dataModel'][sensor_id], columns=['Date', f'{sensor_name}'])

    # Convert 'Date' column to datetime
    timeseries_df['Date'] = pd.to_datetime(timeseries_df['Date'], unit='ms')
    # Identify the last column dynamically
    last_column = timeseries_df.columns[-1]

# Convert the last column to float and round to two decimals
    timeseries_df[last_column] = timeseries_df[last_column].astype(float).round(2)

    return timeseries_df
    
