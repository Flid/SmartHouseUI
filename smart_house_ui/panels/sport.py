from kivy.clock import Clock
from kivy.uix.widget import Widget
import requests
from requests.exceptions import RequestException


class SportWidget(Widget):
    def __init__(self, *args, **kwargs):
        super(SportWidget, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.update_data, timeout=1)
        Clock.schedule_interval(self.update_data, timeout=10)

    def set_state_error(self):
        self.ids['total_distance'].text = '--/--'

    def update_data(self, instance):
        try:
            response = requests.get(
                'http://127.0.0.1:10100/sensors/endomondo/read',
                timeout=(0.05, 0.1),
            )
        except RequestException as ex:
            self.set_state_error()
            return

        data = response.json()

        if data['status'] != 'ok':
            self.set_state_error()
            return

        data = data['data']
        self.ids['total_distance'].text = 'Total Distance: %s km' % (
            round(data['total_distance'], 2)
        )
