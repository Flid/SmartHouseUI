import os
import re
import random
import logging

import vlc
from vlc import EventType
from time import sleep

log = logging.getLogger(__name__)



class AudioPlayer(object):
    _PROXY_METHODS = {
        'stop',
        'pause',
        'get_position',
        'get_length',
    }

    def __init__(self):
        self._instance = vlc.Instance()

        self._track_list = []
        self._current_track_id = 0

    def _reset_player(self):
        self._player = self._instance.media_player_new()

        self._event_manager = self._player.event_manager()

        self.bind_event(
            EventType.MediaPlayerEndReached,
            self._on_track_end_reached,
        )

    def _get_media(self, filename):
        m = self._instance.media_new(filename)
        m.parse()
        if not m.get_duration():
            log.warning('Corrupted file: %s' % filename)
            return
        return m

    def _normalize_track_id(self, val):
        if val is None:
            return 0

        if val >= len(self._track_list):
            return len(self._track_list) - 1

        if val < 0:
            return 0

        return val

    def play(self, track_id=None):
        self._current_track_id = self._normalize_track_id(track_id)
        print('Starting to play track %s' % self._current_track_id)

        self._reset_player()

        self._player.set_media(
            self._get_media(self._track_list[self._current_track_id]),
        )
        self._player.play()

    def next(self):
        print('Starting the next track')
        self.play(
            (self._current_track_id + 1) % len(self._track_list),
        )

    def stop(self):
        self._player.stop()

    def set_position(self, pos):
        self._player.set_position(pos)

    def load_directory(self, path):

        re_audio_name = re.compile('^.*\.(mp3|wav|ogg|py)$')

        for path, dirs, files in os.walk(path):
            for f in files:
                if not re_audio_name.match(f):
                    continue

                fname = os.path.join(path, f)
                media = self._get_media(fname)
                if not media:
                    continue

                self._track_list.append(fname)

    def __getattr__(self, item):
        if item in self._PROXY_METHODS:
            return getattr(self._player, item)

        raise AttributeError(item)


    def bind_event(self, event, callback_func, *args):
        self._event_manager.event_attach(
            event,
            callback_func,
            *args
        )

    def _on_track_end_reached(self, event):
        print('Track end reached')
        self.next()


p = AudioPlayer()


p.load_directory('/home/flid/hobby/git/SmartHouseUI')

p.play(0)

sleep(1)

p.set_position(0.99)

sleep(5)

print('1')

p.set_position(0.99)

sleep(5)

print('2')

p.set_position(0.99)

sleep(5)
