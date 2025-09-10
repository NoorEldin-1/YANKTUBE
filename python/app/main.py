import os
import shutil
import tempfile
import uuid
import zipfile
import asyncio
from pathlib import Path
from typing import Optional
import re
import traceback
import logging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from starlette.middleware.cors import CORSMiddleware
import yt_dlp
from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from starlette.background import BackgroundTask
from fastapi.responses import FileResponse, JSONResponse
from yt_dlp import YoutubeDL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APP_TITLE = "YANKTUBE FastAPI (yt-dlp)"
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title=APP_TITLE)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "Content-Length"],
)


async def cleanup_temp_files(files: list):
    for file_path in files:
        try:
            if file_path and file_path.exists():
                file_path.unlink(missing_ok=True)
                logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning up {file_path}: {e}")


async def delayed_cleanup(playlist_dir: Path, zip_path: Path, delay: int = 300):
    import asyncio

    await asyncio.sleep(delay)
    try:
        if playlist_dir.exists():
            shutil.rmtree(playlist_dir, ignore_errors=True)
            logger.info(f"Cleaned up playlist directory: {playlist_dir}")
        if zip_path.exists():
            zip_path.unlink(missing_ok=True)
            logger.info(f"Cleaned up zip file: {zip_path}")
    except Exception as e:
        logger.error(f"Error in delayed cleanup: {e}")


def sanitize_filename(name: str) -> str:
    illegal = '/\\?%*:|"<>'
    return "".join(c for c in name if c not in illegal).strip()


async def run_extract(url: str, ydl_opts: dict, download: bool = False):
    with YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=download)


async def run_download(urls, ydl_opts: dict):
    with YoutubeDL(ydl_opts) as ydl:
        return ydl.download(urls)


def extract_video_info(url):
    ydl_opts = {"quiet": True, "extract_flat": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "type": "video",
            "title": info.get("title"),
            "duration": info.get("duration"),
            "uploader": info.get("uploader"),
            "id": info.get("id"),
        }


def extract_playlist_info(url):
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "type": "playlist",
            "playlist_name": info.get("title"),
            "playlist_id": info.get("id"),
            "videos": [
                {
                    "title": entry.get("title"),
                    "duration": entry.get("duration"),
                    "uploader": entry.get("uploader"),
                    "id": entry.get("id"),
                }
                for entry in info.get("entries", [])
                if entry
            ],
        }


@app.get("/details")
def get_details(url: str = Query(...)):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if parsed.path.startswith("/playlist") and "list" in query:
        return extract_playlist_info(url)
    if parsed.path.startswith("/watch") and "v" in query:
        clean_query = {"v": query["v"][0]}
        clean_url = urlunparse(parsed._replace(query=urlencode(clean_query)))
        return extract_video_info(clean_url)
    return extract_video_info(url)


