import simplesubapi as ssapi
import alertlabapi as atapi
import common_functions as cf
import time
import pandas as pd
from collections import defaultdict

### Main code:
month_start, month_end = cf.get_firstandlastdayofpreviousmonth()
master_df = cf.get_master_df()

### Get data from alert labs
token = atapi.get_token()
property_id = atapi.get_property_id(token, 'BGO Eglinton Town Centre (24)')
if property_id is None:
    raise ValueError("No valid location found. Exiting.")

sensor_list_df = atapi.get_sensorlist(token, property_id)
sensorstoquery = dict(zip(sensor_list_df['_id'], sensor_list_df['name']))  # Map sensor_id to name

for sensor_id in sensorstoquery.keys():
    timeseries_df = atapi.get_timeseries_data(token, sensor_id, sensorstoquery, month_start, month_end)
    time.sleep(1)
    # Merge the timeseries data with the master dataframe
    master_df = cf.mergewithmasterdf(master_df, timeseries_df)

### Get simpleSub data
ss_token = ssapi.get_token()
ss_properties = ssapi.get_property_list(ss_token)
property_name = 'Pen Centre' #### Change property name here
unit_ids = ssapi.get_unit_ids_for_property(ss_properties, property_name)

for unit in unit_ids:
    try:
        timeseries = ssapi.get_timeseries_data(unit, ss_token, month_start=month_start, month_end=month_end)
        time.sleep(0.5)
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
            print(f"Warning: No devices data found for unit {unit_name}. Skipping...")
            continue
        
        if len(timeseries['devices']) > 1:
            mergeddata = defaultdict(float)
            for device in timeseries['devices']:
                for entry in device['daily_usages']:
                    mergeddata[entry['date']] += entry['volume']
                    
            daily_usage = [{'date': k, 'volume': v} for k, v in mergeddata.items()]
        else:
            daily_usage = timeseries["devices"][0].get("daily_usages", [])
            
        if not daily_usage:
            print(f"Warning: No daily usage data for unit {unit}. Skipping...")
            continue

        # Convert to DataFrame
        df = pd.DataFrame(daily_usage)

        # Rename the volume column to the unit name
        df.rename(columns={"volume": unit_name, "date": "Date"}, inplace=True)
        df["Date"] = pd.to_datetime(df["Date"])
        master_df = cf.mergewithmasterdf(master_df, df)
    
    except Exception as e:
        print(f"Failed to get timeseries data for unit {unit}: {e}")
        continue


master_df = cf.add_summary_rows(master_df) 

# Save final CSV
master_df.to_csv(f"csvs/{property_name} monthly report.csv", index=False)