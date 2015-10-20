from kivy.loader import Loader
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.relativelayout import RelativeLayout
import requests
from requests.exceptions import RequestException


AVERAGE_PRESSURE = 1013.25  # bar


class WeatherWidget(RelativeLayout):
    def __init__(self, *args, **kwargs):
        super(WeatherWidget, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.update_weather, timeout=1)
        Clock.schedule_interval(self.update_weather, timeout=10)

    def set_state_error(self):
        pass # self.status_light.source = self.LIGHT_OFFLINE_IMG

    def set_state_ok(self):
        pass # self.status_light.source = self.LIGHT_ONLINE_IMG

    def update_weather(self, instance):
        return
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

        self.temperature_label.text = str(round(data['data']['temperature'])) + ' \u00b0C'
        self.humidity_label.text = str(round(data['data']['humidity'])) + ' %'

        delta_pressure = (data['data']['pressure'] - AVERAGE_PRESSURE) / data['data']['pressure'] * 100
        self.pressure_label.text = '%s%0.2f %%' % (
            '+' if delta_pressure > 0 else '-',
            delta_pressure,
        )

        rain_forecast_rating = data['data']['rain_forecast_rating']
        if rain_forecast_rating > 2.0:
            text = 'Take an umbrella!!!'
            color = 1, 0.3, 0.3, 1
        elif rain_forecast_rating > 1.0:
            text = 'High rain chance'
            color = 1, 0.3, 0.3, 1
        elif rain_forecast_rating > 0.5:
            text = 'A small rain is expected'
            color = 1, 0.6, 0.4, 1
        elif rain_forecast_rating > 0.2:
            text = 'A chance of small rain'
            color = 1, 0.8, 0.6, 1
        else:
            text = 'Weather will be good'
            color = 0.2, 0.8, 0.2, 1

        self.rain_rating.text = '%0.2f' % rain_forecast_rating

        self.recommendation_label.text = text
        self.recommendation_label.color = color

        self.icon.source = data['data']['icon_url']
        self.icon.opacity = 1

        self.set_state_ok()

