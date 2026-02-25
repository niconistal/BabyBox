import os
from pathlib import Path

# Environment: "dev" for mock hardware, "pi" for real Pi hardware
ENV = os.getenv("BABYBOX_ENV", "pi")
IS_PI = ENV != "dev"

# Base paths
BASE_DIR = Path(os.getenv("BABYBOX_DATA_DIR", "/home/pi/babybox"))
MEDIA_DIR = BASE_DIR / "media"
AUDIO_DIR = MEDIA_DIR / "audio"
VIDEO_DIR = MEDIA_DIR / "video"
THUMBNAIL_DIR = MEDIA_DIR / "thumbnails"
DB_PATH = BASE_DIR / "babybox.db"

# GPIO pins
GPIO_RFID_RST = 25
GPIO_RFID_SDA = 8  # CE0
GPIO_LED_DIN = 18  # PWM0
GPIO_BUZZER = 12  # PWM1
GPIO_BTN_PLAY_PAUSE = 17
GPIO_BTN_STOP = 27

# LED strip
LED_COUNT = 8
LED_BRIGHTNESS = 128  # 0-255

# RFID
RFID_POLL_INTERVAL = 0.2  # seconds
RFID_DEDUP_WINDOW = 2.0  # ignore same UID within this window

# Button debounce
BUTTON_POLL_INTERVAL = 0.05  # seconds
BUTTON_DEBOUNCE_MS = 200

# Defaults for settings
DEFAULT_SETTINGS = {
    "daily_video_limit_count": "5",
    "daily_video_limit_minutes": "60",
    "limit_reset_hour": "6",
    "bt_speaker_mac": "",
}

# Web server
WEB_HOST = "0.0.0.0"
WEB_PORT = 5000

# mpv config
MPV_AUDIO_DEVICE = "pulse"


def ensure_dirs():
    """Create media directories if they don't exist."""
    for d in (AUDIO_DIR, VIDEO_DIR, THUMBNAIL_DIR):
        d.mkdir(parents=True, exist_ok=True)
