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
        self._player = vlc.MediaListPlayer()
        self._event_manager = self._player.event_manager()

        self.bind_event(
            EventType.MediaPlayerPositionChanged,
            self._on_track_end_reached,
        )

        self._media_list = vlc.MediaList()

    def _get_media(self, filename):
        m = vlc.Media(filename)
        m.parse()
        if not m.get_duration():
            log.warning('Corrupted file: %s' % filename)
            return
        return m

    def play(self, track_id=0):
        self._player.play()

    def stop(self):
        self._player.stop()

    def set_position(self, pos):
        self._player.get_media_player().set_position(pos)

    def load_directory(self, path):

        re_audio_name = re.compile('^.*\.(mp3|wav|ogg|py)$')

        for path, dirs, files in os.walk(path):
            for f in files:
                if not re_audio_name.match(f):
                    continue

                media = self._get_media(os.path.join(path, f))
                if not media:
                    continue

                self._media_list.add_media(media)

        self._player.set_media_list(self._media_list)

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
        pass


def pos_changed_cb(event):
    print('Positition', event.u.new_position)



p = AudioPlayer()
p.bind_event(EventType.MediaPlayerPositionChanged, pos_changed_cb)


p.load_directory('/home/flid/hobby/git/SmartHouseUI')

p.play()
p.set_position(0.99)

for _ in range(2):
    print(p.get_position())
    sleep(1)

p.set_position(0.99)

print 'l', p.get_length() / 1000.0

sleep(5)


