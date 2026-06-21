import os
import uuid
import yt_dlp
from enum import Enum


DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


class DownloadStatus(str, Enum):
    pending = "pending"
    downloading = "downloading"
    completed = "completed"
    failed = "failed"


downloads: dict[str, dict] = {}


def get_output_path(filename: str) -> str:
    return os.path.join(DOWNLOAD_DIR, filename)


def download_video(url: str) -> dict:
    task_id = str(uuid.uuid4())[:8]
    downloads[task_id] = {"status": DownloadStatus.downloading, "file": None}

    try:
        ydl_opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": get_output_path(f"%(title)s.%(ext)s"),
            "restrictfilenames": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if not filename.endswith(".mp4"):
                filename = filename.rsplit(".", 1)[0] + ".mp4"
            downloads[task_id] = {"status": DownloadStatus.completed, "file": filename}
    except Exception as e:
        downloads[task_id] = {"status": DownloadStatus.failed, "error": str(e)}

    return {"task_id": task_id, **downloads[task_id]}


def download_audio(url: str) -> dict:
    task_id = str(uuid.uuid4())[:8]
    downloads[task_id] = {"status": DownloadStatus.downloading, "file": None}

    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": get_output_path(f"%(title)s.%(ext)s"),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "restrictfilenames": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            filename = filename.rsplit(".", 1)[0] + ".mp3"
            downloads[task_id] = {"status": DownloadStatus.completed, "file": filename}
    except Exception as e:
        downloads[task_id] = {"status": DownloadStatus.failed, "error": str(e)}

    return {"task_id": task_id, **downloads[task_id]}
