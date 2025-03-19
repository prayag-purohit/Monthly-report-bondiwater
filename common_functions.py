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

    # Apply padding
    padded_start = first_day_previous_month - timedelta(days=1)  # Month start - 1 day
    padded_end = last_day_previous_month + timedelta(days=1)  # Month end + 1 day

    month_start = padded_start.strftime('%Y-%m-%d')
    month_end = padded_end.strftime('%Y-%m-%d')

    return month_start, month_end

def get_master_df():   
    month_start, month_end = get_firstandlastdayofpreviousmonth()
    master_df = pd.DataFrame()
    master_df['Date'] = pd.date_range(start=month_start, end=month_end)
    return master_df

def mergewithmasterdf(master_df, timeseries_df, unit='liters'):
    """
    Merges the timeseries DataFrame with the master DataFrame.
    Converts the volume data to liters if the unit is 'gallons'.
    
    Parameters:
        master_df (pd.DataFrame): The master DataFrame.
        timeseries_df (pd.DataFrame): The timeseries DataFrame to merge.
        unit (str): The unit of the volume data ('liters' or 'gallons').
        
    Returns:
        pd.DataFrame: The updated master DataFrame.
    """
    if unit == 'gallons':
        volume_col = [col for col in timeseries_df.columns if col != 'Date'][0]
        timeseries_df[volume_col] = timeseries_df[volume_col] * 3.78541
    master_df = master_df.merge(timeseries_df, on='Date', how='left')
    return master_df


def add_summary_rows(master_df, cost_per_m3=4.8401):
    """
    Adds summary rows to the given DataFrame, including total liters, m³, total cost, 
    and average daily usage. The summary rows are appended at the bottom of the DataFrame.
    
    Parameters:
        master_df (pd.DataFrame): The input DataFrame with a 'Date' column and numeric columns.
        cost_per_m3 (float): The cost per cubic meter for calculating total cost.
        
    Returns:
        pd.DataFrame: The updated DataFrame with summary rows added.
    """
    # Exclude the 'Date' column for calculations
    master_df = master_df.iloc[1:-1] # correct
    master_df['Date'] = pd.to_datetime(master_df['Date'])
    master_df['Date'] = master_df['Date'].dt.date
    numeric_df = master_df.iloc[:, 1:]
    
    # Calculate the required metrics
    total_liters = numeric_df.sum(axis=0)           # Sum of each column
    total_m3 = total_liters / 1000                 # Convert liters to cubic meters
    total_cost = total_m3 * cost_per_m3            # Calculate total cost
    average_daily_usage = numeric_df.mean(axis=0)  # Average daily usage for each column
    
    # Create a summary DataFrame
    summary_df = pd.DataFrame({
        'Date': ['Total Liters', 'm³', 'Total Cost', 'Average Daily Usage'],
        **{col: [total_liters[col], total_m3[col], total_cost[col], average_daily_usage[col]] for col in numeric_df.columns}
    })
    
    # Concatenate the summary rows with the original DataFrame
    updated_df = pd.concat([master_df, summary_df], ignore_index=True)
    
    return updated_df

"""
### Main code:
month_start, month_end = get_firstandlastdayofpreviousmonth()
master_df = get_master_df()

### Get data from alert labs
token = atapi.get_token()
bgo_id = atapi.get_property_id(token)
if bgo_id is None:
    raise ValueError("No valid location found. Exiting.")

sensor_list_df = atapi.get_sensorlist(token, bgo_id)
sensorstoquery = dict(zip(sensor_list_df['_id'], sensor_list_df['name']))  # Map sensor_id to name

for sensor_id in sensorstoquery.keys():
    timeseries_df = atapi.get_timeseries_data(token, sensor_id, sensorstoquery, month_start, month_end)
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
        timeseries = ssapi.get_timeseries_data(unit, ss_token, month_start=month_start, month_end=month_end)
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


master_df = add_summary_rows(master_df) 

# Save final CSV
master_df.to_csv(f"csvs/{property_name} monthly report.csv", index=False)
"""