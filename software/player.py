import logging
import threading
from pathlib import Path
from typing import Callable, Optional

from software.config import IS_PI, MPV_AUDIO_DEVICE
from software.models import MediaType

logger = logging.getLogger(__name__)


class Player:
    def __init__(self, on_playback_end: Optional[Callable] = None, volume: int = 80):
        self._on_playback_end = on_playback_end
        self._mpv = None
        self._lock = threading.Lock()
        self._playing = False
        self._volume = self._clamp(volume)

    @staticmethod
    def _clamp(level: int) -> int:
        return max(0, min(100, int(level)))

    def _ensure_mpv(self):
        if self._mpv is not None:
            return
        try:
            import mpv
            kwargs = {
                "audio_device": MPV_AUDIO_DEVICE,
                "volume": self._volume,
                "input_default_bindings": False,
                "input_vo_keyboard": False,
            }
            if IS_PI:
                kwargs["vo"] = "gpu"
                kwargs["hwdec"] = "auto"
            else:
                kwargs["vo"] = "null"  # No video output in dev
                kwargs["vid"] = "no"

            self._mpv = mpv.MPV(**kwargs)

            @self._mpv.event_callback("end-file")
            def _on_end(event):
                logger.info("mpv end-file event: %s", event)
                self._playing = False
                if self._on_playback_end:
                    self._on_playback_end()

        except ImportError:
            logger.warning("python-mpv not available, using stub player")
            self._mpv = _StubMPV(self._on_playback_end)

    def play(self, filepath: str, media_type: MediaType):
        with self._lock:
            self._ensure_mpv()
            logger.info("Playing: %s (%s)", filepath, media_type.value)
            self._playing = True

            if isinstance(self._mpv, _StubMPV):
                self._mpv.play(filepath)
                return

            # For video, enable video output; for audio, disable it
            if media_type == MediaType.VIDEO:
                self._mpv["vid"] = "auto"
                if IS_PI:
                    self._mpv["vo"] = "gpu"
            else:
                self._mpv["vid"] = "no"

            self._mpv.play(filepath)

    def stop(self):
        with self._lock:
            if self._mpv and self._playing:
                logger.info("Stopping playback")
                if isinstance(self._mpv, _StubMPV):
                    self._mpv.stop()
                else:
                    self._mpv.stop()
                self._playing = False

    def pause_toggle(self):
        with self._lock:
            if self._mpv and self._playing and not isinstance(self._mpv, _StubMPV):
                self._mpv.pause = not self._mpv.pause
                logger.info("Pause toggled: %s", self._mpv.pause)

    def set_volume(self, level: int):
        """Set output volume (0-100). Applies live and to future playback."""
        with self._lock:
            self._volume = self._clamp(level)
            if self._mpv and not isinstance(self._mpv, _StubMPV):
                self._mpv.volume = self._volume
            logger.info("Volume set to %d", self._volume)

    @property
    def volume(self) -> int:
        return self._volume

    @property
    def is_playing(self) -> bool:
        return self._playing

    def cleanup(self):
        with self._lock:
            if self._mpv and not isinstance(self._mpv, _StubMPV):
                self._mpv.terminate()
            self._mpv = None


class _StubMPV:
    """Stub player when mpv is not available (dev without python-mpv)."""

    def __init__(self, on_end: Optional[Callable] = None):
        self._on_end = on_end
        self._timer = None

    def play(self, filepath: str):
        logger.info("[StubMPV] Playing: %s (will end in 3s)", filepath)
        # Simulate short playback
        self._timer = threading.Timer(3.0, self._finish)
        self._timer.daemon = True
        self._timer.start()

    def _finish(self):
        logger.info("[StubMPV] Playback finished")
        if self._on_end:
            self._on_end()

    def stop(self):
        if self._timer:
            self._timer.cancel()
        logger.info("[StubMPV] Stopped")
