import threading
import time

import pytest

from software.controller import Controller
from software.hardware.mock.buzzer import MockBuzzer
from software.hardware.mock.leds import MockLEDStrip
from software.models import MediaType, PlaybackState, Tag
from software.player import Player


class FakePlayer(Player):
    """Player that doesn't use mpv at all."""

    def __init__(self):
        super().__init__()
        self._playing = False
        self._end_callback = None

    def play(self, filepath, media_type):
        self._playing = True

    def stop(self):
        self._playing = False

    def pause_toggle(self):
        pass

    @property
    def is_playing(self):
        return self._playing

    def cleanup(self):
        pass

    def simulate_end(self):
        """Simulate playback ending."""
        self._playing = False
        if self._on_playback_end:
            self._on_playback_end()


@pytest.fixture
def controller(db, sample_media, tmp_path):
    leds = MockLEDStrip()
    buzzer = MockBuzzer()
    player = FakePlayer()
    ctrl = Controller(db, player, leds, buzzer)
    return ctrl, player, db, sample_media


def test_idle_state(controller):
    ctrl, _, _, _ = controller
    assert ctrl.state == PlaybackState.IDLE


def test_unknown_tag_stays_idle(controller):
    ctrl, _, _, _ = controller
    ctrl.on_tag_scanned("UNKNOWN")
    assert ctrl.state == PlaybackState.IDLE


def test_tag_with_no_file_stays_idle(controller):
    ctrl, _, db, sample_media = controller
    # Map a tag to media, but the file won't exist on disk
    tag = Tag(uid="AAA111", media_id=sample_media["audio_id"])
    db.add_tag(tag)
    ctrl.on_tag_scanned("AAA111")
    # File doesn't exist, so should go back to IDLE
    assert ctrl.state == PlaybackState.IDLE


def test_register_mode_captures_uid(controller):
    ctrl, _, _, _ = controller
    ctrl.register_mode = True
    ctrl.on_tag_scanned("NEWUID")
    assert ctrl.last_scanned_uid == "NEWUID"
    assert ctrl.state == PlaybackState.IDLE  # Doesn't trigger playback


def test_playback_lock_ignores_tags(controller):
    ctrl, player, db, sample_media = controller
    # We need to get into PLAYING state. Since files don't exist,
    # we'll manipulate state directly for this test.
    tag = Tag(uid="TAG1", media_id=sample_media["audio_id"])
    db.add_tag(tag)

    # Manually put controller in PLAYING state
    ctrl._state = PlaybackState.PLAYING

    # Try scanning — should be ignored
    ctrl.on_tag_scanned("TAG1")
    assert ctrl.state == PlaybackState.PLAYING


def test_stop_returns_to_idle(controller):
    ctrl, player, db, sample_media = controller
    ctrl._state = PlaybackState.PLAYING
    ctrl._current_log_id = db.log_playback_start(sample_media["audio_id"])
    ctrl.on_stop()
    assert ctrl.state == PlaybackState.IDLE


def test_get_status(controller):
    ctrl, _, _, _ = controller
    status = ctrl.get_status()
    assert "state" in status
    assert "video_stats" in status
    assert status["state"] == "idle"
