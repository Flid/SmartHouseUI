# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from kivy.clock import Clock
from kivy.logger import Logger as log
from kivy.uix.screenmanager import FadeTransition, Screen

from .screensavers import GameOfLifeArea

SCREENSAVER_TIMEOUT = 30


def reschedule_screensaver():
    Clock.unschedule(_run_screensaver)
    Clock.schedule_once(_run_screensaver, SCREENSAVER_TIMEOUT)


def _run_screensaver(*args):
    manager = IdleScreen._instance.manager
    manager.transition = FadeTransition()
    manager.current = "idle"


class IdleScreen(Screen):
    _instance = None

    def __init__(self, *args, **kwargs):
        super(IdleScreen, self).__init__(*args, **kwargs)
        IdleScreen._instance = self
        reschedule_screensaver()

        self._initialized = False

    def _init(self):
        self.area = GameOfLifeArea()
        self.area.size = self.size
        print(self.size, self.pos)
        self.area.pos = self.pos
        self.add_widget(self.area)
        self.ids["draw_area"] = self.area

    def on_pre_enter(self, *args):
        log.debug("Starting screensaver...")
        if not self._initialized:
            self._init()
            self._initialized = True

        self.ids["draw_area"].restart()

    def on_leave(self, *args):
        log.debug("Stopping screensaver...")
        self.ids["draw_area"].stop()

    def on_touch_down(self, touch):
        self.manager.transition = FadeTransition()
        self.manager.current = self.manager.previous_screen_name
        return True
