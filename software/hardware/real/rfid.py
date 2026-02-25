import time
from typing import Optional

from mfrc522 import SimpleMFRC522

from software.hardware.base import RFIDReader


class PiRFIDReader(RFIDReader):
    def __init__(self, dedup_window: float = 2.0):
        self._reader = SimpleMFRC522()
        self._dedup_window = dedup_window
        self._last_uid = None
        self._last_time = 0.0

    def read_uid(self) -> Optional[str]:
        uid = self._reader.read_id_no_block()
        if uid is None:
            self._last_uid = None
            return None

        uid_hex = format(uid, "X")
        now = time.monotonic()

        # De-duplicate: ignore same UID within window
        if uid_hex == self._last_uid and (now - self._last_time) < self._dedup_window:
            return None

        self._last_uid = uid_hex
        self._last_time = now
        return uid_hex

    def cleanup(self):
        import RPi.GPIO as GPIO
        GPIO.cleanup()
