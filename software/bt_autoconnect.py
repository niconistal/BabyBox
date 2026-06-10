"""Boot-time auto-connect for the saved Bluetooth speaker.

Run by bt-connect.service. Retries for a couple of minutes because the
speaker may power on after the Pi, and WiFi/BT coexistence on the
Zero 2 W's shared radio can make early attempts time out.
"""
import logging
import sys

from software import bluetooth
from software.db import Database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("bt-autoconnect")


def main() -> int:
    mac = Database().get_setting("bt_speaker_mac")
    if not mac:
        logger.info("No speaker configured; nothing to do")
        return 0
    logger.info("Connecting saved speaker %s ...", mac)
    if bluetooth.connect_saved_speaker(mac, attempts=8, delay=15):
        logger.info("Speaker %s connected", mac)
    else:
        logger.warning(
            "Could not connect %s; audio falls back to HDMI until it succeeds",
            mac,
        )
    return 0  # never fail the unit — the speaker may simply be off


if __name__ == "__main__":
    sys.exit(main())
