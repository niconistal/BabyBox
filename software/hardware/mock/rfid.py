import logging
import threading
from typing import Optional

from software.hardware.base import RFIDReader

logger = logging.getLogger(__name__)


class MockRFIDReader(RFIDReader):
    """Mock RFID reader. Set `next_uid` from tests or web UI to simulate a scan."""

    def __init__(self):
        self._next_uid: Optional[str] = None
        self._lock = threading.Lock()

    def set_next_uid(self, uid: str):
        with self._lock:
            self._next_uid = uid

    def read_uid(self) -> Optional[str]:
        with self._lock:
            uid = self._next_uid
            self._next_uid = None
        if uid:
            logger.info("[MockRFID] Read UID: %s", uid)
        return uid

    def cleanup(self):
        pass
