import json
import sys
import time
from collections import namedtuple
from queue import Queue, Empty, Full
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
        self._pwm = GPIO.PWM(self._gpio_port, self._frequency)
        self._pwm.start(0)

        self._queue = Queue(maxsize=10)
        self._current_brightness = 0
        self._target_brightness = 0
        self._brightness_change_speed = 1

        super().__init__()

    def _process_message(self, msg):
        code, payload = msg

        if code == 'exit':
            self._pwm.stop()
            GPIO.cleanup()
            sys.exit()

        if code == 'set_brightness':
            self._target_brightness = payload
            self._brightness_change_speed = 5

    def _step_brightness(self):
        if self._current_brightness == self._target_brightness:
            log.info('No brightness change required')
            return

        diff = self._target_brightness - self._current_brightness
        max_diff = self._brightness_change_speed * self.UPDATE_INTERVAL

        diff = max(max_diff, diff)
        diff = min(-max_diff, diff)
        log.info('Increasing the brightness by {}'.format(diff))
        self._current_brightness += diff
        self._pwm.ChangeDutyCycle(self._current_brightness)


    def _worker(self):
        while True:
            while True:
                try:
                    msg = self._queue.get_nowait()
                    try:
                        self._process_message(msg)
                    except Exception:
                        log.exception('Error while processing LightController command')

                except Empty:
                    pass

            time.sleep(self.UPDATE_INTERVAL)
            self._step_brightness()

    def set_brightness(self, value: int):
        assert 0 <= value <= 100

        try:
            self._queue.put(('set_brightness', value))
        except Full:
            log.warning('Message queue is full')


    def update_settings(self, settings):
        pass  # Not implemented yet
