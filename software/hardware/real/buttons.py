import time
from typing import Optional

import RPi.GPIO as GPIO

from software.config import BUTTON_DEBOUNCE_MS, GPIO_BTN_PLAY_PAUSE, GPIO_BTN_STOP
from software.hardware.base import ButtonHandler


class PiButtonHandler(ButtonHandler):
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GPIO_BTN_PLAY_PAUSE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(GPIO_BTN_STOP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self._last_press = {GPIO_BTN_PLAY_PAUSE: 0, GPIO_BTN_STOP: 0}

    def poll(self) -> Optional[str]:
        now_ms = time.monotonic() * 1000

        if GPIO.input(GPIO_BTN_PLAY_PAUSE) == GPIO.LOW:
            if (now_ms - self._last_press[GPIO_BTN_PLAY_PAUSE]) > BUTTON_DEBOUNCE_MS:
                self._last_press[GPIO_BTN_PLAY_PAUSE] = now_ms
                return "play_pause"

        if GPIO.input(GPIO_BTN_STOP) == GPIO.LOW:
            if (now_ms - self._last_press[GPIO_BTN_STOP]) > BUTTON_DEBOUNCE_MS:
                self._last_press[GPIO_BTN_STOP] = now_ms
                return "stop"

        return None

    def cleanup(self):
        pass  # GPIO cleanup handled centrally
