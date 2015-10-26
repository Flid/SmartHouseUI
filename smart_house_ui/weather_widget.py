from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
import requests
from requests.exceptions import RequestException


AVERAGE_PRESSURE = 1013.25  # bar


class WeatherWidget(Widget):
    temp_out = ObjectProperty(None)
    temp_in = ObjectProperty(None)
    humidity_out = ObjectProperty(None)
    humidity_in = ObjectProperty(None)
    pressure = ObjectProperty(None)
    rain_forecast = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(WeatherWidget, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.update_weather, timeout=1)
        Clock.schedule_interval(self.update_weather, timeout=10)

    def set_state_error(self):
        self.temp_out.text = '--'
        self.humidity_out.text = '--'
        self.pressure.text = 'Pressure: +0.0%'
        self.rain_forecast.text = 'Expecting: -------- (0.00)'

    def set_state_ok(self):
        pass

    def update_weather(self, instance):
        try:
            response = requests.get(
                'http://127.0.0.1:10100/sensors/weather/read',
                timeout=(0.05, 0.1),
            )
        except RequestException as ex:
            self.set_state_error()
            return

        data = response.json()

        if data['status'] != 'ok':
            self.set_state_error()
            return

        self.temp_out.text = str(round(data['data']['temperature']))
        self.humidity_out.text = str(round(data['data']['humidity']))

        delta_pressure = (data['data']['pressure'] - AVERAGE_PRESSURE) / data['data']['pressure'] * 100
        self.pressure.text = 'Pressure: %s%0.1f %%' % (
            '+' if delta_pressure > 0 else '',
            delta_pressure,
        )

        rain_forecast_rating = data['data']['rain_forecast_rating']
        if rain_forecast_rating > 1.0:
            text = 'heavy rain'
        elif rain_forecast_rating > 0.5:
            text = 'rain'
        elif rain_forecast_rating > 0.2:
            text = 'drizzle'
        else:
            text = 'clear'

        self.rain_forecast.text = 'Expected: %s (%0.2f)' % (text, rain_forecast_rating)
        self.set_state_ok()

