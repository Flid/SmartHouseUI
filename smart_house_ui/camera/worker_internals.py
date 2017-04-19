from picamera import PiCamera
import time
import threading
import io
import json
import requests
from PIL import Image
import logging
from prod_config import CAMERA_RECOGNIZER_URL, CAMERA_IMAGE_SIZE
from face_recognition.motion import MotionDetector
import numpy as np


log = logging.getLogger(__name__)
lock = threading.Lock()
task_pool = []


class ImageProcessorBase(threading.Thread):
    def __init__(self, job_queue):
        super(ImageProcessorBase, self).__init__()
        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.daemon = True
        self._job_queue = job_queue
        self.start()

    def run(self):
        # This method runs in a separate thread
        while not self.terminated:
            # Wait for an image to be written to the stream
            if self.event.wait(1):
                try:
                    self.process_frame()
                except Exception:
                    log.exception('Error while processing frame')
                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
                    # Return ourselves to the pool
                    with lock:
                        task_pool.append(self)

    def process_frame(self):
        pass


class FaceImageProcessor(ImageProcessorBase):
    def process_frame(self):
        self.stream.seek(0)
        buf = io.BytesIO()
        img = Image.open(self.stream).convert('L')
        img.save(buf, format='JPEG', quality=90)
        buf.seek(0)

        response = requests.post(
            CAMERA_RECOGNIZER_URL + '/recognize',
            files={'img': buf},
        )

        if response.status_code != 200:
            return

        result = json.loads(response.content.decode('utf-8'))

        if result:
            self._job_queue.put({'type': 'face', 'data': result})


class MotionImageProcessor(ImageProcessorBase):
    def __init__(self, *args, **kwargs):
        super(MotionImageProcessor, self).__init__(*args, **kwargs)
        self.md = MotionDetector(1000)

    def process_frame(self):
        self.stream.seek(0)
        img = Image.open(self.stream).convert('L')
        arr = np.array(img)
        result = self.md.submit_frame(arr)

        if result.get('center'):
            log.info('Motion %s', result)
            self._job_queue.put({'type': 'motion', 'data': result['center']})


def run(job_queue):
    global task_pool

    log.info('Setting up camera')
    _cap = PiCamera()
    _cap.resolution = CAMERA_IMAGE_SIZE
    _cap.framerate = 30

    time.sleep(1)  # Let it stabilize

    task_pool += [FaceImageProcessor(job_queue), MotionImageProcessor(job_queue)]
    log.info('Pool initialized')

    def streams():
        while True:
            with lock:
                if task_pool:
                    processor = task_pool.pop()
                else:
                    processor = None
            if processor:
                yield processor.stream
                processor.event.set()
            else:
                # When the pool is starved, wait a while for it to refill
                time.sleep(0.05)

    _cap.capture_sequence(streams(), use_video_port=True)
