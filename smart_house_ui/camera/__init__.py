from kivy.event import EventDispatcher
from multiprocessing import Process, Queue


class MovementTracker(EventDispatcher):
    def __init__(self):
        self.register_event_type('on_movement')
        self.register_event_type('on_face_recognized')

        self._job_queue = Queue()
        self._worker_process = Process(target=self.api_worker)
        self._worker_process.daemon = True
        self._worker_process.start()

        from kivy.clock import Clock
        Clock.schedule_interval(self._send, 1)

    def _send(self, *args):
        while not self._job_queue.empty():
            result = self._job_queue.get()

            t = result.get('type')

            if t == 'motion':
                self.dispatch('on_movement', result['data'])
            elif t == 'face':
                self.dispatch('on_face_recognized', result['data'])

    def on_movement(self, pos):
        pass

    def on_face_recognized(self, faces):
        pass

    def api_worker(self):
        from smart_house_ui.camera.worker_internals import run
        run(self._job_queue)
