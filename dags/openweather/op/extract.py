import typing
import requests

import logging
import json


class OpenWeatherMapExtractor:

    # In practice for security, we'd pass this via Airflow into the init
    # and grab it from env vars
    api_key: str = 'a6e6e5ef01421b25be04a1a6efbd7ead'
    base_url: str = 'http://api.openweathermap.org/data/2.5/weather'


    def __init__(self, api_key: typing.Optional[str] = None):
        if api_key:
            self.api_key = api_key


    def get_current_weather(self, city_id: str, units: str = "metric") -> typing.Optional[str]:
        """
        See https://openweathermap.org/current for API spec.
        """
        response = requests.get(
            self.base_url,
            params = {
                "appid" : self.api_key,
                "id": city_id,
                "units" : units,
            }
        )
        # Kind of limp error handling; just putting here to show that I would.
        if not(response.ok) or ('cod' in response and response['cod'] != '200'):
            # Obviously I'd write this better in practice.
            logging.warning("Oh no, couldn't pull desired payload.")
            return None

        return response.json()

