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
    def __init__(self, gpio_port=12, frequency=1000):
        self._queue = Queue(maxsize=10)
        super().__init__()
        self._gpio_port = gpio_port
        self._frequency = frequency
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self._gpio_port, GPIO.OUT)

    def _process_message(self, pwm, msg):
        code, payload = msg

        if code == 'exit':
            pwm.stop()
            GPIO.cleanup()
            sys.exit()

        if code == 'set_brightness':
            pwm.ChangeDutyCycle(payload)

    def _worker(self):
        pwm = GPIO.PWM(self._gpio_port, self._frequency)
        pwm.start(0)

        while True:
            while True:
                try:
                    msg = self._queue.get_nowait()
                    try:
                        self._process_message(pwm, msg)
                    except Exception:
                        log.exception('Error while processing LightController command')
                        time.sleep(0.1)

                except Empty:
                    time.sleep(0.1)

    def set_brightness(self, value: int):
        assert 0 <= value <= 100

        try:
            self._queue.put(('set_brightness', value))
        except Full:
            log.warning('Message queue is full')


    def update_settings(self, settings):
        pass  # Not implemented yet
