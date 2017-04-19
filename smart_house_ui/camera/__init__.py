from kivy.event import EventDispatcher
from multiprocessing import Process, Queue


class MovementTracker(EventDispatcher):
    def __init__(self):
        self.register_event_type('on_movement')

        self._job_queue = Queue()
        self._worker_process = Process(target=self.api_worker)
        self._worker_process.daemon = True
        self._worker_process.start()

        from kivy.clock import Clock
        Clock.schedule_interval(self._send, 1)

    def _send(self, *args):
        while not self._job_queue.empty():
            result = self._job_queue.get()

            motion_center = result.get('motion', {}).get('center')

            if motion_center:
                self.dispatch('on_movement', motion_center)

    def on_movement(self, pos):
        pass

    def api_worker(self):
        from smart_house_ui.camera.worker_internals import run
        run()
