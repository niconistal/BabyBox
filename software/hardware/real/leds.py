import threading
import time

from rpi_ws281x import Color, PixelStrip

from software.config import GPIO_LED_DIN, LED_BRIGHTNESS, LED_COUNT
from software.hardware.base import LEDStrip

LED_FREQ_HZ = 800000
LED_DMA = 10
LED_INVERT = False
LED_CHANNEL = 0


class PiLEDStrip(LEDStrip):
    def __init__(self):
        self._strip = PixelStrip(
            LED_COUNT, GPIO_LED_DIN, LED_FREQ_HZ, LED_DMA,
            LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL,
        )
        self._strip.begin()
        self._stop_event = threading.Event()
        self._anim_thread = None

    def _stop_animation(self):
        self._stop_event.set()
        if self._anim_thread and self._anim_thread.is_alive():
            self._anim_thread.join(timeout=1.0)
        self._stop_event.clear()

    def _start_animation(self, target):
        self._stop_animation()
        self._anim_thread = threading.Thread(target=target, daemon=True)
        self._anim_thread.start()

    def _fill(self, color):
        for i in range(self._strip.numPixels()):
            self._strip.setPixelColor(i, color)
        self._strip.show()

    def _pulse(self, r, g, b, count=3, period=0.5):
        for _ in range(count):
            if self._stop_event.is_set():
                return
            # Fade in
            for step in range(0, LED_BRIGHTNESS, 8):
                if self._stop_event.is_set():
                    return
                scale = step / LED_BRIGHTNESS
                self._fill(Color(int(r * scale), int(g * scale), int(b * scale)))
                time.sleep(period / (LED_BRIGHTNESS // 4))
            # Fade out
            for step in range(LED_BRIGHTNESS, 0, -8):
                if self._stop_event.is_set():
                    return
                scale = step / LED_BRIGHTNESS
                self._fill(Color(int(r * scale), int(g * scale), int(b * scale)))
                time.sleep(period / (LED_BRIGHTNESS // 4))
        self._fill(Color(0, 0, 0))

    def scan_feedback(self):
        self._stop_animation()
        self._fill(Color(0, 150, 255))
        time.sleep(0.15)
        self._fill(Color(0, 0, 0))

    def playing_animation(self):
        def _breathe():
            while not self._stop_event.is_set():
                self._pulse(0, 80, 200, count=1, period=1.5)
                if not self._stop_event.is_set():
                    time.sleep(0.3)
        self._start_animation(_breathe)

    def last_video_warning(self):
        self._stop_animation()
        self._pulse(255, 200, 0, count=3, period=0.4)

    def all_done_feedback(self):
        self._stop_animation()
        self._pulse(255, 0, 0, count=3, period=0.5)

    def idle(self):
        self._stop_animation()
        self._fill(Color(5, 5, 10))

    def off(self):
        self._stop_animation()
        self._fill(Color(0, 0, 0))

    def cleanup(self):
        self.off()
