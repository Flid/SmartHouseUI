import pyximport
pyximport.install()

import os

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.logger import Logger as log

from .screens import (
    MainScreen,
    SettingsScreen,
    IdleScreen,
)
from .camera import MovementTracker


class CustomScreenManager(ScreenManager):
    def __init__(self, *args, **kwargs):
        super(CustomScreenManager, self).__init__(*args, **kwargs)
        self.previous_screen_name = None

    def on_current(self, instance, value):
        self.previous_screen_name = self.current_screen.name if self.current_screen \
                                                             else None
        return super(CustomScreenManager, self).on_current(instance, value)


class SmartHouseApp(App):
    def load_kv(self, *args, **kwargs):
        for f in [
            'styles',
            'debug',
            'panels/base',
            'panels/weather',
            'panels/calendar',
            'screens/main',
            'screens/settings',
            'screens/idle',
        ]:
            Builder.load_file(os.path.join('smart_house_ui/uix', f + '.kv'))

    def build(self):
        self.movement_tracker = MovementTracker()

        self.sm = CustomScreenManager()

        self.main_screen = MainScreen(name='main')
        self.sm.add_widget(self.main_screen)

        self.settings_screen = SettingsScreen(name='settings')
        self.sm.add_widget(self.settings_screen)

        self.idle_screen = IdleScreen(name='idle')
        self.sm.add_widget(self.idle_screen)

        return self.sm

    def on_stop(self):
        log.info('Stopping app...')
