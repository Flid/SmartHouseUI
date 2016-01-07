import os

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.logger import Logger as log

from .screens import MainScreen, SettingsScreen


class SmartHouseApp(App):
    def load_kv(self, *args, **kwargs):
        for f in [
            'styles',
            'debug',
            'panels/base',
            'panels/weather',
            'panels/music',
            'panels/sport',
            'panels/calendar',
            'screens/main',
            'screens/settings',
        ]:
            Builder.load_file(os.path.join('smart_house_ui/uix', f + '.kv'))

    def build(self):
        self.sm = ScreenManager()

        self.main_screen = MainScreen(name='main')
        self.sm.add_widget(self.main_screen)

        self.settings_screen = SettingsScreen(name='settings')
        self.sm.add_widget(self.settings_screen)

        self.settings_screen.setup()
        return self.sm

    def on_stop(self):
        log.info('Stopping app...')
        self.main_screen.panels.music.release()
