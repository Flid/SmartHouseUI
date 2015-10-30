import os
import re
import logging

from kivy.properties import (
    NumericProperty,
    ObjectProperty,
    BooleanProperty,
    AliasProperty,
)
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.graphics import Rectangle, Color


try:
    import vlc
    FAKE_VLC = False
except OSError:
    import mock
    vlc = mock.Mock()
    FAKE_VLC = True

log = logging.getLogger(__name__)

class TrackList(object):
    _re_audio_name = re.compile('^.*\.(mp3|wav|ogg)$', re.IGNORECASE)

    def __init__(self):
        self.reset()

    def reset(self):
        self._tracks = []

    def _get_track_info(self, path, media):
        return {
            'path': path,
            'duration': media.get_duration(),
        }

    def add(self, filename):
        log.debug('Loading track from %s...' % filename)
        media = self._load_media(filename)
        if not media:
            log.warning('Failed to load track.')
            return

        self._tracks.append(
            self._get_track_info(filename, media),
        )

    def add_directory(self, path):
        self._tracks = []

        for path, dirs, files in os.walk(path):
            for f in files:
                if not self._re_audio_name.match(f):
                    continue

                self.add(os.path.join(path, f))

    def _load_media(self, filename):
        m = vlc.Media(filename)
        m.parse()
        if not m.get_duration():
            log.warning('Corrupted file: %s' % filename)
            return
        return m

    def get_media(self, track_id):
        return self._load_media(self._tracks[track_id]['path'])

    def count(self):
        return len(self._tracks) if self._tracks else 0

    def get_info(self, track_id):
        try:
            return dict(self._tracks[track_id])
        except IndexError:
            return


class AudioPlayer(EventDispatcher):
    position = NumericProperty(0)
    playing = BooleanProperty(False)
    track_id = NumericProperty(-1)

    def __init__(self):
        self._track_list = TrackList()
        self._track_source = None
        self._init_player()
        self._current_track_id = 0

    def _init_player(self):
        self._instance = vlc.Instance()
        self._player = self._instance.media_player_new()
        self._event_manager = self._player.event_manager()
        self._bind_event(
            vlc.EventType.MediaPlayerEndReached,
            self._on_track_end_reached,
        )
        self._bind_event(
            vlc.EventType.MediaPlayerPositionChanged,
            self._on_position_changed,
        )

        self._media = None

    def _on_track_end_reached(self, event):
        log.debug('Track end reached')
        Clock.schedule_once(lambda dt: self.next())

    def _on_position_changed(self, event):
        log.debug('Position: %s' % event.u.new_position)
        self.position = event.u.new_position

    def _normalize_track_id(self, val):
        return val % self._track_list.count()

    def _bind_event(self, event, callback_func, *args):
        self._event_manager.event_attach(
            event,
            callback_func,
            *args
        )

    def play(self, track_id=0):
        if self._media is not None:
            self._player.stop()
            self._media.release()

        self._current_track_id = self._normalize_track_id(track_id)

        self._media = self._track_list.get_media(self._current_track_id)
        self._player.set_media(self._media)
        self._player.play()

    def next(self):
        log.debug('Starting the next track')
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
        if FAKE_VLC:
            return

        self._audio_player = AudioPlayer()

        self._audio_player.bind(position=self.on_position_change)

    def release(self):
        log.info('Deleting PlayerWidget')

        if FAKE_VLC:
            return

        self._audio_player.delete()

    def on_position_change(self, instance, value):
        self.progress_bar.value = value

    def on_play_press(self):
        self._audio_player.load_directory('.')
        self._audio_player.play(0)


class MusicProgressBar(Widget):
    dot = ObjectProperty(None)

    def __init__(self, **kwargs):
        self._value = -1
        super(MusicProgressBar, self).__init__(**kwargs)

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        value = max(0, min(self.max, value))
        if value == self._value:
            return False

        if self.dot is None:
            return True

        self._value = value

        self.dot.pos = [
            self.x + self.width * self.value_normalized - self.dot.width/2,
            self.y + self.height / 2 - self.dot.height/2,
        ]

        return True

    value = AliasProperty(_get_value, _set_value)

    def get_norm_value(self):
        d = self.max
        if d == 0:
            return 0
        return self.value / float(d)

    def set_norm_value(self, value):
        self.value = value * self.max

    value_normalized = AliasProperty(
        get_norm_value,
        set_norm_value,
        bind=('value', 'max'),
    )

    max = NumericProperty(100.)

    def _process_touch(self, touch):
        if not self.collide_point(*touch.pos):
            return
        x = touch.pos[0] - self.pos[0]
        self.value_normalized = x / self.width

    def on_touch_down(self, touch):
        self._process_touch(touch)

    def on_touch_move(self, touch):
        self._process_touch(touch)
