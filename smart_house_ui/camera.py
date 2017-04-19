from kivy.event import EventDispatcher
from prod_config import CAMERA_RECOGNIZER_URL, CAMERA_IMAGE_SIZE
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

    def on_movement(self, pos, size):
        pass

    def api_worker(self):
        from picamera import PiCamera
        import time
        import threading
        import io
        import json
        import requests
        from PIL import Image

        lock = threading.Lock()

        def streams():
            with lock:
                if pool:
                    processor = pool.pop()
                else:
                    processor = None
            if processor:
                yield processor.stream
                processor.event.set()
            else:
                # When the pool is starved, wait a while for it to refill
                time.sleep(0.1)

        def send(img_stream):
            img_stream.seek(0)
            buf = io.BytesIO()
            img = Image.open(img_stream).convert('L')
            img.save(buf, format='JPEG', quality=90)
            buf.seek(0)

            response = requests.post(
                CAMERA_RECOGNIZER_URL + '/recognize',
                files={'img': buf},
            )

            if response.status_code != 200:
                return None

            return json.loads(response.content)

        class ImageProcessor(threading.Thread):
            def __init__(self):
                super(ImageProcessor, self).__init__()
                self.stream = io.BytesIO()
                self.event = threading.Event()
                self.terminated = False
                self.daemon = True
                self.start()

            def run(self):
                # This method runs in a separate thread
                global done
                while not self.terminated:
                    # Wait for an image to be written to the stream
                    if self.event.wait(1):
                        try:
                            send(self.stream)
                        finally:
                            # Reset the stream and event
                            self.stream.seek(0)
                            self.stream.truncate()
                            self.event.clear()
                            # Return ourselves to the pool
                            with lock:
                                pool.append(self)

        _cap = PiCamera()
        _cap.resolution = CAMERA_IMAGE_SIZE
        _cap.framerate = 8

        time.sleep(0.1)  # Let it stabilize

        pool = [ImageProcessor()]

        _cap.capture_sequence(streams(), use_video_port=True)
