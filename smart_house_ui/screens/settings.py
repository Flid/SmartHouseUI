# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from datetime import date
from typing import Any, Dict, List

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config, ConfigParser
from kivy.uix.screenmanager import Screen
from kivy.uix.settings import Settings

_ORIGINAL_KEYS_KEYS = {"type", "title", "desc", "key", "section", "options"}


def _get_alarm_on_option(schedule_option, value):
    value = value.lower()

    if value == "off":
        enabled = False
    elif value == "every day":
        enabled = True
    elif value == "working days":
        enabled = date.today().weekday() < 5
    else:
        raise ValueError()

    return {"alarm_enabled": enabled}


_LIGHT_CONTROL_PANEL = [
    {"type": "title", "title": "General"},
    {
        "type": "string",
        "title": "IP",
        "desc": "IP address of the device. Restart required to take effect.",
        "section": "light_controls",
        "key": "ip_address",
        "default": "192.168.0.50",
    },
    {
        "type": "bool",
        "title": "Device Enabled",
        "desc": "If disabled, we stop any interactions with the device. Restart required to take effect.",
        "section": "light_controls",
        "key": "device_enabled",
        "default": "1",
    },
    {"type": "title", "title": "Alarm"},
    {
        "type": "options",
        "options": ["Off", "Every day", "Working days"],
        "title": "Alarm Schedule",
        "desc": "Decide which days to turn alarm on",
        "section": "light_controls",
        "key": "alarm_schedule",
        "default": "Working days",
        "hardware_option_generator": _get_alarm_on_option,
    },
    {
        "type": "numeric",
        "title": "Hour",
        "desc": "An hour when alarm goes off",
        "section": "light_controls",
        "key": "alarm_hour",
        "is_hardware_option": True,
        "default": 7,
        "max": 23,
        "min": 0,
        "format": "int",
    },
    {
        "type": "numeric",
        "title": "Minute",
        "desc": "A minute when alarm goes off",
        "section": "light_controls",
        "key": "alarm_minute",
        "is_hardware_option": True,
        "default": 0,
        "max": 59,
        "min": 0,
        "format": "int",
    },
    {
        "type": "numeric",
        "title": "Fading In Duration",
        "desc": "A number of seconds alarm is gradually turning on (10-1800)",
        "section": "light_controls",
        "key": "alarm_turn_on_duration",
        "is_hardware_option": True,
        "default": 600,
        "min": 10,
        "max": 1800,
        "format": "int",
    },
    {
        "type": "numeric",
        "title": "Staying On Duration",
        "desc": "A number of seconds alarm stays on between fading in and out (10-65000)",
        "section": "light_controls",
        "key": "alarm_stay_on_duration",
        "is_hardware_option": True,
        "format": "int",
        "min": 10,
        "max": 65000,
        "default": 7200,
    },
    {
        "type": "numeric",
        "title": "Fading Out Duration",
        "desc": "A number of seconds alarm is gradually turning off (5-600)",
        "section": "light_controls",
        "key": "alarm_turn_off_duration",
        "is_hardware_option": True,
        "format": "int",
        "min": 5,
        "max": 600,
        "default": 60,
    },
    {
        "type": "numeric",
        "title": "Audio Volume",
        "desc": "Max alarm audio volume (0-255)",
        "section": "light_controls",
        "key": "player_max_volume",
        "is_hardware_option": True,
        "format": "int",
        "min": 0,
        "max": 255,
        "default": 128,
    },
]
_OPTION_BY_KEY = {}


def _setup_defaults():
    Config.adddefaultsection("light_controls")

    for option in _LIGHT_CONTROL_PANEL:
        if "key" in option and "default" in option:
            Config.setdefault("light_controls", option["key"], option["default"])


def _clean_bool(option: Dict, value):
    return value == "1"


def _number_from_option(option: Dict, value: Any):
    if option.get("format") == "int":
        value = int(value)
    elif option.get("format") == "float":
        value = float(value)
    elif option.get("format") is not None:
        raise ValueError('"format" key can only be "int" ot "float"')

    if "max" in option:
        value = min(option["max"], value)

    if "min" in option:
        value = max(option["min"], value)

    return value


def clean_value(option, value):
    if not option:
        return value

    if option["type"] == "bool":
        return _clean_bool(option, value)

    if option["type"] == "numeric":
        return _number_from_option(option, value)

    return value


def _setup_panel(
    settings: Settings, section_name: str, panel_options: List[Dict[str, Any]]
):
    processed_options = []

    for option in panel_options:
        processed_options.append(
            {k: option[k] for k in _ORIGINAL_KEYS_KEYS if k in option}
        )

        if "section" not in option or "key" not in option:
            continue

        assert option["section"] == section_name

        _OPTION_BY_KEY[(section_name, option["key"])] = option

    settings.add_json_panel(
        "Light Controls", Config, data=json.dumps(processed_options)
    )


class SettingsScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        settings: Settings = self.ids["settings_widget"]
        settings.add_kivy_panel()
        _setup_panel(settings, "light_controls", _LIGHT_CONTROL_PANEL)

        settings.bind(on_config_change=self.on_config_change, on_close=self.on_close)
        Clock.schedule_once(self.update_all_settings, timeout=0)
        Clock.schedule_interval(self.update_all_settings, timeout=600)

    def _get_hardware_settings(self, option, value):
        if option.get("hardware_option_generator"):
            return option["hardware_option_generator"](option, value)

        elif not option or not option.get("is_hardware_option"):
            return None
        else:
            return {option["key"]: clean_value(option, value)}

    def on_config_change(
        self,
        settings: Settings,
        config: ConfigParser,
        section: str,
        key: str,
        value: Any,
    ):
        if section == "light_controls":
            option = _OPTION_BY_KEY.get((section, key))

            if not option:
                return

            settings = self._get_hardware_settings(option, value)

            if settings:
                App.get_running_app().light_control_client.send(
                    command="update_settings", data=settings, persistent=True
                )

    def update_all_settings(self, instance):
        all_settings = {}

        for (section, key), option in _OPTION_BY_KEY.items():
            settings = self._get_hardware_settings(option, Config.get(section, key))
            if settings:
                all_settings.update(settings)

        App.get_running_app().light_control_client.send(
            command="update_settings", data=all_settings, persistent=True
        )

    def on_close(self, *args):
        App.get_running_app().sm.current = "main"


_setup_defaults()
