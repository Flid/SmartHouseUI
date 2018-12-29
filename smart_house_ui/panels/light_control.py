from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget


class LightControlWidget(Widget):
    current_brightness = NumericProperty(0)
    CHECK_UPDATES_EVERY = 0.5  # sec

    def __init__(self, *args, **kwargs):
        super(LightControlWidget, self).__init__(*args, **kwargs)
        Clock.schedule_interval(self.send_updates, timeout=self.CHECK_UPDATES_EVERY)
        self.last_brightness_sent = None

    def send_updates(self, instance):
        brightness = max(0, min(255, int(self.current_brightness)))

        if self.last_brightness_sent != brightness:
            self.last_brightness_sent = brightness

            App.get_running_app().light_control_client.send(
                command="set_brightness", data={"value": brightness}
            )
