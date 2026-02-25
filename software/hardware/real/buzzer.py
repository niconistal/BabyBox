import time

import RPi.GPIO as GPIO

from software.config import GPIO_BUZZER
from software.hardware.base import Buzzer


class PiBuzzer(Buzzer):
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GPIO_BUZZER, GPIO.OUT)
        self._pwm = GPIO.PWM(GPIO_BUZZER, 440)

    def _tone(self, freq, duration):
        self._pwm.ChangeFrequency(freq)
        self._pwm.start(50)
        time.sleep(duration)
        self._pwm.stop()

    def _rest(self, duration):
        time.sleep(duration)

    def scan_confirm(self):
        self._tone(1000, 0.08)
        self._rest(0.03)
        self._tone(1500, 0.08)

    def last_video_warning(self):
        # Gentle ascending tone
        for freq in [523, 659, 784]:  # C5, E5, G5
            self._tone(freq, 0.15)
            self._rest(0.05)

    def all_done(self):
        # Calm descending melody
        for freq in [784, 659, 523, 392]:  # G5, E5, C5, G4
            self._tone(freq, 0.2)
            self._rest(0.05)

    def error(self):
        self._tone(200, 0.15)
        self._rest(0.05)
        self._tone(200, 0.15)

    def cleanup(self):
        self._pwm.stop()
