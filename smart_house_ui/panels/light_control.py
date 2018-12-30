from typing import List, Optional, Tuple, NamedTuple

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget
from kivy.config import Config
from datetime import date, timedelta, datetime
from kivy.logger import Logger as log

WEEK_DAYS = [
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
]


class NextAlarmTrigger(NamedTuple):
    is_enabled: bool
    hour: int
    minute: int
    weekday: Optional[int]
    today: bool


class LightControlWidget(Widget):
    current_brightness = NumericProperty(0)
    CHECK_UPDATES_EVERY = 0.5  # sec

    def __init__(self, *args, **kwargs):
        super(LightControlWidget, self).__init__(*args, **kwargs)
        Clock.schedule_interval(self.send_updates, timeout=self.CHECK_UPDATES_EVERY)
        Clock.schedule_interval(self.update_alarm_controls, timeout=10)
        Clock.schedule_once(self.update_alarm_controls, timeout=0)
        self.last_brightness_sent = None

    def send_updates(self, instance):
        brightness = max(0, min(255, int(self.current_brightness)))

        if self.last_brightness_sent != brightness:
            self.last_brightness_sent = brightness

            App.get_running_app().light_control_client.send(
                command="set_brightness", data={"value": brightness}
            )

    def _get_next_alarm_weekday(self, schedule: List[bool]) -> NextAlarmTrigger:
        assert len(schedule) == 7

        now_dt = datetime.now()
        alarm_minute = max(0, min(60, Config.getint('light_controls',
                                                    'alarm_minute')))
        alarm_hour = max(0,
                         min(24, Config.getint('light_controls', 'alarm_hour')))

        alarm_dt = now_dt.replace(hour=alarm_hour, minute=alarm_minute)

        if schedule[now_dt.weekday()] and alarm_dt >= now_dt:
            return NextAlarmTrigger(
                is_enabled=True,
                hour=alarm_hour,
                minute=alarm_minute,
                weekday=now_dt.weekday(),
                today=True,
            )

        # 8, because alarm can be once a week and today's one is off already.
        for i in range(1, 8):
            weekday = (now_dt.weekday() + i) % 7
            if schedule[weekday]:
                return NextAlarmTrigger(
                    is_enabled=True,
                    hour=alarm_hour,
                    minute=alarm_minute,
                    weekday=weekday,
                    today=False,
                )

        return NextAlarmTrigger(
            is_enabled=False,
            hour=alarm_hour,
            minute=alarm_minute,
            weekday=None,
            today=False,
        )

    def update_alarm_controls(self, instance):
        if not App.get_running_app().light_control_client.started:
            return

        schedule = Config.get('light_controls', 'alarm_schedule').lower()

        if schedule == 'off':
            schedule = [False] * 7
        elif schedule == 'every day':
            schedule = [True] * 7
        elif schedule == 'working days':
            schedule = [True, True, True, True, True, False, False]
        else:
            log.warning('Invalaid alarm_schedule in config')
            return

        alarm_trigger = self._get_next_alarm_weekday(schedule)

        if not alarm_trigger.is_enabled:
            self.ids['alarm_state'].text = 'OFF'
        else:
            weekday = "Today" if alarm_trigger.today else WEEK_DAYS[alarm_trigger.weekday]
            self.ids['alarm_state'].text = f'{alarm_trigger.hour:02}:{alarm_trigger.minute:02} ({weekday})'
