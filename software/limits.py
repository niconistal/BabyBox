from software.models import VideoStats


class LimitResult:
    __slots__ = ("allowed", "is_last", "reason")

    def __init__(self, allowed: bool, is_last: bool = False, reason: str = ""):
        self.allowed = allowed
        self.is_last = is_last
        self.reason = reason


def check_video_limit(
    stats: VideoStats,
    max_count: int,
    max_minutes: int,
    video_duration_s: int = 0,
) -> LimitResult:
    """Check if another video is allowed under the daily limits.

    Returns LimitResult with:
      - allowed: True if the video can play
      - is_last: True if this would be the last allowed video
      - reason: Human-readable explanation if denied
    """
    # Check count limit
    if stats.count >= max_count:
        return LimitResult(False, reason=f"Video limit reached ({max_count} today)")

    # Check time limit
    if stats.total_minutes >= max_minutes:
        return LimitResult(
            False, reason=f"Video time limit reached ({max_minutes} min today)"
        )

    # Would this video push over the time limit?
    projected_minutes = stats.total_minutes + (video_duration_s / 60.0)

    # Is this the last by count?
    last_by_count = (stats.count + 1) >= max_count

    # Is this the last by time? (projected time would exceed limit)
    last_by_time = projected_minutes >= max_minutes

    is_last = last_by_count or last_by_time

    return LimitResult(allowed=True, is_last=is_last)
