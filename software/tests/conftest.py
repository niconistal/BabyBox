import os
import tempfile

import pytest

# Force dev mode before importing anything else
os.environ["BABYBOX_ENV"] = "dev"

from software.db import Database
from software.hardware.mock.buzzer import MockBuzzer
from software.hardware.mock.leds import MockLEDStrip
from software.models import Media, MediaType


@pytest.fixture
def db(tmp_path):
    db_path = tmp_path / "test.db"
    return Database(db_path)


@pytest.fixture
def mock_leds():
    return MockLEDStrip()


@pytest.fixture
def mock_buzzer():
    return MockBuzzer()


@pytest.fixture
def sample_media(db):
    """Insert sample media and return the list."""
    audio = Media(
        id=None, title="Test Song", filename="test.mp3",
        media_type=MediaType.AUDIO, duration_s=180,
    )
    video = Media(
        id=None, title="Test Video", filename="test.mp4",
        media_type=MediaType.VIDEO, duration_s=300,
    )
    audio_id = db.add_media(audio)
    video_id = db.add_media(video)
    return {"audio_id": audio_id, "video_id": video_id}