@app.get("/download/video")
async def download_video(
    url: str = Query(..., description="YouTube video URL"),
    quality: str = Query("720p", description="Video quality"),
):
    try:
        try:
            quality_value = int(quality.rstrip("p"))
            if quality_value < 144:
                quality_value = 144
            elif quality_value > 4320:
                quality_value = 4320
        except:
            quality_value = 720

        ydl_opts = {
            "format": f"bestvideo[height<={quality_value}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality_value}]/best",
            "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
            "merge_output_format": "mp4",
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            filepath = ydl.prepare_filename(info)
            safe_filename = "".join(
                c for c in info["title"] if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            safe_filename = f"{safe_filename}.mp4"
            return FileResponse(
                filepath,
                media_type="video/mp4",
                filename=safe_filename,
                background=BackgroundTask(
                    lambda: (os.remove(filepath) if os.path.exists(filepath) else None)
                ),
            )
    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=400, detail=f"Download error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/download/audio")
async def download_audio(url: str = Query(...)):
    try:
        ydl_opts = {
            "format": f"bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
            "merge_output_format": "mp4",
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            filepath = ydl.prepare_filename(info)
            safe_filename = "".join(
                c for c in info["title"] if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            safe_filename = f"{safe_filename}.mp3"
            return FileResponse(
                filepath,
                media_type="audio/mpeg",
                filename=safe_filename,
                background=BackgroundTask(
                    lambda: os.remove(filepath) if os.path.exists(filepath) else None
                ),
            )
    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=400, detail=f"Download error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/download/playlist/video")
async def download_playlist_video(
    url: str = Query(...),
    quality: str = Query("720p"),
    background_tasks: BackgroundTasks = None,
):
    try:
        try:
            quality_value = int(quality.rstrip("p"))
            if quality_value < 144:
                quality_value = 144
            elif quality_value > 4320:
                quality_value = 4320
        except:
            quality_value = 720

        temp_dir = tempfile.mkdtemp(prefix="playlist_video_")
        playlist_dir = Path(temp_dir)

        playlist_info = extract_playlist_info(url)
        playlist_name = sanitize_filename(
            playlist_info.get("playlist_name", "playlist")
        )

        ydl_opts = {
            "format": f"bestvideo[height<={quality_value}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality_value}]/best",
            "outtmpl": str(playlist_dir / "%(title)s.%(ext)s"),
            "merge_output_format": "mp4",
            "quiet": True,
            "extract_flat": False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await asyncio.to_thread(ydl.download, [url])

        zip_filename = f"{playlist_name}_videos.zip"
        zip_path = DOWNLOAD_DIR / zip_filename

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            file_count = 0
            for file_path in playlist_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(playlist_dir)
                    zipf.write(file_path, arcname)
                    file_count += 1
                    logger.info(f"Added to zip: {arcname}")
            logger.info(f"Created zip with {file_count} files: {zip_path}")

        if not zip_path.exists():
            raise HTTPException(status_code=500, detail="Failed to create zip file")

        try:
            with zipfile.ZipFile(zip_path, "r") as test_zip:
                test_zip.testzip()
            logger.info(f"Zip file integrity verified: {zip_path}")
        except Exception as e:
            logger.error(f"Zip file integrity check failed: {e}")
            raise HTTPException(status_code=500, detail="Created zip file is corrupted")

        if background_tasks:
            background_tasks.add_task(
                delayed_cleanup, playlist_dir, zip_path, delay=300
            )

        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=zip_filename,
        )
    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=400, detail=f"Download error: {str(e)}")
    except Exception as e:
        logger.error(f"Playlist video download error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/download/playlist/audio")
async def download_playlist_audio(
    url: str = Query(...),
    background_tasks: BackgroundTasks = None,
):
    try:
        temp_dir = tempfile.mkdtemp(prefix="playlist_audio_")
        playlist_dir = Path(temp_dir)

        playlist_info = extract_playlist_info(url)
        playlist_name = sanitize_filename(
            playlist_info.get("playlist_name", "playlist")
        )

        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": str(playlist_dir / "%(title)s.%(ext)s"),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "quiet": True,
            "extract_flat": False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await asyncio.to_thread(ydl.download, [url])

        zip_filename = f"{playlist_name}_audio.zip"
        zip_path = DOWNLOAD_DIR / zip_filename

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            file_count = 0
            for file_path in playlist_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(playlist_dir)
                    zipf.write(file_path, arcname)
                    file_count += 1
                    logger.info(f"Added to zip: {arcname}")
            logger.info(f"Created zip with {file_count} files: {zip_path}")

        if not zip_path.exists():
            raise HTTPException(status_code=500, detail="Failed to create zip file")

        try:
            with zipfile.ZipFile(zip_path, "r") as test_zip:
                test_zip.testzip()
            logger.info(f"Zip file integrity verified: {zip_path}")
        except Exception as e:
            logger.error(f"Zip file integrity check failed: {e}")
            raise HTTPException(status_code=500, detail="Created zip file is corrupted")

        if background_tasks:
            background_tasks.add_task(
                delayed_cleanup, playlist_dir, zip_path, delay=300
            )

        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=zip_filename,
        )
    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=400, detail=f"Download error: {str(e)}")
    except Exception as e:
        logger.error(f"Playlist audio download error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
