import json
import sys
import time
from collections import namedtuple
from threading import Thread

from kivy.logger import Logger as log
import time
import pigpio

from .base import ServiceBase

Message = namedtuple("Message", "body, persistent")


class LightController(ServiceBase):
    UPDATE_INTERVAL = 0.1

    def __init__(self, pin=18):
        self._pin = pin
        self._current_brightness = 0
        self._target_brightness = 0
        self._brightness_change_speed = 1
        self._exitting = False

        self._pwm = pigpio.pi()
        self._pwm.set_mode(self._pin, pigpio.OUTPUT)

        if not self._pwm.connected:
            raise RuntimeError('Failed to initialize PWM')

        super().__init__()

    def _step_brightness(self):
        if self._current_brightness == self._target_brightness:
            return

        diff = self._target_brightness - self._current_brightness
        max_diff = self._brightness_change_speed * self.UPDATE_INTERVAL

        if diff > 0:
            diff = max(max_diff, diff)
        else:
            diff = min(-max_diff, diff)

        log.info('Increasing the brightness by {}'.format(diff))
        self._current_brightness += diff
        self._pwm.set_PWM_dutycycle(self._current_brightness)

    def _worker(self):
        while True:
            try:
                if self._exitting:
                    sys.exit()

                self._step_brightness()

                time.sleep(self.UPDATE_INTERVAL)
            except Exception:
                log.exception('Error processing LightController events')

    def set_brightness(self, value: int):
        assert 0 <= value <= 255
        self._target_brightness = value
        self._brightness_change_speed = 5

    def update_settings(self, settings):
        pass  # Not implemented yet
