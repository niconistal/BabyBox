import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Optional

from software.config import DB_PATH, DEFAULT_SETTINGS
from software.models import Media, MediaType, PlaybackLog, Tag, VideoStats

SCHEMA = """
CREATE TABLE IF NOT EXISTS media (
    id          INTEGER PRIMARY KEY,
    title       TEXT NOT NULL,
    filename    TEXT NOT NULL,
    media_type  TEXT NOT NULL,
    source_url  TEXT,
    thumbnail   TEXT,
    duration_s  INTEGER,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tags (
    uid         TEXT PRIMARY KEY,
    media_id    INTEGER NOT NULL,
    label       TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (media_id) REFERENCES media(id)
);

CREATE TABLE IF NOT EXISTS playback_log (
    id          INTEGER PRIMARY KEY,
    media_id    INTEGER NOT NULL,
    tag_uid     TEXT,
    started_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at    TIMESTAMP,
    completed   BOOLEAN DEFAULT 0,
    FOREIGN KEY (media_id) REFERENCES media(id)
);

CREATE TABLE IF NOT EXISTS settings (
    key         TEXT PRIMARY KEY,
    value       TEXT NOT NULL
);
"""


class Database:
    def __init__(self, db_path=None):
        self._db_path = str(db_path or DB_PATH)
        self._lock = threading.Lock()
        self._local = threading.local()
        self._init_db()

    def _get_conn(self):
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(self._db_path, check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.row_factory = sqlite3.Row
            self._local.conn = conn
        return self._local.conn

    def _init_db(self):
        conn = self._get_conn()
        conn.executescript(SCHEMA)
        # Seed default settings
        for key, value in DEFAULT_SETTINGS.items():
            conn.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )
        conn.commit()

    # -- Media CRUD --

    def add_media(self, media: Media) -> int:
        conn = self._get_conn()
        with self._lock:
            cur = conn.execute(
                "INSERT INTO media (title, filename, media_type, source_url, thumbnail, duration_s) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (media.title, media.filename, media.media_type.value,
                 media.source_url, media.thumbnail, media.duration_s),
            )
            conn.commit()
            return cur.lastrowid

    def get_media(self, media_id: int) -> Optional[Media]:
        row = self._get_conn().execute(
            "SELECT * FROM media WHERE id = ?", (media_id,)
        ).fetchone()
        return self._row_to_media(row) if row else None

    def get_all_media(self) -> list[Media]:
        rows = self._get_conn().execute(
            "SELECT * FROM media ORDER BY created_at DESC"
        ).fetchall()
        return [self._row_to_media(r) for r in rows]

    def delete_media(self, media_id: int):
        conn = self._get_conn()
        with self._lock:
            conn.execute("DELETE FROM tags WHERE media_id = ?", (media_id,))
            conn.execute("DELETE FROM media WHERE id = ?", (media_id,))
            conn.commit()

    @staticmethod
    def _row_to_media(row) -> Media:
        return Media(
            id=row["id"],
            title=row["title"],
            filename=row["filename"],
            media_type=MediaType(row["media_type"]),
            source_url=row["source_url"],
            thumbnail=row["thumbnail"],
            duration_s=row["duration_s"],
            created_at=row["created_at"],
        )

    # -- Tag CRUD --

    def add_tag(self, tag: Tag):
        conn = self._get_conn()
        with self._lock:
            conn.execute(
                "INSERT OR REPLACE INTO tags (uid, media_id, label) VALUES (?, ?, ?)",
                (tag.uid, tag.media_id, tag.label),
            )
            conn.commit()

    def get_tag(self, uid: str) -> Optional[Tag]:
        row = self._get_conn().execute(
            "SELECT * FROM tags WHERE uid = ?", (uid,)
        ).fetchone()
        return self._row_to_tag(row) if row else None

    def get_all_tags(self) -> list[Tag]:
        rows = self._get_conn().execute(
            "SELECT * FROM tags ORDER BY created_at DESC"
        ).fetchall()
        return [self._row_to_tag(r) for r in rows]

    def delete_tag(self, uid: str):
        conn = self._get_conn()
        with self._lock:
            conn.execute("DELETE FROM tags WHERE uid = ?", (uid,))
            conn.commit()

    @staticmethod
    def _row_to_tag(row) -> Tag:
        return Tag(
            uid=row["uid"],
            media_id=row["media_id"],
            label=row["label"],
            created_at=row["created_at"],
        )

    # -- Playback Log --

    def log_playback_start(self, media_id: int, tag_uid: str = None) -> int:
        conn = self._get_conn()
        with self._lock:
            cur = conn.execute(
                "INSERT INTO playback_log (media_id, tag_uid) VALUES (?, ?)",
                (media_id, tag_uid),
            )
            conn.commit()
            return cur.lastrowid

    def log_playback_end(self, log_id: int, completed: bool):
        conn = self._get_conn()
        with self._lock:
            conn.execute(
                "UPDATE playback_log SET ended_at = CURRENT_TIMESTAMP, completed = ? WHERE id = ?",
                (int(completed), log_id),
            )
            conn.commit()

    def get_playback_history(self, limit: int = 50) -> list[dict]:
        rows = self._get_conn().execute(
            "SELECT p.*, m.title, m.media_type FROM playback_log p "
            "JOIN media m ON p.media_id = m.id "
            "ORDER BY p.started_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    # -- Video Stats (for limit enforcement) --

    def get_today_video_stats(self) -> VideoStats:
        reset_hour = int(self.get_setting("limit_reset_hour") or "6")
        now = datetime.now()
        if now.hour < reset_hour:
            reset_time = (now - timedelta(days=1)).replace(
                hour=reset_hour, minute=0, second=0, microsecond=0
            )
        else:
            reset_time = now.replace(
                hour=reset_hour, minute=0, second=0, microsecond=0
            )
        reset_str = reset_time.strftime("%Y-%m-%d %H:%M:%S")

        row = self._get_conn().execute(
            "SELECT COUNT(*) as cnt, COALESCE(SUM(m.duration_s), 0) as total_s "
            "FROM playback_log p JOIN media m ON p.media_id = m.id "
            "WHERE m.media_type = 'video' AND p.completed = 1 "
            "AND p.started_at >= ?",
            (reset_str,),
        ).fetchone()

        return VideoStats(
            count=row["cnt"],
            total_minutes=row["total_s"] / 60.0,
        )

    # -- Settings --

    def get_setting(self, key: str) -> Optional[str]:
        row = self._get_conn().execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else None

    def set_setting(self, key: str, value: str):
        conn = self._get_conn()
        with self._lock:
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )
            conn.commit()

    def get_all_settings(self) -> dict[str, str]:
        rows = self._get_conn().execute("SELECT * FROM settings").fetchall()
        return {r["key"]: r["value"] for r in rows}
