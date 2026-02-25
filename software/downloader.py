import json
import logging
import subprocess
import threading
import uuid
from pathlib import Path
from typing import Optional

from software.config import AUDIO_DIR, THUMBNAIL_DIR, VIDEO_DIR
from software.db import Database
from software.models import DownloadJob, DownloadStatus, Media, MediaType

logger = logging.getLogger(__name__)

# In-memory job tracker
_jobs: dict[str, DownloadJob] = {}
_jobs_lock = threading.Lock()


def get_job(job_id: str) -> Optional[DownloadJob]:
    with _jobs_lock:
        return _jobs.get(job_id)


def fetch_metadata(url: str) -> dict:
    """Fetch video metadata without downloading."""
    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-download", url],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())
        return json.loads(result.stdout)
    except FileNotFoundError:
        raise RuntimeError("yt-dlp not installed")


def start_download(url: str, media_type: MediaType, db: Database) -> str:
    """Start a background download. Returns job ID."""
    job_id = uuid.uuid4().hex[:8]
    job = DownloadJob(id=job_id, url=url, media_type=media_type)

    with _jobs_lock:
        _jobs[job_id] = job

    thread = threading.Thread(
        target=_download_worker, args=(job, db), daemon=True
    )
    thread.start()
    return job_id


def _download_worker(job: DownloadJob, db: Database):
    try:
        job.status = DownloadStatus.DOWNLOADING

        # Fetch metadata first
        meta = fetch_metadata(job.url)
        job.title = meta.get("title", "Unknown")
        duration = meta.get("duration")

        # Build output template
        safe_id = meta.get("id", job.id)
        if job.media_type == MediaType.VIDEO:
            out_dir = VIDEO_DIR
            ext = "mp4"
            format_arg = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best"
        else:
            out_dir = AUDIO_DIR
            ext = "mp3"
            format_arg = "bestaudio/best"

        out_path = out_dir / f"{safe_id}.{ext}"
        thumb_path = THUMBNAIL_DIR / f"{safe_id}.jpg"

        cmd = [
            "yt-dlp",
            "-f", format_arg,
            "--newline",
            "--write-thumbnail",
            "--convert-thumbnails", "jpg",
            "-o", str(out_path),
            "--paths", f"thumbnail:{THUMBNAIL_DIR}",
            "-o", f"thumbnail:{safe_id}",
        ]

        if job.media_type == MediaType.AUDIO:
            cmd += ["--extract-audio", "--audio-format", "mp3"]

        cmd.append(job.url)

        logger.info("Running: %s", " ".join(cmd))
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True,
        )

        for line in proc.stdout:
            line = line.strip()
            if "[download]" in line and "%" in line:
                try:
                    pct = line.split("%")[0].split()[-1]
                    job.progress = float(pct)
                except (ValueError, IndexError):
                    pass

        proc.wait()

        if proc.returncode != 0:
            raise RuntimeError(f"yt-dlp exited with code {proc.returncode}")

        # Find the actual output file (yt-dlp may have merged)
        actual_file = _find_output_file(out_dir, safe_id, ext)
        if not actual_file:
            raise RuntimeError(f"Output file not found for {safe_id}")

        # Find thumbnail
        actual_thumb = None
        for candidate in THUMBNAIL_DIR.glob(f"{safe_id}*"):
            actual_thumb = str(candidate.name)
            break

        # Save to database
        media = Media(
            id=None,
            title=job.title,
            filename=str(actual_file.name),
            media_type=job.media_type,
            source_url=job.url,
            thumbnail=actual_thumb,
            duration_s=int(duration) if duration else None,
        )
        media_id = db.add_media(media)

        job.media_id = media_id
        job.progress = 100.0
        job.status = DownloadStatus.COMPLETE
        logger.info("Download complete: %s -> media_id=%d", job.title, media_id)

    except Exception as e:
        logger.error("Download failed: %s", e)
        job.status = DownloadStatus.FAILED
        job.error = str(e)


def _find_output_file(directory: Path, stem: str, ext: str) -> Optional[Path]:
    """Find output file by stem, handling yt-dlp naming variations."""
    # Exact match
    exact = directory / f"{stem}.{ext}"
    if exact.exists():
        return exact
    # Glob for variations
    for f in directory.glob(f"{stem}*"):
        return f
    return None
