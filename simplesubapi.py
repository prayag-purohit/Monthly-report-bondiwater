import requests
import json
import time
from datetime import datetime, date, timedelta
import os

def get_token():
    """Get authentication token for SimpleSub API."""
    header = {
        "Content-Type": "application/x-amz-json-1.1",
        "X-Amz-Target": "AWSCognitoIdentityProviderService.InitiateAuth"
    }

    payload = {
        "AuthFlow": "USER_PASSWORD_AUTH",
        "AuthParameters": {
            "USERNAME": os.getenv("SIMPLESUB_USERNAME"),
            "PASSWORD": os.getenv("SIMPLESUB_PASSWORD")
        },
        "ClientId": os.getenv("SIMPLESUB_CLIENT_ID")
    }

    url = "https://cognito-idp.us-east-2.amazonaws.com/"

    response = requests.post(url, headers=header, json=payload)

    if response.status_code == 200:
        try:
            return response.json()["AuthenticationResult"]["IdToken"]
        except KeyError:
            print(f"Unexpected response: {response.json()}")
            return None
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def get_property_list(token):
    """
    Function to retrieve the list of properties from the API.

    Parameters:
        token (str): The authentication token.

    Returns:
        list: A list of property names.
    """
    header = {
        "Authorization": token,
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache"
    }

    url = "https://api.prod.simplesubwater.com/v1/structure?"

    response = requests.get(url, headers=header)
    locations = response.json()
    return locations

def get_unit_ids_for_property(data, property_name):
    unit_ids = []
    
    # Iterate through each property
    for property_data in data:
        if property_data['name'] == property_name:
            # Iterate through each unit in the property
            for unit in property_data['units']:
                unit_ids.append(unit['id'])  # Collect the unit ID
            break  # Exit the loop once the property is found
    
    return unit_ids

def get_timeseries_data(unit_id, auth_token, month_start, month_end):

    #month_start, month_end = get_firstandlastdayofpreviousmonth()
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    api_url = f"https://api.prod.simplesubwater.com/v1/unit/{unit_id}/usage?end_date={month_end}&timezone_key=America/New_York&start_date={month_start}"
    #time.sleep(1)
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        return None
    timeseries = response.json()
    return timeseries

