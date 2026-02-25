import logging
import threading
from pathlib import Path
from typing import Optional

from software.config import AUDIO_DIR, VIDEO_DIR
from software.db import Database
from software.hardware.base import Buzzer, LEDStrip
from software.limits import check_video_limit
from software.models import MediaType, PlaybackState
from software.player import Player

logger = logging.getLogger(__name__)


class Controller:
    def __init__(self, db: Database, player: Player, leds: LEDStrip, buzzer: Buzzer):
        self._db = db
        self._player = player
        self._leds = leds
        self._buzzer = buzzer
        self._lock = threading.Lock()
        self._state = PlaybackState.IDLE
        self._current_log_id: Optional[int] = None
        self._current_media_id: Optional[int] = None
        self._current_tag_uid: Optional[str] = None
        self._was_last_video = False
        self._register_mode = False
        self._last_scanned_uid: Optional[str] = None

        # Wire up player end callback
        self._player._on_playback_end = self._on_playback_end

        # Start in idle
        self._leds.idle()

    @property
    def state(self) -> PlaybackState:
        return self._state

    @property
    def register_mode(self) -> bool:
        return self._register_mode

    @register_mode.setter
    def register_mode(self, value: bool):
        self._register_mode = value
        if value:
            logger.info("Register mode enabled")
        else:
            logger.info("Register mode disabled")

    @property
    def last_scanned_uid(self) -> Optional[str]:
        return self._last_scanned_uid

    @property
    def current_media_id(self) -> Optional[int]:
        return self._current_media_id

    def on_tag_scanned(self, uid: str):
        """Called by RFID thread when a tag is detected."""
        self._last_scanned_uid = uid

        if self._register_mode:
            logger.info("Register mode: captured UID %s", uid)
            self._buzzer.scan_confirm()
            self._leds.scan_feedback()
            return

        with self._lock:
            if self._state != PlaybackState.IDLE:
                logger.debug("Ignoring tag %s — state is %s", uid, self._state.value)
                return
            self._process_tag(uid)

    def _process_tag(self, uid: str):
        """Process a scanned tag. Must be called with _lock held."""
        # Look up tag → media mapping
        tag = self._db.get_tag(uid)
        if not tag:
            logger.warning("Unknown tag: %s", uid)
            self._buzzer.error()
            return

        media = self._db.get_media(tag.media_id)
        if not media:
            logger.error("Tag %s points to missing media %d", uid, tag.media_id)
            self._buzzer.error()
            return

        # Check limits for video
        self._state = PlaybackState.CHECK_LIMITS
        self._was_last_video = False

        if media.media_type == MediaType.VIDEO:
            stats = self._db.get_today_video_stats()
            settings = self._db.get_all_settings()
            max_count = int(settings.get("daily_video_limit_count", "5"))
            max_minutes = int(settings.get("daily_video_limit_minutes", "60"))

            result = check_video_limit(
                stats, max_count, max_minutes, media.duration_s or 0
            )

            if not result.allowed:
                logger.info("Video limit reached: %s", result.reason)
                self._buzzer.all_done()
                self._leds.all_done_feedback()
                self._state = PlaybackState.IDLE
                return

            if result.is_last:
                logger.info("This is the last allowed video")
                self._was_last_video = True
                self._buzzer.last_video_warning()
                self._leds.last_video_warning()

        # Load and play
        self._state = PlaybackState.LOADING
        self._buzzer.scan_confirm()
        self._leds.scan_feedback()

        # Determine file path
        if media.media_type == MediaType.VIDEO:
            filepath = VIDEO_DIR / media.filename
        else:
            filepath = AUDIO_DIR / media.filename

        if not filepath.exists():
            logger.error("Media file not found: %s", filepath)
            self._buzzer.error()
            self._state = PlaybackState.IDLE
            self._leds.idle()
            return

        # Log playback start
        self._current_media_id = media.id
        self._current_tag_uid = uid
        self._current_log_id = self._db.log_playback_start(media.id, uid)

        # Start playing
        self._state = PlaybackState.PLAYING
        self._leds.playing_animation()
        self._player.play(str(filepath), media.media_type)

    def _on_playback_end(self):
        """Called by player when playback ends naturally."""
        with self._lock:
            if self._state != PlaybackState.PLAYING:
                return

            self._state = PlaybackState.FINISHED
            logger.info("Playback finished")

            # Log completion
            if self._current_log_id:
                self._db.log_playback_end(self._current_log_id, completed=True)

            # Check if this was the last video
            if self._was_last_video:
                self._buzzer.all_done()
                self._leds.all_done_feedback()
            else:
                self._leds.off()

            self._cleanup_state()

    def on_play_pause(self):
        """Called by button thread on play/pause press."""
        with self._lock:
            if self._state == PlaybackState.PLAYING:
                self._player.pause_toggle()

    def on_stop(self):
        """Called by button thread on stop press."""
        with self._lock:
            if self._state == PlaybackState.PLAYING:
                logger.info("Stop button pressed")
                self._player.stop()

                if self._current_log_id:
                    self._db.log_playback_end(self._current_log_id, completed=False)

                self._leds.off()
                self._cleanup_state()

    def _cleanup_state(self):
        self._current_log_id = None
        self._current_media_id = None
        self._current_tag_uid = None
        self._was_last_video = False
        self._state = PlaybackState.IDLE
        self._leds.idle()

    def get_status(self) -> dict:
        """Get current status for the web UI."""
        status = {
            "state": self._state.value,
            "register_mode": self._register_mode,
            "last_scanned_uid": self._last_scanned_uid,
        }
        if self._current_media_id:
            media = self._db.get_media(self._current_media_id)
            if media:
                status["now_playing"] = {
                    "title": media.title,
                    "media_type": media.media_type.value,
                    "thumbnail": media.thumbnail,
                }
        stats = self._db.get_today_video_stats()
        settings = self._db.get_all_settings()
        status["video_stats"] = {
            "count": stats.count,
            "total_minutes": round(stats.total_minutes, 1),
            "limit_count": int(settings.get("daily_video_limit_count", "5")),
            "limit_minutes": int(settings.get("daily_video_limit_minutes", "60")),
        }
        return status

    def cleanup(self):
        self._player.stop()
        self._player.cleanup()
        self._leds.off()
        self._leds.cleanup()
        self._buzzer.cleanup()
