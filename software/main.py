import logging
import signal
import threading
import time

from software import bluetooth
from software.config import (
    BUTTON_POLL_INTERVAL,
    RFID_POLL_INTERVAL,
    WEB_HOST,
    WEB_PORT,
    ensure_dirs,
)
from software.controller import Controller
from software.db import Database
from software.hardware.factory import create_all
from software.player import Player
from software.web.app import create_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("babybox")

_shutdown = threading.Event()


def rfid_loop(rfid, controller):
    logger.info("RFID thread started")
    while not _shutdown.is_set():
        uid = rfid.read_uid()
        if uid:
            controller.on_tag_scanned(uid)
        time.sleep(RFID_POLL_INTERVAL)


def button_loop(buttons, controller):
    logger.info("Button thread started")
    while not _shutdown.is_set():
        action = buttons.poll()
        if action == "play_pause":
            controller.on_play_pause()
        elif action == "stop":
            controller.on_stop()
        time.sleep(BUTTON_POLL_INTERVAL)


def main():
    ensure_dirs()
    db = Database()

    # Try connecting saved Bluetooth speaker
    bt_mac = db.get_setting("bt_speaker_mac")
    if bt_mac:
        logger.info("Connecting Bluetooth speaker: %s", bt_mac)
        threading.Thread(
            target=bluetooth.connect_saved_speaker, args=(bt_mac,), daemon=True
        ).start()

    # Create hardware
    rfid, leds, buzzer, buttons = create_all()

    # Create player and controller
    player = Player()
    controller = Controller(db, player, leds, buzzer)

    # Start RFID thread
    rfid_thread = threading.Thread(
        target=rfid_loop, args=(rfid, controller), daemon=True
    )
    rfid_thread.start()

    # Start button thread
    button_thread = threading.Thread(
        target=button_loop, args=(buttons, controller), daemon=True
    )
    button_thread.start()

    # Start Flask
    app = create_app(db, controller)
    flask_thread = threading.Thread(
        target=lambda: app.run(
            host=WEB_HOST, port=WEB_PORT, use_reloader=False, threaded=True
        ),
        daemon=True,
    )
    flask_thread.start()

    logger.info("BabyBox started — web UI at http://%s:%d", WEB_HOST, WEB_PORT)

    # Signal handling for graceful shutdown
    def handle_signal(signum, frame):
        logger.info("Received signal %d, shutting down...", signum)
        _shutdown.set()

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    # Wait for shutdown
    try:
        signal.pause()
    except AttributeError:
        # Windows fallback
        _shutdown.wait()

    # Cleanup
    logger.info("Cleaning up...")
    controller.cleanup()
    rfid.cleanup()
    buttons.cleanup()
    logger.info("Goodbye!")


if __name__ == "__main__":
    main()
