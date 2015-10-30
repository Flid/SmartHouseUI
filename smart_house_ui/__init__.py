from datetime import datetime

from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.button import ButtonBehavior

from .weather_widget import WeatherWidget
from .music_widget import PlayerWidget, MusicProgressBar
from .sidebar import SidebarWidget




class TimeLabel(Label):
    def __init__(self, *args, **kwargs):
        super(TimeLabel, self).__init__(*args, **kwargs)
        Clock.schedule_interval(self._update_time, 1)

    def _update_time(self, *args):
        self.text = datetime.now().strftime('%H:%M')


class ImageButton(ButtonBehavior, Image):
    def on_press(self):
        print(1111111)