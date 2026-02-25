import logging
import threading
from typing import Optional

from software.hardware.base import ButtonHandler

logger = logging.getLogger(__name__)


class MockButtonHandler(ButtonHandler):
    """Mock buttons. Set `next_button` from tests or web UI to simulate presses."""

    def __init__(self):
        self._next_button: Optional[str] = None
        self._lock = threading.Lock()

    def set_next_button(self, button: str):
        with self._lock:
            self._next_button = button

    def poll(self) -> Optional[str]:
        with self._lock:
            btn = self._next_button
            self._next_button = None
        if btn:
            logger.info("[MockButton] %s pressed", btn)
        return btn

    def cleanup(self):
        pass
