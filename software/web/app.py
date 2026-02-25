import logging
import os
import subprocess

from flask import Flask, jsonify, render_template, request

from software import bluetooth, downloader
from software.config import AUDIO_DIR, THUMBNAIL_DIR, VIDEO_DIR, ensure_dirs
from software.controller import Controller
from software.db import Database
from software.models import MediaType, Tag

logger = logging.getLogger(__name__)


def create_app(db: Database, controller: Controller) -> Flask:
    app = Flask(__name__)

    # Serve thumbnail files
    @app.route("/thumbnails/<path:filename>")
    def serve_thumbnail(filename):
        from flask import send_from_directory
        return send_from_directory(str(THUMBNAIL_DIR), filename)

    # -- Pages --

    @app.route("/")
    def dashboard():
        status = controller.get_status()
        return render_template("dashboard.html", status=status)

    @app.route("/library")
    def library():
        media_list = db.get_all_media()
        return render_template("library.html", media=media_list)

    @app.route("/figurines")
    def figurines():
        tags = db.get_all_tags()
        media_list = db.get_all_media()
        # Build tag info with media titles
        tag_info = []
        media_map = {m.id: m for m in media_list}
        for t in tags:
            m = media_map.get(t.media_id)
            tag_info.append({
                "uid": t.uid,
                "label": t.label,
                "media_id": t.media_id,
                "media_title": m.title if m else "Unknown",
            })
        return render_template(
            "figurines.html", tags=tag_info, media=media_list
        )

    @app.route("/settings")
    def settings():
        all_settings = db.get_all_settings()
        return render_template("settings.html", settings=all_settings)

    @app.route("/history")
    def history():
        logs = db.get_playback_history(limit=100)
        return render_template("history.html", logs=logs)

    # -- API: Download --

    @app.route("/api/download", methods=["POST"])
    def api_download():
        data = request.get_json()
        url = data.get("url", "").strip()
        media_type_str = data.get("media_type", "audio")

        if not url:
            return jsonify({"error": "URL is required"}), 400

        try:
            media_type = MediaType(media_type_str)
        except ValueError:
            return jsonify({"error": "Invalid media_type"}), 400

        ensure_dirs()
        job_id = downloader.start_download(url, media_type, db)
        return jsonify({"job_id": job_id})

    @app.route("/api/download/<job_id>")
    def api_download_progress(job_id):
        job = downloader.get_job(job_id)
        if not job:
            return jsonify({"error": "Job not found"}), 404
        return jsonify({
            "status": job.status.value,
            "progress": job.progress,
            "title": job.title,
            "error": job.error,
            "media_id": job.media_id,
        })

    # -- API: Media --

    @app.route("/api/media/<int:media_id>", methods=["DELETE"])
    def api_delete_media(media_id):
        media = db.get_media(media_id)
        if not media:
            return jsonify({"error": "Not found"}), 404

        # Delete file
        if media.media_type == MediaType.VIDEO:
            filepath = VIDEO_DIR / media.filename
        else:
            filepath = AUDIO_DIR / media.filename
        if filepath.exists():
            filepath.unlink()

        # Delete thumbnail
        if media.thumbnail:
            thumb_path = THUMBNAIL_DIR / media.thumbnail
            if thumb_path.exists():
                thumb_path.unlink()

        db.delete_media(media_id)
        return jsonify({"ok": True})

    # -- API: Tags / Figurines --

    @app.route("/api/register-mode", methods=["POST"])
    def api_register_mode():
        data = request.get_json()
        controller.register_mode = data.get("enabled", True)
        return jsonify({"register_mode": controller.register_mode})

    @app.route("/api/scan-tag")
    def api_scan_tag():
        uid = controller.last_scanned_uid
        return jsonify({"uid": uid})

    @app.route("/api/tags", methods=["POST"])
    def api_add_tag():
        data = request.get_json()
        uid = data.get("uid", "").strip()
        media_id = data.get("media_id")
        label = data.get("label", "").strip()

        if not uid or not media_id:
            return jsonify({"error": "uid and media_id required"}), 400

        tag = Tag(uid=uid, media_id=int(media_id), label=label or None)
        db.add_tag(tag)
        controller.register_mode = False
        return jsonify({"ok": True})

    @app.route("/api/tags/<uid>", methods=["DELETE"])
    def api_delete_tag(uid):
        db.delete_tag(uid)
        return jsonify({"ok": True})

    # -- API: Settings --

    @app.route("/api/settings", methods=["POST"])
    def api_update_settings():
        data = request.get_json()
        for key, value in data.items():
            db.set_setting(key, str(value))
        return jsonify({"ok": True})

    # -- API: Bluetooth --

    @app.route("/api/bluetooth/scan", methods=["POST"])
    def api_bt_scan():
        devices = bluetooth.scan_devices()
        return jsonify({"devices": devices})

    @app.route("/api/bluetooth/pair", methods=["POST"])
    def api_bt_pair():
        data = request.get_json()
        mac = data.get("mac", "").strip()
        if not mac:
            return jsonify({"error": "MAC address required"}), 400

        success = bluetooth.pair_and_connect(mac)
        if success:
            bluetooth.set_default_sink(mac)
            db.set_setting("bt_speaker_mac", mac)
            return jsonify({"ok": True})
        return jsonify({"error": "Pairing failed"}), 500

    # -- API: System --

    @app.route("/api/system/shutdown", methods=["POST"])
    def api_shutdown():
        subprocess.Popen(["sudo", "shutdown", "-h", "now"])
        return jsonify({"ok": True})

    @app.route("/api/system/reboot", methods=["POST"])
    def api_reboot():
        subprocess.Popen(["sudo", "reboot"])
        return jsonify({"ok": True})

    # -- API: Status --

    @app.route("/api/status")
    def api_status():
        return jsonify(controller.get_status())

    return app
