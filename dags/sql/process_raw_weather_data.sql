/*
* Insert selected uninserted columns with some transformation logic applied and more meaningful names
* into the current_weather table 
*/

INSERT INTO current_weather
SELECT city_id
	,city_name
	,city_timezone / 3600 AS city_timezone_utc_offset
	,sys_country AS city_country
	,base AS weather_base
	,coord_lat
	,coord_lon
	,weather_main AS weather_group
	,weather_description AS weather_condition
	,main_temp AS temp_c
	,(9 * main_temp / 5) + 32 AS temp_f
	,main_feels_like AS feels_like_c
	,(9 * main_feels_like / 5) + 32 AS feels_like_f
	,main_temp_min AS min_temp_c
	,(9 * main_temp_min / 5) + 32 AS min_temp_f
	,main_temp_max AS max_temp_c
	,(9 * main_temp_max / 5) + 32 AS max_temp_f
	,cast(main_humidity AS FLOAT) AS humidity
	,coalesce(main_pressure, main_sea_level) AS sea_level_pressure
	,main_grnd_level AS grnd_level_pressure
	,visibility AS visibility_mtr
	,visibility * 0.000621371 AS visibility_mi
	,wind_speed AS wind_speed_ms
	,wind_speed * 2.23694 AS wind_speed_mph
	,wind_gust AS wind_gust_ms
	,wind_gust * 2.23694 AS wind_gust_mph
	,wind_deg
	,clouds_all AS cloudiness_pct
	,coalesce(rain_1h, 0) AS rain_1h_mm
	,coalesce(rain_3h, 0) AS rain_3h_mm
	,coalesce(snow_1h, 0) AS snow_1h_mm
	,coalesce(snow_3h, 0) AS snow_3h_mm
	,to_timestamp(sys_sunrise) AS sunrise_time
	,to_timestamp(sys_sunset) AS sunset_time
	,to_timestamp(data_coll_ts) AT TIME ZONE 'UTC' AS data_coll_ts_utc
FROM raw_current_weather
WHERE data_coll_ts > (
		SELECT max(extract(epoch FROM data_coll_ts_utc))
		FROM current_weather
		);