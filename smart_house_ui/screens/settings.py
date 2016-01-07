# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from kivy.uix.screenmanager import Screen

from smart_house_ui.utils import self_update, sensors_update


class SettingsScreen(Screen):
    def __init__(self, *args, **kwargs):
        super(SettingsScreen, self).__init__(*args, **kwargs)
        self.ids['update_btn'].bind(on_press=self.on_update_btn_press)
        self.ids['sensors_update_btn'].bind(on_press=self.on_sensors_update_btn_press)

    def on_update_btn_press(self, instance):
        self_update()

    def on_sensors_update_btn_press(self, inst):
        sensors_update()

