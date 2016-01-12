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
from kivy.graphics.context_instructions import (
    PushMatrix,
    PopMatrix,
    Rotate,
)


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
            'title': media.get_meta(vlc.Meta.Title) or os.path.basename(path),
            'artist': media.get_meta(vlc.Meta.Artist) or 'Artist Unknown',
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
    is_playing = BooleanProperty(False)
    track_id = NumericProperty(-1)
    position = NumericProperty(0)
    volume = NumericProperty(0.5)

    def __init__(self):
        self._track_list = TrackList()
        self._track_source = None
        self._init_player()
        self.track_id = 0

    def _init_player(self):
        self._instance = vlc.Instance()
        self._player = self._instance.media_player_new()
        self._event_manager = self._player.event_manager()

        self._bind_event(
            vlc.EventType.MediaPlayerPositionChanged,
            self._on_position_changed,
        )
        self._bind_event(
            vlc.EventType.MediaPlayerAudioVolume,
            self._on_volume_changed,
        )
        self._bind_event(
            vlc.EventType.MediaPlayerEndReached,
            self._on_track_end_reached,
        )
        self._bind_event(
            vlc.EventType.MediaPlayerPaused,
            self._on_paused,
        )
        self._bind_event(
            vlc.EventType.MediaPlayerPlaying,
            self._on_playing,
        )

        self._media = None
        self.set_volume(self.volume)

    def _on_track_end_reached(self, event):
        log.debug('Track end reached')
        Clock.schedule_once(lambda dt: self.next())

    def _on_paused(self, event):
        log.debug('Paused event')
        self.is_playing = False

    def _on_playing(self, event):
        log.debug('Playing event')
        self.is_playing = True

    def _on_position_changed(self, event):
        self.position = event.u.new_position

    def set_position(self, value):
        self._player.set_position(value)

    def _on_volume_changed(self, event):
        self.volume = self._player.audio_get_volume() / 100.

    def set_volume(self, value):
        self._player.audio_set_volume(int(value * 100))

    def _normalize_track_id(self, val):
        return val % self.tracks_count

    def _bind_event(self, event, callback_func, *args):
        self._event_manager.event_attach(
            event,
            callback_func,
            *args
        )

    def play(self, track_id=None):
        if self.tracks_count == 0:
            return

        if track_id is not None:
            track_id = self._normalize_track_id(track_id)

        log.debug('Starting to play track %s' % (track_id if track_id is not None else '<undef>'))

        if self._media is None or track_id is not None:
            if track_id is None:
                track_id = 0
            self.stop()
            log.debug('Loading new media...')
            self._media = self._track_list.get_media(track_id)
            self._player.set_media(self._media)

        self._player.play()

        if track_id is not None:
            self.track_id = track_id

    def next(self):
        if self.tracks_count == 0:
            return

        log.debug('Starting the next track')
        self.play(self.track_id + 1)

    def prev(self):
        if self.tracks_count == 0:
            return

        log.debug('Starting the prev track')
        self.play(self.track_id - 1)

    def stop(self):
        if self.tracks_count == 0:
            return

        log.debug('Stopping track...')
        self.pause()
        if self._media:
            self._media.release()
            self._media = None

    def pause(self):
        if self.tracks_count == 0:
            return

        self._player.pause()

    def load_directory(self, path):
        path = os.path.expanduser(path)
        log.debug('Loading the track list from `%s`' % path)
        self._track_list.reset()
        self._track_list.add_directory(path)

    def get_current_track_info(self):
        if self.tracks_count == 0:
            return

        return self._track_list.get_info(self.track_id)

    def delete(self):
        self._player.delete()

    @property
    def tracks_count(self):
        return self._track_list.count()


class PlayerWidget(Widget):
    def __init__(self, *args, **kwargs):
        super(PlayerWidget, self).__init__(*args, **kwargs)
        if FAKE_VLC:
            return

        self.audio_player = AudioPlayer()

        self.audio_player.bind(
            position=self.on_position_change,
            track_id=self.on_track_id_change,
            is_playing=self.on_is_playing_changed,
        )

    def _set_label_time(self, label, value):
        value /= 1000.
        seconds = int(value % 60)
        minutes = int(value / 60)
        label.text = '%d:%0.2d' % (minutes, seconds)

    def release(self):
        log.info('Deleting PlayerWidget')

        if FAKE_VLC:
            return

        self.audio_player.delete()

    def get_track_info(self):
        return self.audio_player.get_current_track_info()

    def on_position_change(self, instance, value):
        self.progress_bar.value = value

        info = self.get_track_info()

        self._set_label_time(
            self.current_time,
            info['duration'] * value if info else 0,
        )

    def on_track_id_change(self, instance, value):
        info = self.get_track_info()

        self._set_label_time(
            self.total_time,
            info['duration'] if info else None,
        )
        self._set_label_time(self.current_time, 0)
        self.title.text = info['title'] if info else '--//--'
        self.artist.text = info['artist'] if info else '--//--'

    def on_is_playing_changed(self, instance, is_playing):
        log.debug('is_playing is now %s' % is_playing)
        if is_playing:
            self.play_btn.source = 'static/music/pause.png'
        else:
            self.play_btn.source = 'static/music/play.png'

    def on_play_press(self):
        if self.audio_player.tracks_count == 0:
            self.audio_player.load_directory('~/Music/')

        if self.audio_player.is_playing:
            self.audio_player.pause()
        else:
            self.on_track_id_change(None, None)
            self.audio_player.play()


class ProgressBarBehavior(object):
    vertical = False

    def init(self, **kwargs):
        self._value = -1
        self.register_event_type('on_manual_change')

    def on_vertical(self, *args):
        self._rotation.origin=self.center
        if self.vertical:
            self._rotation.angle = 90
        else:
            self._rotation.angle = 0

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        value = max(0, min(self.max, value))
        if value == self._value:
            return False

        self._value = value
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

        if self.vertical:
            y = touch.y - self.y
            self.value_normalized = y / self.height
        else:
            x = touch.x - self.x
            self.value_normalized = x / self.width

        self.dispatch('on_manual_change')

    def on_touch_down(self, touch):
        self._process_touch(touch)

    def on_touch_move(self, touch):
        self._process_touch(touch)

    def on_manual_change(self):
        pass


class MusicProgressBar(ProgressBarBehavior, Widget):
    def __init__(self, *args, **kwargs):
        super(MusicProgressBar, self).__init__(*args, **kwargs)
        self.init()


class MusicVerticalProgressBar(ProgressBarBehavior, Widget):
    vertical = True

    def __init__(self, *args, **kwargs):
        super(MusicVerticalProgressBar, self).__init__(*args, **kwargs)
        self.init()
