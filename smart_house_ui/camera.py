from kivy.event import EventDispatcher


class MovementTracker(EventDispatcher):
    def __init__(self):
        self.register_event_type('on_movement')

        from kivy.clock import Clock
        Clock.schedule_interval(self._send, 1)

    def _send(self, *args):
        from random import randint
        self.dispatch('on_movement', (randint(0, 800), randint(0, 480)), (10, 10))

    def on_movement(self, pos, size):
        pass
