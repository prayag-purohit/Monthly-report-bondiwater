import alertlabapi as atapi
import monthlyreport as mr

token = atapi.get_token()
property_to_query = 'BGO Pen Centre'
bgo_id = atapi.get_property_id(token, 'BGO Pen Centre')
if bgo_id is None:
    raise ValueError("No valid location found. Exiting.")

sensor_list_df = atapi.get_sensorlist(token, bgo_id)
sensorstoquery = dict(zip(sensor_list_df['_id'], sensor_list_df['name']))  # Map sensor_id to name

master_df = mr.get_master_df()
for sensor_id in sensorstoquery.keys():
    timeseries_df = atapi.get_timeseries_data(token, sensor_id, sensorstoquery)
    master_df = mr.mergewithmasterdf(master_df, timeseries_df)

master_df.head()