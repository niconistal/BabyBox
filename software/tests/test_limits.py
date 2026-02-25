from software.limits import check_video_limit
from software.models import VideoStats


def test_allowed_under_limits():
    stats = VideoStats(count=2, total_minutes=20.0)
    result = check_video_limit(stats, max_count=5, max_minutes=60, video_duration_s=300)
    assert result.allowed is True
    assert result.is_last is False


def test_denied_at_count_limit():
    stats = VideoStats(count=5, total_minutes=40.0)
    result = check_video_limit(stats, max_count=5, max_minutes=60)
    assert result.allowed is False
    assert "limit reached" in result.reason.lower()


def test_denied_at_time_limit():
    stats = VideoStats(count=3, total_minutes=60.0)
    result = check_video_limit(stats, max_count=5, max_minutes=60)
    assert result.allowed is False


def test_last_by_count():
    stats = VideoStats(count=4, total_minutes=30.0)
    result = check_video_limit(stats, max_count=5, max_minutes=60, video_duration_s=300)
    assert result.allowed is True
    assert result.is_last is True


def test_last_by_time():
    stats = VideoStats(count=2, total_minutes=55.0)
    result = check_video_limit(stats, max_count=5, max_minutes=60, video_duration_s=360)
    assert result.allowed is True
    assert result.is_last is True


def test_not_last():
    stats = VideoStats(count=1, total_minutes=10.0)
    result = check_video_limit(stats, max_count=5, max_minutes=60, video_duration_s=180)
    assert result.allowed is True
    assert result.is_last is False
