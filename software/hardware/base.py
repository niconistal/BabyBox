from abc import ABC, abstractmethod
from typing import Callable, Optional


class RFIDReader(ABC):
    @abstractmethod
    def read_uid(self) -> Optional[str]:
        """Non-blocking read. Returns hex UID string or None."""

    @abstractmethod
    def cleanup(self):
        pass


class LEDStrip(ABC):
    @abstractmethod
    def scan_feedback(self):
        """Quick flash on tag scan."""

    @abstractmethod
    def playing_animation(self):
        """Gentle breathing/pulse while playing."""

    @abstractmethod
    def last_video_warning(self):
        """Pulse yellow 3x."""

    @abstractmethod
    def all_done_feedback(self):
        """Pulse red 3x then fade off."""

    @abstractmethod
    def idle(self):
        """Dim idle glow or off."""

    @abstractmethod
    def off(self):
        """All LEDs off."""

    @abstractmethod
    def cleanup(self):
        pass


class Buzzer(ABC):
    @abstractmethod
    def scan_confirm(self):
        """Short beep on successful tag scan."""

    @abstractmethod
    def last_video_warning(self):
        """Gentle ascending tone."""

    @abstractmethod
    def all_done(self):
        """Calm descending melody."""

    @abstractmethod
    def error(self):
        """Short error buzz."""

    @abstractmethod
    def cleanup(self):
        pass


class ButtonHandler(ABC):
    @abstractmethod
    def poll(self) -> Optional[str]:
        """Non-blocking poll. Returns 'play_pause', 'stop', or None."""

    @abstractmethod
    def cleanup(self):
        pass
