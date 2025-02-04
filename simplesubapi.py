import requests
import json


def get_token():
    """
    Function to retrieve the authentication token from the API.

    Parameters:
        api_url (str): The authentication endpoint URL.
        client_id (str): Client ID for authentication.
        client_secret (str): Client Secret for authentication.

    Returns:
        str: The authentication token.
    """
    header = {
        "Content-Type": "application/x-amz-json-1.1",
        "X-Amz-Target": "AWSCognitoIdentityProviderService.InitiateAuth"
    }

    payload = {
        "AuthFlow": "USER_PASSWORD_AUTH",
        "AuthParameters": {
            "USERNAME": "alerts.watercontrols@gmail.com",
            "PASSWORD": "theH20m@sters"
        },
        "ClientId": "3jkng9ho3h3l8a93h5bfg4oml2"
    }

    url = "https://cognito-idp.us-east-2.amazonaws.com/"

    response = requests.post(url, headers=header, data=json.dumps(payload))
    response_data = response.json()
    return response_data["AuthenticationResult"]["IdToken"]

def get_property_list(token):
    """
    Function to retrieve the list of properties from the API.

    Parameters:
        token (str): The authentication token.

    Returns:
        list: A list of property names.
    """
    header = {
        "Authorization": token
    }

    url = "https://api.alertlab.com/properties"

    response = requests.get(url, headers=header)
    locations = response.json()
    return locations

def get_firstandlastdayofpreviousmonth():
    today = datetime.today()
    first_day_current_month = today.replace(day=1)
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    first_day_previous_month = last_day_previous_month.replace(day=1)
    
    month_start = first_day_previous_month.strftime('%Y-%m-%d')
    month_end = last_day_previous_month.strftime('%Y-%m-%d')
    
    return month_start, month_end

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

def get_timeseries_data(unit_id, auth_token):

    month_start, month_end = get_firstandlastdayofpreviousmonth()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    api_url = f"https://api.prod.simplesubwater.com/v1/unit/{unit_id}/usage?end_date={month_end}&timezone_key=America/New_York&start_date={month_start}"

    response = requests.get(api_url, headers=headers)

    timeseries = response.json()
    return timeseries

