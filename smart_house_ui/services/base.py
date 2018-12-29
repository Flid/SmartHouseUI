import abc
from threading import Thread


class ServiceBase:
    def __init__(self):
        self._srv_thread = None
        self.started = False

    @abc.abstractmethod
    def _worker(self):
        pass

    def start(self):
        self._srv_thread = Thread(target=self._worker, daemon=True)
        self._srv_thread.start()
        self.started = True
