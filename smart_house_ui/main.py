from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.image import Image
from kivy.animation import Animation

from smart_house_ui.utils import self_update, sensors_update


class MainScreen(Screen):
    pass


class BlinkingImage(Image):
    def __init__(self, *args, **kwargs):
        super(BlinkingImage, self).__init__(*args, **kwargs)

        anim = Animation(opacity=0.4) + Animation(opacity=0.8)
        anim.repeat = True
        anim.start(self)


class SettingsScreen(Screen):
    update_btn = ObjectProperty(None)
    sensors_update_btn = ObjectProperty(None)

    def on_update_btn_press(self, instance):
        self_update()

    def on_sensors_update_btn_press(self, inst):
        sensors_update()

    def setup(self):
        self.update_btn.bind(on_press=self.on_update_btn_press)
        self.sensors_update_btn.bind(on_press=self.on_sensors_update_btn_press)


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