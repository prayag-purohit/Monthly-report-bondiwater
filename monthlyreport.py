import alertlabapi as atapi
import pandas as pd
from datetime import datetime, timedelta

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


token = atapi.get_token()
property_to_query = 'BGO Pen Centre'
bgo_id = atapi.get_property_id(token, 'BGO Pen Centre')
if bgo_id is None:
    raise ValueError("No valid location found. Exiting.")

sensor_list_df = atapi.get_sensorlist(token, bgo_id)
sensorstoquery = dict(zip(sensor_list_df['_id'], sensor_list_df['name']))  # Map sensor_id to name

master_df = get_master_df()
for sensor_id in sensorstoquery.keys():
    timeseries_df = atapi.get_timeseries_data(token, sensor_id, sensorstoquery)
    master_df = mergewithmasterdf(master_df, timeseries_df)



