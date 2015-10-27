import os
import re
import logging

from pyglet.media import (
    Player as _Player,
    load as load_track,
    MediaException,
)
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.event import EventDispatcher

log = logging.getLogger(__name__)


class TrackList(object):
    _re_audio_name = re.compile('^.*\.(mp3|wav|ogg)$', re.IGNORECASE)

    def __init__(self):
        self.reset()

    def reset(self):
        self._tracks = []

    def _get_track_info(self, path):
        src = load_track(path)
        return {
            'path': path,
            'duration': src.duration,
        }

    def add(self, filename):
        print('Loading track from %s...' % filename)
        try:
            self._tracks.append(self._get_track_info(filename))
            return True
        except MediaException:
            print('Failed to load track.')
            return False

    def add_directory(self, path):
        self._tracks = []

        for path, dirs, files in os.walk(path):
            for f in files:
                if not self._re_audio_name.match(f):
                    continue

                self.add(os.path.join(path, f))

    def get_source(self, track_id):
        return load_track(self._tracks[track_id]['path'])

    def count(self):
        return len(self._tracks) if self._tracks else 0

    def get_info(self, track_id):
        return dict(self._tracks[track_id])


class AudioPlayer(EventDispatcher):
    position = NumericProperty(0)
    playing = BooleanProperty(False)
    track_id = NumericProperty(-1)

    def __init__(self):
        self._track_list = TrackList()
        self._track_source = None
        self._player = None
        self._current_track_id = 0
        self._has_manual_position_changes = False

        Clock.schedule_interval(self._update_properties, 0.01)

    def _update_properties(self, *args):

        if self._player is None:
            self.position = 0
            self.playing = False
        else:
            print(self._player.time)
            self.playing = self._player.time != self.position
            self.position = self._player.time

            if not self._has_manual_position_changes and self.position == 0:
                self._player.delete()
                self._player = None
                self._on_track_end()

        self._has_manual_position_changes = False

    def _on_track_end(self):
        print('Track end reached')
        self.next()

    def _normalize_track_id(self, val):
        return val % self._track_list.count()

    def play(self, track_id=0):
        self._current_track_id = self._normalize_track_id(track_id)
        print('Playing track %s' % self._current_track_id)

        self._track_source = self._track_list.get_source(self._current_track_id)

        self._has_manual_position_changes = False
        self._player = _Player()
        self._player.queue(self._track_source)
        self._player.play()

    def next(self):
        print('Starting the next track')
        self.play(self._current_track_id + 1)

    def stop(self):
        self.pause()
        self._player = None

    def pause(self):
        self._has_manual_position_changes = True
        self._player.pause()

    def load_directory(self, path):
        self._track_list.reset()
        self._track_list.add_directory(path)

    def get_current_track_info(self):
        return self._track_list.get_info(self._current_track_id)

    def delete(self):
        self._player.delete()


class PlayerWidget(Widget):
    play_btn = ObjectProperty(None)
    position_label = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(PlayerWidget, self).__init__(*args, **kwargs)
        self._audio_player = AudioPlayer()
        self._audio_player.bind(position=self.on_position_change)

    def release(self):
        print('Deleting PlayerWidget')
        self._audio_player.delete()

    def on_position_change(self, instance, value):
        duration = self._audio_player.get_current_track_info()['duration']
        self.progress_bar.value = self._audio_player.position/duration

    def on_play_press(self):
        self._audio_player.load_directory('.')
        self._audio_player.play(0)