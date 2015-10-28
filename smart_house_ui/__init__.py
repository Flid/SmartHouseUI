from datetime import datetime
from .weather_widget import WeatherWidget
from .music_widget import PlayerWidget
from .sidebar import SidebarWidget
from kivy.uix.label import Label
from kivy.clock import Clock


class TimeLabel(Label):
    def __init__(self, *args, **kwargs):
        super(TimeLabel, self).__init__(*args, **kwargs)
        Clock.schedule_interval(self._update_time, 1)

    def _update_time(self, *args):
        self.text = datetime.now().strftime('%H:%M')