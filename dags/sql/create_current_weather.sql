/*
* DDL for reporting-ready current_weather table 
*/

CREATE TABLE IF NOT EXISTS current_weather (
	city_id INT
	,city_name VARCHAR
	,city_timezone_utc_offset INT
	,city_country VARCHAR
	,weather_base VARCHAR
	,coord_lat FLOAT
	,coord_lon FLOAT
	,weather_group VARCHAR
	,weather_condition VARCHAR
	,temp_c FLOAT
	,temp_f FLOAT
	,feels_like_c FLOAT
	,feels_like_f FLOAT
	,min_temp_c FLOAT
	,min_temp_f FLOAT
	,max_temp_c FLOAT
	,max_temp_f FLOAT
	,humidity FLOAT
	,sea_level_pressure FLOAT
	,grnd_level_pressure FLOAT
	,visibility_mtr FLOAT
	,visibility_mi FLOAT
	,wind_speed_ms FLOAT
	,wind_speed_mph FLOAT
	,wind_gust_ms FLOAT
	,wind_gust_mph FLOAT
	,wind_deg FLOAT
	,cloudiness_pct FLOAT
	,rain_1h_mm FLOAT
	,rain_3h_mm FLOAT
	,snow_1h_mm FLOAT
	,snow_3h_mm FLOAT
	,sunrise_time TIMESTAMPTZ
	,sunset_time TIMESTAMPTZ
	,data_coll_ts_utc TIMESTAMP
	);

