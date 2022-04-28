/*
* DDL for the raw_current_weather table. 
* The raw JSON response is stored along with the broken down components
*/

CREATE TABLE IF NOT EXISTS raw_current_weather (
	raw_response JSON
	,city_id INT
	,city_name VARCHAR
	,city_timezone INT
	,coord_lat FLOAT
	,coord_lon FLOAT
	,weather_id INT
	,weather_main VARCHAR
	,weather_description VARCHAR
	,weather_icon VARCHAR
	,main_temp FLOAT
	,main_feels_like FLOAT
	,main_temp_min FLOAT
	,main_temp_max FLOAT
	,main_pressure FLOAT
	,main_humidity FLOAT
	,main_sea_level FLOAT
	,main_grnd_level FLOAT
	,visibility INT
	,wind_speed FLOAT
	,wind_gust FLOAT
	,wind_deg FLOAT
	,clouds_all FLOAT
	,rain_1h FLOAT
	,rain_3h FLOAT
	,snow_1h FLOAT
	,snow_3h FLOAT
	,sys_sunrise BIGINT
	,sys_sunset BIGINT
	,data_coll_ts BIGINT
	,sys_country VARCHAR
	,base VARCHAR
	,sys_type INT
	,sys_id INT
	,sys_message FLOAT
	,cod INT
	);