import alertlabapi as atapi
import simplesubapi as ssapi
import pandas as pd
from datetime import datetime, timedelta
import time


### Common functions 
def get_firstandlastdayofpreviousmonth():
    today = datetime.today()
    first_day_current_month = today.replace(day=1)
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    first_day_previous_month = last_day_previous_month.replace(day=1)
    
    month_start = first_day_previous_month.strftime('%Y-%m-%d')
    month_end = last_day_previous_month.strftime('%Y-%m-%d')
    
    return month_start, month_end


def get_master_df():   
    month_start, month_end = get_firstandlastdayofpreviousmonth()
    master_df = pd.DataFrame()
    master_df['Date'] = pd.date_range(start=month_start, end=month_end)
    return master_df

def mergewithmasterdf(master_df, timeseries_df):
    master_df = master_df.merge(timeseries_df, on='Date', how='left')
    return master_df


### Get data from alert labs
token = atapi.get_token()
bgo_id = atapi.get_property_id(token)
if bgo_id is None:
    raise ValueError("No valid location found. Exiting.")

sensor_list_df = atapi.get_sensorlist(token, bgo_id)
sensorstoquery = dict(zip(sensor_list_df['_id'], sensor_list_df['name']))  # Map sensor_id to name

master_df = get_master_df()
for sensor_id in sensorstoquery.keys():
    timeseries_df = atapi.get_timeseries_data(token, sensor_id, sensorstoquery)
    time.sleep(1)
    # Merge the timeseries data with the master dataframe
    master_df = mergewithmasterdf(master_df, timeseries_df)

### Get simpleSub data
ss_token = ssapi.get_token()
ss_properties = ssapi.get_property_list(ss_token)
property_name = 'Pen Centre' #### Change property name here
unit_ids = ssapi.get_unit_ids_for_property(ss_properties, property_name)

for unit in unit_ids:
    try:
        timeseries = ssapi.get_timeseries_data(unit, ss_token)
        time.sleep(1)
        if timeseries is None:
            print(f"Warning: No timeseries data returned for unit {unit}. Skipping...")
            continue  # Skip to the next unit

        if "unit_name" not in timeseries:
            print(f"Warning: 'unit_name' missing in response for unit {unit}. Skipping...")
            unit_name = f"Unit {unit}"
        else:
            unit_name = timeseries["unit_name"]
        

        # Extract daily usage data safely
        if "devices" not in timeseries or not timeseries["devices"]:
            print(f"Warning: No devices data found for unit {unit}. Skipping...")
            continue
        
        daily_usage = timeseries["devices"][0].get("daily_usages", [])
        if not daily_usage:
            print(f"Warning: No daily usage data for unit {unit}. Skipping...")
            continue

        # Convert to DataFrame
        df = pd.DataFrame(daily_usage)

        # Rename the volume column to the unit name
        df.rename(columns={"volume": unit_name, "date": "Date"}, inplace=True)
        df["Date"] = pd.to_datetime(df["Date"])
        master_df = mergewithmasterdf(master_df, df)
    
    except Exception as e:
        print(f"Failed to get timeseries data for unit {unit}: {e}")
        continue


# Save final CSV
master_df.to_csv(f"csvs/{property_name} monthly report.csv", index=False)