import requests
import json
import pandas as pd 
from datetime import datetime, date, time, timedelta
import pytz

def get_token():
  request_url = "https://api.alertaq.com/api/v4/public/login"
  request_body = {
    "user": "prayagpurohit1@gmail.com",
    "password": "8238709119Pp!",
  }

  response = requests.post(request_url,json=request_body)

  login_response=json.loads(response.text)
  token = login_response['token']
  return token


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


def get_property_id(token):
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
        matching_entries = [entry for entry in properties if entry.get('name') == 'BGO Pen Center']
        print(matching_entries)
        if matching_entries:
            return matching_entries[0]['_id']  # Return the first match
        
        else:
            print(f"Property '{property_name}' not found.")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching property data: {e}")
        return None

def get_sensorlist(token, bgo_id):
    # Get locations by id
    sensors_url = f"https://api.alertaq.com/api/v4/public/sensors?locationID={bgo_id}"
    response = requests.get(sensors_url, headers={"Token": token})
    sensors = json.loads(response.text)
    sensor_list_df = pd.DataFrame(sensors['dataModel'])
    # Filter only "Flowie-O" sensors
    flowie_sensors = sensor_list_df[sensor_list_df['friendlyType'] == "Flowie-O"]

    return flowie_sensors

def get_firstandlastdayofpreviousmonth():
    today = datetime.today()
    first_day_current_month = today.replace(day=1)
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    first_day_previous_month = last_day_previous_month.replace(day=1)
    
    month_start = first_day_previous_month.strftime('%Y-%m-%d')
    month_end = last_day_previous_month.strftime('%Y-%m-%d')
    
    return month_start, month_end

def get_timeseries_data(token, sensor_id, sensorstoquery): 
    rate = "d"
    series = "W"
    month_start, month_end = get_firstandlastdayofpreviousmonth()
    eastern = pytz.timezone('America/New_York')
    start_time_unix = int(eastern.localize(datetime.strptime(month_start, '%Y-%m-%d')).timestamp())
    end_time_unix = int(eastern.localize(datetime.strptime(month_end, '%Y-%m-%d')).timestamp()) 
    
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
    return timeseries_df
    
