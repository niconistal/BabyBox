import time
from typing import Optional

import RPi.GPIO as GPIO
from mfrc522 import MFRC522

from software.config import GPIO_RFID_RST
from software.hardware.base import RFIDReader


class PiRFIDReader(RFIDReader):
    def __init__(self, dedup_window: float = 2.0):
        # Force BCM pin numbering for the whole app. The buzzer and buttons
        # use BCM pin numbers (from config), and RPi.GPIO refuses to mix BOARD
        # and BCM. mfrc522's SimpleMFRC522 would otherwise default to BOARD
        # mode, so we drive MFRC522 directly and pass the RST pin in BCM. (In
        # BCM mode mfrc522 would wrongly default RST to BCM 15; our hardware
        # wires it to GPIO_RFID_RST.)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self._reader = MFRC522(pin_rst=GPIO_RFID_RST)
        self._dedup_window = dedup_window
        self._last_uid = None
        self._last_time = 0.0

    def _read_uid_num(self) -> Optional[int]:
        status, _ = self._reader.MFRC522_Request(self._reader.PICC_REQIDL)
        if status != self._reader.MI_OK:
            return None
        status, uid = self._reader.MFRC522_Anticoll()
        if status != self._reader.MI_OK:
            return None
        num = 0
        for i in range(5):
            num = num * 256 + uid[i]
        return num

    def read_uid(self) -> Optional[str]:
        uid = self._read_uid_num()
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
        GPIO.cleanup()
