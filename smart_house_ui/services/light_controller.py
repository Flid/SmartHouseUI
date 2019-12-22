import json
import sys
import time
from collections import namedtuple
from threading import Thread

from kivy.logger import Logger as log
import time
import RPi.GPIO as GPIO

from .base import ServiceBase

Message = namedtuple("Message", "body, persistent")


class LightController(ServiceBase):
    UPDATE_INTERVAL = 0.1

    def __init__(self, gpio_port=12, frequency=1000):
        self._gpio_port = gpio_port
        self._frequency = frequency
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self._gpio_port, GPIO.OUT)
        self._current_brightness = 0
        self._target_brightness = 0
        self._brightness_change_speed = 1
        self._exitting = False

        super().__init__()

    def _step_brightness(self):
        if self._current_brightness == self._target_brightness:
            log.info('No brightness change required')
            return

        diff = self._target_brightness - self._current_brightness
        max_diff = self._brightness_change_speed * self.UPDATE_INTERVAL

        if diff > 0:
            diff = max(max_diff, diff)
        else:
            diff = min(-max_diff, diff)

        log.info('Increasing the brightness by {}'.format(diff))
        self._current_brightness += diff
        self._pwm.ChangeDutyCycle(self._current_brightness)

    def _worker(self):
        self._pwm = GPIO.PWM(self._gpio_port, self._frequency)
        self._pwm.start(0)

        while True:
            try:
                if self._exitting:
                    self._pwm.stop()
                    GPIO.cleanup()
                    sys.exit()

                self._step_brightness()

                time.sleep(self.UPDATE_INTERVAL)
            except Exception:
                log.exception('Error processing LightController events')

    def set_brightness(self, value: int):
        assert 0 <= value <= 100
        log.info('Trying to set brightness to {}'.format(value))

        self._target_brightness = value
        self._brightness_change_speed = 5

    def update_settings(self, settings):
        pass  # Not implemented yet
