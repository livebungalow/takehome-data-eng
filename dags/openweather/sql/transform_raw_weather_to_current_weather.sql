SET TIME ZONE 'UTC';

WITH

transform_step AS (

    SELECT

        city_id
        , raw_data->>'name' AS city_name
        , raw_data->'sys'->>'country' AS country

        , TO_TIMESTAMP(unix_time_seconds) AS utc_recorded_at
        , tz_offset_seconds / 3600.0 * INTERVAL '1 hour' AS tz_offset_hours

        , (raw_data->'coord'->>'lat')::NUMERIC(11, 8) AS lat
        , (raw_data->'coord'->>'lon')::NUMERIC(11, 8) AS lon

        , (raw_data->'weather'->0->>'main') AS weather_type
        , (raw_data->'weather'->0->>'description') AS weather_desc

        -- This could be set via environment variable too,
        -- or airflow config. Hardcoding for POC here.
        , 'Metric' AS measure_units

        , (raw_data->>'visibility')::FLOAT AS visibility_pct
        , (raw_data->'clouds'->>'all')::FLOAT AS cloud_pct

        , (raw_data->'main'->>'temp')::FLOAT AS temp_deg
        , (raw_data->'main'->>'humidity')::FLOAT AS humidity_pct
        , (raw_data->'main'->>'pressure')::FLOAT AS pressure
        , (raw_data->'main'->>'temp_min')::FLOAT AS temp_min
        , (raw_data->'main'->>'temp_max')::FLOAT AS temp_max
        , (raw_data->'main'->>'feels_like')::FLOAT AS feels_like

        , (raw_data->'wind'->>'deg')::FLOAT AS wind_deg
        , (raw_data->'wind'->>'gust')::FLOAT AS wind_gust
        , (raw_data->'wind'->>'speed')::FLOAT AS wind_speed

    FROM raw_current_weather

)

INSERT INTO current_weather

SELECT *
FROM transform_step
ORDER BY utc_recorded_at, city_id

ON CONFLICT (city_id, utc_recorded_at) DO UPDATE SET

    city_name = EXCLUDED.city_name

    , country = EXCLUDED.country
    , tz_offset_hours = EXCLUDED.tz_offset_hours

    , lat = EXCLUDED.lat
    , lon = EXCLUDED.lon

    , weather_type = EXCLUDED.weather_type
    , weather_desc = EXCLUDED.weather_desc

    , measure_units = EXCLUDED.measure_units

    , visibility_pct = EXCLUDED.visibility_pct
    , cloud_pct = EXCLUDED.cloud_pct

    , temp_deg = EXCLUDED.temp_deg
    , humidity_pct = EXCLUDED.humidity_pct
    , pressure = EXCLUDED.pressure
    , temp_min = EXCLUDED.temp_min
    , temp_max = EXCLUDED.temp_max
    , feels_like = EXCLUDED.feels_like

    , wind_deg = EXCLUDED.wind_deg
    , wind_gust = EXCLUDED.wind_gust
    , wind_speed = EXCLUDED.wind_speed

