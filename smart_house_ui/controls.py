# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime


from kivy.uix.image import Image
from kivy.uix.button import ButtonBehavior
from kivy.uix.label import Label
from kivy.clock import Clock


class ImageButton(ButtonBehavior, Image):
    def on_press(self):
        pass


class TimeLabel(Label):
    def __init__(self, *args, **kwargs):
        super(TimeLabel, self).__init__(*args, **kwargs)
        Clock.schedule_interval(self._update_time, 1)

    def _update_time(self, *args):
        self.text = datetime.now().strftime('%H:%M')
