import sys
import os

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from utils import self_update
from weather_widget import WeatherWidget


class MainScreen(Screen):
    pass


class SettingsScreen(Screen):
    update_btn = ObjectProperty(None)

    def on_update_btn_click(self, instance):
        self_update()

    def setup(self):
        self.update_btn.bind(on_press=self.on_update_btn_click)


class SmartHouseApp(App):
    kv_file = 'smart_house.kv'

    def build(self):
        self.sm = ScreenManager()

        self.main_screen = MainScreen(name='main')
        self.sm.add_widget(self.main_screen)

        self.settings_screen = SettingsScreen(name='settings')
        self.sm.add_widget(self.settings_screen)

        self.settings_screen.setup()

        return self.sm


app = SmartHouseApp()
app.run()