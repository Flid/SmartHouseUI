from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.switch import Switch
from kivy.properties import ObjectProperty
from kivy.vector import Vector
from kivy.core.window import Window
from kivy.uix.layout import Layout
from kivy.clock import Clock
from kivy.uix.button import Button


from kivy.uix.screenmanager import Screen, ScreenManager


class MainScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class SmartHouseApp(App):
    kv_file='smart_house.kv'

    def build(self):
        self.sm = ScreenManager()

        self.main_screen = MainScreen(name='main')
        self.sm.add_widget(self.main_screen)

        self.settings_screen = SettingsScreen(name='settings')
        self.sm.add_widget(self.settings_screen)

        return self.sm


app = SmartHouseApp()

import json
import socket

data = {
    'type': 'motors_state',
    'data': {
        'vertical': 1,
        'horizontal': 0,
    },
}

for i in range(100):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect(('192.168.42.1', 9999))
    clientsocket.send(json.dumps(data).encode())

exit()

print(clientsocket.recv(1024))