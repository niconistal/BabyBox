from software.models import Media, MediaType, Tag


def test_add_and_get_media(db):
    media = Media(
        id=None, title="My Song", filename="song.mp3",
        media_type=MediaType.AUDIO, duration_s=120,
    )
    mid = db.add_media(media)
    assert mid > 0

    fetched = db.get_media(mid)
    assert fetched is not None
    assert fetched.title == "My Song"
    assert fetched.media_type == MediaType.AUDIO


def test_get_all_media(db, sample_media):
    all_media = db.get_all_media()
    assert len(all_media) == 2


def test_delete_media(db, sample_media):
    db.delete_media(sample_media["audio_id"])
    assert db.get_media(sample_media["audio_id"]) is None
    assert len(db.get_all_media()) == 1


def test_add_and_get_tag(db, sample_media):
    tag = Tag(uid="AABBCCDD", media_id=sample_media["audio_id"], label="Dino")
    db.add_tag(tag)

    fetched = db.get_tag("AABBCCDD")
    assert fetched is not None
    assert fetched.label == "Dino"
    assert fetched.media_id == sample_media["audio_id"]


def test_delete_tag(db, sample_media):
    tag = Tag(uid="AABBCCDD", media_id=sample_media["audio_id"])
    db.add_tag(tag)
    db.delete_tag("AABBCCDD")
    assert db.get_tag("AABBCCDD") is None


def test_playback_log(db, sample_media):
    log_id = db.log_playback_start(sample_media["video_id"], "AABB")
    assert log_id > 0

    db.log_playback_end(log_id, completed=True)
    history = db.get_playback_history()
    assert len(history) == 1
    assert history[0]["completed"] == 1


def test_video_stats(db, sample_media):
    # Initially no video playback
    stats = db.get_today_video_stats()
    assert stats.count == 0
    assert stats.total_minutes == 0.0

    # Log a completed video
    log_id = db.log_playback_start(sample_media["video_id"])
    db.log_playback_end(log_id, completed=True)

    stats = db.get_today_video_stats()
    assert stats.count == 1


def test_settings(db):
    # Default settings seeded
    assert db.get_setting("daily_video_limit_count") == "5"

    db.set_setting("daily_video_limit_count", "10")
    assert db.get_setting("daily_video_limit_count") == "10"

    all_s = db.get_all_settings()
    assert "daily_video_limit_count" in all_s


def test_delete_media_cascades_tags(db, sample_media):
    tag = Tag(uid="XXXX", media_id=sample_media["audio_id"])
    db.add_tag(tag)
    db.delete_media(sample_media["audio_id"])
    assert db.get_tag("XXXX") is None
