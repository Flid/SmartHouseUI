"""
Weather service.
Retrieves the current weather and weather forecasts from  openweathermap.org
API once in a while and caches it to be easily retrieved later.
We separately calculate "rain forecast rating", like some measure of umbrella
necessity today... It's England, I need it!
"""
import time

import requests
from smart_house_ui import config
from .base import ServiceBase
from threading import RLock
from kivy.logger import Logger as log
from typing import NamedTuple, Optional

# There are lots of possible rain types, let's get value to each,
# assuming that 1 is a usual rain
LIGHT_RAIN = 0.2
RAIN = 1.0
HEAVY_RAIN = 2.0
DRIZZLE = 0.7

KELVIN_TO_CELSIUS_CONSTANT = 273.15
FORECAST_URL = 'http://api.openweathermap.org/data/2.5/forecast'
WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather'
WEATHER_ICON_URL_TEMPLATE = 'http://openweathermap.org/img/w/{}.png'


class WeatherData(NamedTuple):
    humidity: float
    temperature: float
    pressure: float
    icon_url: str
    rain_forecast_rating: float


WEATHER_CODE_RAIN_WEIGHTS = {
    200: LIGHT_RAIN,            # thunderstorm with light rain
    201: RAIN,                  # thunderstorm with rain
    202: HEAVY_RAIN,            # thunderstorm with heavy rain
    230: LIGHT_RAIN * DRIZZLE,  # thunderstorm with light drizzle
    231: RAIN * DRIZZLE,        # thunderstorm with drizzle
    232: HEAVY_RAIN * DRIZZLE,  # thunderstorm with heavy drizzle
    300: LIGHT_RAIN * DRIZZLE,  # light intensity drizzle
    301: RAIN * DRIZZLE,        # drizzle
    302: HEAVY_RAIN * DRIZZLE,  # heavy intensity drizzle
    310: LIGHT_RAIN,            # light intensity drizzle rain
    311: RAIN,                  # drizzle rain
    312: HEAVY_RAIN,            # heavy intensity drizzle rain
    313: RAIN,                  # shower rain and drizzle
    314: HEAVY_RAIN,            # heavy shower rain and drizzle
    321: RAIN * DRIZZLE,        # shower drizzle
    500: LIGHT_RAIN,            # light rain
    501: RAIN,                  # moderate rain
    502: HEAVY_RAIN,            # heavy intensity rain
    503: HEAVY_RAIN * 2,        # very heavy rain
    504: HEAVY_RAIN * 4,        # extreme rain
    511: HEAVY_RAIN * 4,        # freezing rain
    520: LIGHT_RAIN,            # light intensity shower rain
    521: RAIN,                  # shower rain
    522: HEAVY_RAIN,            # heavy intensity shower rain
    531: HEAVY_RAIN,            # ragged shower rain
    611: RAIN,                  # sleet
    612: RAIN,                  # shower sleet
    615: LIGHT_RAIN,            # light rain and snow
    616: RAIN,                  # rain and snow
    620: LIGHT_RAIN,            # light shower snow
}  # noqa


class WeatherService(ServiceBase):
    # Forecast has data for every 3 hours, so let'sconsider only 12 hours
    RAIN_ITEMS_TO_MEASURE = 4
    UPDATE_EVERY = 60  # sec
    RESET_AFTER_N_FAILURES = 5

    def __init__(self):
        super().__init__()
        self._data_lock = RLock()
        self._data = None
        self.failures_count = 0

    def get_rain_forecast(self):
        log.info('Getting the weather forecast')
        response = requests.get(
            FORECAST_URL,
            params={
                'id': config.CITY_ID_LONDON,
                'appid': config.WEATHER_API_KEY,
            },
        )
        response.raise_for_status()

        items = response.json()['list']
        items = items[:self.RAIN_ITEMS_TO_MEASURE]

        sum = 0
        for item in items:
            weather_id = item['weather'][0]['id']
            sum += WEATHER_CODE_RAIN_WEIGHTS.get(weather_id, 0)

        return float(sum) / self.RAIN_ITEMS_TO_MEASURE

    def _get_weather(self) -> WeatherData:
        log.info('Getting the current weather')
        response = requests.get(
            WEATHER_URL,
            params={
                'id': config.CITY_ID_LONDON,
                'appid': config.WEATHER_API_KEY,
            },
        )
        response.raise_for_status()
        data = response.json()

        return WeatherData(
            humidity=data['main']['humidity'],
            temperature=data['main']['temp'] - KELVIN_TO_CELSIUS_CONSTANT,
            pressure=data['main']['pressure'],
            icon_url=WEATHER_ICON_URL_TEMPLATE.format(
                data["weather"][0]["icon"],
            ),
            rain_forecast_rating=self.get_rain_forecast(),
        )

    def _worker(self):
        log.info('Starting weather service...')
        while True:
            try:
                weather_data = self._get_weather()

                with self._data_lock:
                    self._data = weather_data

                log.info('Weather has been successfully updated')
            except Exception:
                log.exception('Error processing weather')
                self.failures_count += 1

                if self.failures_count >= self.RESET_AFTER_N_FAILURES:
                    with self._data_lock:
                        self._data = None

            finally:
                time.sleep(self.UPDATE_EVERY)

    @property
    def data(self) -> Optional[WeatherData]:
        with self._data_lock:
            return self._data
