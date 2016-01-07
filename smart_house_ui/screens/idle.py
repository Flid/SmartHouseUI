# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, FadeTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.logger import Logger as log

SCREENSAVER_TIMEOUT = 60


class ScreensaverDrawingArea(FloatLayout):
    def __init__(self, *args, **kwargs):
        super(ScreensaverDrawingArea, self).__init__(*args, **kwargs)
        self._tempr_label = None

    def restart(self):
        log.debug('Starting screensaver...')
        Clock.schedule_interval(self._update, 1)
        self._update()

    def _update(self, *args):

        if not self._tempr_label:
            panels = App.get_running_app().main_screen.ids['panels']
            self._tempr_label = panels.ids['weather'].ids['temp_out']

        temp = self._tempr_label.text
        if temp and temp.isdigit():
            temp = 'Temperature: %s [sup]o[/sup]C' % temp
        else:
            temp = 'Temperature Unknown =('

        self.ids['temperature_label'].text = temp

        self.ids['time_label'].text = datetime.now().strftime('%H:%M')

    def stop(self):
        log.debug('Stopping screensaver...')
        Clock.unschedule(self._update)


def reschedule_screensaver():
    Clock.unschedule(_run_screensaver)
    Clock.schedule_once(_run_screensaver, SCREENSAVER_TIMEOUT)


def _run_screensaver(*args):
    manager = IdleScreen._instance.manager
    manager.transition = FadeTransition()
    manager.current = 'idle'


class IdleScreen(Screen):
    _instance = None

    def __init__(self, *args, **kwargs):
        super(IdleScreen, self).__init__(*args, **kwargs)
        IdleScreen._instance = self
        reschedule_screensaver()

    def on_pre_enter(self, *args):
        self.ids['draw_area'].restart()

    def on_leave(self, *args):
        self.ids['draw_area'].stop()

    def on_touch_down(self, touch):
        self.manager.transition = FadeTransition()
        self.manager.current = self.manager.previous_screen_name
        return True
