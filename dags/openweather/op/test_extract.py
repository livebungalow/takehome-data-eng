# I installed testing lib as a dev dependency (locally), I wouldn't install it in the container.
# Might write this in a different style depending on what team uses.

import pytest
from .extract import OpenWeatherMapExtractor


class TestOpenWeatherMapExtractor:

    @classmethod
    def setup_class(cls):
        cls.extractor = OpenWeatherMapExtractor()

    def test_get_current_weather_ok(self):
        """
        Verify GET on the API returns a usable payload if status OK/200.

        Depending on how flaky we think source is, we could write more
        stringest tests here. Right now I'm just checking it returns a payload
        with the lat and lon matching what I passed as args.
        """
        payload = self.extractor.get_current_weather(city_id=5992996) # KW ID

        assert 'id' in payload
        assert 'coord' in payload
        assert 'lat' in payload['coord']
        assert 'lon' in payload['coord']

