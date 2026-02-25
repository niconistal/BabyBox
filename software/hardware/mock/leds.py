import logging

from software.hardware.base import LEDStrip

logger = logging.getLogger(__name__)


class MockLEDStrip(LEDStrip):
    def scan_feedback(self):
        logger.info("[MockLED] Scan feedback flash")

    def playing_animation(self):
        logger.info("[MockLED] Playing animation started")

    def last_video_warning(self):
        logger.info("[MockLED] Last video warning (yellow pulse)")

    def all_done_feedback(self):
        logger.info("[MockLED] All done feedback (red pulse)")

    def idle(self):
        logger.info("[MockLED] Idle glow")

    def off(self):
        logger.info("[MockLED] Off")

    def cleanup(self):
        pass
