import sys

# Define lat and lon coordinates and the OpenWeather API key
#
# Note: 1. Ideally, these would either be a list of coordinates in a config file,
# or they'd be passed as Variables in Airflow.
# 2. The API key could be stored in AWS Secrets Manager (or similar service),
# and be retrieved from there when needed.
lat = 37.7987
lon = -122.46608
owm_api_key = "***REMOVED***"

# Check if the lat/lon coordinates are in a valid range.
# Latitudes have to be between -90 and 90, while longitudes have to be between -180 and 180.
# As such, we can pass illegal coordinates to the API call and it'll return an error, but that'd be a waste of an API call :)
def coord_check(lat, lon):

    if (lat > 90 or lat < -90) or (lon > 180 or lon < -180):
        sys.exit(
            "Invalid lat/lon coordinates! Please check the values and try again. Exiting..."
        )

    else:
        return lat, lon


# Return DB Engine to write data into
def get_db_engine():

    import os

    import psycopg2
    import sqlalchemy as sa

    return sa.create_engine(
        "postgresql+psycopg2://airflow:airflow@postgres/airflow",
        isolation_level="SERIALIZABLE",
    )


# Use pandas to process the JSON response and store it in the raw_current_weather table
def process_record(response):

    import pandas as pd

    # Use json_normalize to naturally explode the elements of the JSON object
    # record_path further explodes the array elements, and meta helps get all columns together in one dataframe
    # sep is the separator used when the column names are derived from the JSON keys. Default is period (.), but we
    # override it with underscore (_) to align with the table DDL.
    # We also use the errors='ignore' parameter because the JSON body may not contain all possible elements, and so it fills NaNs wherever an element is not found
    # e.g. if it is not snowing in San Francisco, we'd never see it show up in the JSON response, but if we then
    # switched to Houghton, MI, for example, where it snows a lot, it'd show up then, and if we don't handle this schema change, so to speak, it'd break our code.
    wthr_df = pd.json_normalize(
        response.json(),
        record_path="weather",
        record_prefix="weather_",
        meta=[
            "id",
            "name",
            "timezone",
            ["coord", "lat"],
            ["coord", "lon"],
            ["main", "temp"],
            ["main", "feels_like"],
            ["main", "temp_min"],
            ["main", "temp_max"],
            ["main", "pressure"],
            ["main", "humidity"],
            ["main", "sea_level"],
            ["main", "grnd_level"],
            "visibility",
            ["wind", "speed"],
            ["wind", "gust"],
            ["wind", "deg"],
            ["clouds", "all"],
            ["rain", "1h"],
            ["rain", "3h"],
            ["snow", "1h"],
            ["snow", "3h"],
            ["sys", "sunrise"],
            ["sys", "sunset"],
            "dt",
            ["sys", "country"],
            "base",
            ["sys", "type"],
            ["sys", "id"],
            ["sys", "message"],
            "cod",
        ],
        sep="_",
        errors="ignore",
    )

    wthr_df = wthr_df.rename(
        columns={
            "id": "city_id",
            "name": "city_name",
            "timezone": "city_timezone",
            "dt": "data_coll_ts",
        }
    )

    col_ord = [
        "city_id",
        "city_name",
        "city_timezone",
        "coord_lat",
        "coord_lon",
        "weather_id",
        "weather_main",
        "weather_description",
        "weather_icon",
        "main_temp",
        "main_feels_like",
        "main_temp_min",
        "main_temp_max",
        "main_pressure",
        "main_humidity",
        "main_sea_level",
        "main_grnd_level",
        "visibility",
        "wind_speed",
        "wind_gust",
        "wind_deg",
        "clouds_all",
        "rain_1h",
        "rain_3h",
        "snow_1h",
        "snow_3h",
        "sys_sunrise",
        "sys_sunset",
        "data_coll_ts",
        "sys_country",
        "base",
        "sys_type",
        "sys_id",
        "sys_message",
        "cod",
    ]

    wthr_df = wthr_df[col_ord]

    wthr_df.insert(0, "raw_response", response.text)

    conn = get_db_engine().connect()

    with conn:
        # We'd like to always append to this table
        wthr_df.to_sql("raw_current_weather", con=conn, if_exists="append", index=False)

    conn.close()


# This function performs the API call and based on the response code, either exits, or processes the response
def get_weather(lat, lon, owm_api_key):

    import requests

    # Check lat/lon values
    lat, lon = coord_check(lat, lon)

    # Construct the API call URL
    owm_req_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&mode=json&units=metric&lang=en&appid={owm_api_key}"
    response = requests.get(owm_req_url)

    # Get status code to handle it gracefully - somewhat gracefully, at least :)
    status_code = response.status_code

    # Check for each of the codes - taken from the API Errors section found at https://openweathermap.org/faq
    if status_code == 401:
        sys.exit("API Key error! Please check your API Key and try again. Exiting...")

    if status_code == 401:
        sys.exit(
            "City not found, or request URL is malformed. Please check lat/lon coordinates and request URL and try again. Exiting..."
        )

    if status_code == 429:
        sys.exit(
            "Exceeded 60 calls per minute. Please slow down request rate or upgrade subscription plan and try again. Exiting..."
        )

    if (
        status_code == 500
        or status_code == 502
        or status_code == 503
        or status_code == 504
    ):
        sys.exit(
            "Unknown error! Please contact OpenWeather for further assistance. Exiting..."
        )

    # If the status code is 200 (OK), process the record
    if status_code == 200:
        process_record(response)


def main():
    get_weather(lat, lon, owm_api_key)


if __name__ == "__main__":
    main()
