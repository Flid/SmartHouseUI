from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget


class SidebarWidget(Widget):
    settings_btn = ObjectProperty(None)
    quit_btn = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(SidebarWidget, self).__init__(*args, **kwargs)

    def on_btn_settings(self):
        screen_manager = self.parent.parent.manager
        screen_manager.transition.direction = "left"
        screen_manager.current = "settings"

    def on_btn_quit(self):
        # exit()
        pass  # It will be auto restarted by systemd anyway
