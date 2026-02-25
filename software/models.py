from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class MediaType(str, Enum):
    AUDIO = "audio"
    VIDEO = "video"


class DownloadStatus(str, Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETE = "complete"
    FAILED = "failed"


class PlaybackState(str, Enum):
    IDLE = "idle"
    CHECK_LIMITS = "check_limits"
    LOADING = "loading"
    PLAYING = "playing"
    FINISHED = "finished"


@dataclass
class Media:
    id: Optional[int]
    title: str
    filename: str
    media_type: MediaType
    source_url: Optional[str] = None
    thumbnail: Optional[str] = None
    duration_s: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class Tag:
    uid: str
    media_id: int
    label: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class PlaybackLog:
    id: Optional[int]
    media_id: int
    tag_uid: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    completed: bool = False


@dataclass
class DownloadJob:
    id: str
    url: str
    media_type: MediaType
    status: DownloadStatus = DownloadStatus.PENDING
    progress: float = 0.0
    title: Optional[str] = None
    error: Optional[str] = None
    media_id: Optional[int] = None


@dataclass
class VideoStats:
    count: int = 0
    total_minutes: float = 0.0
