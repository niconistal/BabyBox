import logging

from software.hardware.base import Buzzer

logger = logging.getLogger(__name__)


class MockBuzzer(Buzzer):
    def scan_confirm(self):
        logger.info("[MockBuzzer] Scan confirm beep")

    def last_video_warning(self):
        logger.info("[MockBuzzer] Last video warning (ascending)")

    def all_done(self):
        logger.info("[MockBuzzer] All done (descending)")

    def error(self):
        logger.info("[MockBuzzer] Error buzz")

    def cleanup(self):
        pass
