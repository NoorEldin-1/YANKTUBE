# main.py
# استيراد مكتبات نظام التشغيل لإدارة الملفات والمجلدات
import os

# استيراد shutil للمساعدة في عمليات الملفات عالية المستوى مثل حذف المجلدات
import shutil

# استيراد tempfile لإنشاء ملفات ومجلدات مؤقتة
import tempfile

# استيراد uuid لإنشاء معرفات فريدة عالميًا (Universal Unique Identifiers)
import uuid

# استيراد zipfile للتعامل مع ملفات ZIP (إنشاء، فك الضغط، الخ.)
import zipfile

# استيراد asyncio لدعم البرمجة المتزامنة (asynchronous programming)
import asyncio

# استيراد Path من pathlib للتعامل مع مسارات الملفات بطريقة موجهة للكائنات (object-oriented)
from pathlib import Path

# استيراد Optional من typing لتحديد أن المتغير يمكن أن يكون له قيمة أو يكون None
from typing import Optional

# استيراد re للتعامل مع التعابير النمطية (regular expressions)
import re

# استيراد traceback للحصول على معلومات تفصيلية عن الأخطاء (stack traces)
import traceback

# استيراد logging لتسجيل رسائل التطبيق (معلومات، تحذيرات، أخطاء)
import logging

# استيراد دوال من urllib.parse لتحليل روابط الويب
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# استيراد yt_dlp، المكتبة الأساسية لتنزيل الفيديوهات
from starlette.middleware.cors import CORSMiddleware
import yt_dlp

# استيراد الفئات والوحدات الرئيسية من FastAPI لبناء الـ API
from fastapi import FastAPI, Query, HTTPException, BackgroundTasks

# استيراد BackgroundTask لتشغيل المهام في الخلفية بعد استجابة الـ API
from starlette.background import BackgroundTask

# استيراد CORSMiddleware للتعامل مع سياسات CORS (Cross-Origin Resource Sharing)
from fastapi.responses import FileResponse, JSONResponse

# استيراد YoutubeDL من yt_dlp لإنشاء كائن مخصص لخيارات التنزيل
from yt_dlp import YoutubeDL

# تهيئة نظام تسجيل الأخطاء (logging) ليعرض الرسائل على مستوى INFO
logging.basicConfig(level=logging.INFO)
# إنشاء كائن logger للاستخدام في جميع أنحاء التطبيق
logger = logging.getLogger(__name__)

# تعريف عنوان التطبيق
APP_TITLE = "YANKTUBE FastAPI (yt-dlp)"
# تعريف مسار مجلد التنزيلات
DOWNLOAD_DIR = Path("downloads")
# إنشاء مجلد التنزيلات إذا لم يكن موجودًا بالفعل
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# إنشاء كائن التطبيق الرئيسي لـ FastAPI
app = FastAPI(title=APP_TITLE)
# إضافة middleware لتمكين سياسة CORS
app.add_middleware(
    # استخدام CORSMiddleware
    CORSMiddleware,
    # السماح بالطلبات من هذين النطاقين (domains) فقط
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    # عدم السماح بإرسال بيانات الاعتماد (credentials)
    allow_credentials=False,
    # السماح بجميع أنواع طلبات HTTP (GET, POST, PUT, DELETE, إلخ.)
    allow_methods=["*"],
    # السماح بجميع ترويسات (headers) الطلب
    allow_headers=["*"],
    # السماح بعرض ترويسات الاستجابة المخصصة هذه للعميل
    expose_headers=["Content-Disposition", "Content-Length"],
)


# دالة لتنظيف الملفات المؤقتة
async def cleanup_temp_files(files: list):
    """Clean up temporary files in the background."""
    # التكرار على قائمة الملفات
    for file_path in files:
        try:
            # التحقق مما إذا كان المسار موجودًا
            if file_path and file_path.exists():
                # حذف الملف
                file_path.unlink(missing_ok=True)
                # تسجيل رسالة تفيد بأن الملف قد تم حذفه
                logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            # تسجيل أي خطأ يحدث أثناء عملية الحذف
            logger.error(f"Error cleaning up {file_path}: {e}")


# دالة لتنظيف المجلدات والملفات المؤقتة بعد تأخير
async def delayed_cleanup(playlist_dir: Path, zip_path: Path, delay: int = 300):
    """Clean up files after a delay to allow download to complete."""
    # استيراد asyncio داخليًا لتجنب أخطاء الاستيراد الدورية
    import asyncio

    # الانتظار لمدة محددة (افتراضيًا 300 ثانية)
    await asyncio.sleep(delay)
    try:
        # التحقق مما إذا كان مجلد قائمة التشغيل موجودًا
        if playlist_dir.exists():
            # حذف المجلد ومحتوياته بالكامل
            shutil.rmtree(playlist_dir, ignore_errors=True)
            # تسجيل رسالة تفيد بأن المجلد قد تم حذفه
            logger.info(f"Cleaned up playlist directory: {playlist_dir}")
        # التحقق مما إذا كان ملف الـ zip موجودًا
        if zip_path.exists():
            # حذف ملف الـ zip
            zip_path.unlink(missing_ok=True)
            # تسجيل رسالة تفيد بأن ملف الـ zip قد تم حذفه
            logger.info(f"Cleaned up zip file: {zip_path}")
    except Exception as e:
        # تسجيل أي خطأ يحدث أثناء عملية الحذف
        logger.error(f"Error in delayed cleanup: {e}")


# دالة لتنظيف اسم الملف من الأحرف غير القانونية
def sanitize_filename(name: str) -> str:
    # تعريف الأحرف غير القانونية في أنظمة التشغيل
    illegal = '/\\?%*:|"<>'
    # إرجاع الاسم بعد حذف الأحرف غير القانونية منه
    return "".join(c for c in name if c not in illegal).strip()


# دالة لتشغيل استخلاص معلومات من yt-dlp بشكل متزامن
async def run_extract(url: str, ydl_opts: dict, download: bool = False):
    # إنشاء كائن YoutubeDL مع الخيارات المحددة
    with YoutubeDL(ydl_opts) as ydl:
        # استخلاص المعلومات من الرابط
        return ydl.extract_info(url, download=download)


# دالة لتشغيل عملية تنزيل yt-dlp بشكل متزامن
async def run_download(urls, ydl_opts: dict):
    # إنشاء كائن YoutubeDL مع الخيارات المحددة
    with YoutubeDL(ydl_opts) as ydl:
        # تنزيل الفيديوهات من الروابط
        return ydl.download(urls)


# دالة لاستخلاص معلومات فيديو واحد
def extract_video_info(url):
    # تعريف خيارات yt-dlp للاستخلاص فقط
    ydl_opts = {"quiet": True, "extract_flat": True}
    # إنشاء كائن YoutubeDL
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # استخلاص المعلومات دون تنزيل الفيديو
        info = ydl.extract_info(url, download=False)
        # إرجاع المعلومات في قاموس (dictionary)
        return {
            "type": "video",
            "title": info.get("title"),
            "duration": info.get("duration"),
            "uploader": info.get("uploader"),
            "id": info.get("id"),
        }


# دالة لاستخلاص معلومات قائمة تشغيل (playlist)
def extract_playlist_info(url):
    # تعريف خيارات yt-dlp للاستخلاص فقط
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
    }
    # إنشاء كائن YoutubeDL
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # استخلاص المعلومات دون تنزيل
        info = ydl.extract_info(url, download=False)
        # إرجاع المعلومات في قاموس
        return {
            "type": "playlist",
            "playlist_name": info.get("title"),
            "playlist_id": info.get("id"),
            "videos": [
                # استخلاص معلومات كل فيديو في القائمة
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


# تعريف نقطة نهاية (endpoint) لـ GET /details
@app.get("/details")
# الدالة التي تُعالج الطلب
def get_details(url: str = Query(...)):
    # تحليل الرابط إلى أجزائه (بروتوكول، مسار، استعلام، إلخ.)
    parsed = urlparse(url)
    # تحليل جزء الاستعلام (query) إلى قاموس
    query = parse_qs(parsed.query)
    # ✅ التحقق مما إذا كان الرابط لقائمة تشغيل كاملة
    if parsed.path.startswith("/playlist") and "list" in query:
        # إذا كان كذلك، استخلاص معلومات القائمة
        return extract_playlist_info(url)

    # ✅ التحقق مما إذا كان الرابط لفيديو واحد (حتى لو كان جزءًا من قائمة تشغيل)
    if parsed.path.startswith("/watch") and "v" in query:
        # تنظيف معلمات الاستعلام، مع الاحتفاظ فقط بمعرف الفيديو 'v'
        clean_query = {"v": query["v"][0]}  # Take just v
        # إعادة بناء الرابط النظيف
        clean_url = urlunparse(parsed._replace(query=urlencode(clean_query)))
        # استخلاص معلومات الفيديو
        return extract_video_info(clean_url)

    # إذا لم تتطابق الشروط السابقة، اعتبره فيديو واحد
    return extract_video_info(url)


# تعريف نقطة نهاية (endpoint) لـ GET /download/video
@app.get("/download/video")
# الدالة التي تُعالج الطلب بشكل متزامن (asynchronously)
async def download_video(
    # تعريف معلمة الرابط (URL) مع وصف
    url: str = Query(..., description="YouTube video URL"),
    # تعريف معلمة الجودة (quality) مع قيمة افتراضية ووصف
    quality: str = Query("720p", description="Video quality"),
):
    try:
        # التحقق من قيمة الجودة
        try:
            # استخراج القيمة العددية من سلسلة الجودة (e.g., "720p" -> 720)
            quality_value = int(quality.rstrip("p"))
            # تحديد الحد الأدنى للجودة
            if quality_value < 144:
                quality_value = 144
            # تحديد الحد الأقصى للجودة
            elif quality_value > 4320:
                quality_value = 4320
        # في حالة فشل التحويل، استخدام قيمة افتراضية
        except:
            quality_value = 720

        # إعداد خيارات yt-dlp
        ydl_opts = {
            # تحديد صيغة التنزيل (أفضل فيديو وصوت)
            "format": f"bestvideo[height<={quality_value}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality_value}]/best",
            # تحديد مسار واسم الملف الناتج
            "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
            # تحديد صيغة الدمج لتكون mp4
            "merge_output_format": "mp4",
            # تشغيل العملية في الوضع الصامت (quiet)
            "quiet": True,
        }

        # بدء عملية التنزيل
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # تشغيل عملية التنزيل في خيط منفصل لتجنب حجب التطبيق
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            # الحصول على المسار النهائي للملف الذي تم تنزيله
            filepath = ydl.prepare_filename(info)

            # الحصول على اسم الملف الآمن للاستخدام في التنزيل
            safe_filename = "".join(
                c for c in info["title"] if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            # إضافة لاحقة mp4 لاسم الملف الآمن
            safe_filename = f"{safe_filename}.mp4"

            # إرجاع استجابة ملف (FileResponse)
            return FileResponse(
                # المسار إلى الملف
                filepath,
                # نوع وسائط الملف
                media_type="video/mp4",
                # اسم الملف الذي سيراه المستخدم
                filename=safe_filename,
                # مهمة خلفية لحذف الملف بعد إرساله
                background=BackgroundTask(
                    lambda: (os.remove(filepath) if os.path.exists(filepath) else None)
                ),
            )

    # التعامل مع أخطاء التنزيل المحددة من yt_dlp
    except yt_dlp.utils.DownloadError as e:
        # إرجاع خطأ HTTP 400
        raise HTTPException(status_code=400, detail=f"Download error: {str(e)}")
    # التعامل مع أي أخطاء أخرى غير متوقعة
    except Exception as e:
        # إرجاع خطأ HTTP 500
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# تعريف نقطة نهاية لـ GET /download/audio
@app.get("/download/audio")
# الدالة التي تُعالج الطلب بشكل متزامن
async def download_audio(url: str = Query(...)):
    try:

        # إعداد خيارات yt-dlp
        ydl_opts = {
            # تحديد أفضل صيغة صوت (m4a أو غيرها)
            "format": f"bestaudio[ext=m4a]/bestaudio/best",
            # تحديد مسار واسم الملف الناتج
            "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
            # تحديد صيغة الدمج لتكون mp4
            "merge_output_format": "mp4",
            # تشغيل العملية في الوضع الصامت
            "quiet": True,
        }

        # بدء عملية التنزيل
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # تشغيل عملية التنزيل في خيط منفصل
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            # الحصول على المسار النهائي للملف
            filepath = ydl.prepare_filename(info)

            # الحصول على اسم الملف الآمن
            safe_filename = "".join(
                c for c in info["title"] if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            # إضافة لاحقة mp3 لاسم الملف الآمن
            safe_filename = f"{safe_filename}.mp3"

            # إرجاع استجابة ملف
            return FileResponse(
                # المسار إلى الملف
                filepath,
                # نوع وسائط الملف
                media_type="audio/mpeg",
                # اسم الملف الذي سيراه المستخدم
                filename=safe_filename,
                # مهمة خلفية لحذف الملف بعد إرساله
                background=BackgroundTask(
                    lambda: os.remove(filepath) if os.path.exists(filepath) else None
                ),
            )

    # التعامل مع أخطاء التنزيل المحددة من yt_dlp
    except yt_dlp.utils.DownloadError as e:
        # إرجاع خطأ HTTP 400
        raise HTTPException(status_code=400, detail=f"Download error: {str(e)}")
    # التعامل مع أي أخطاء أخرى غير متوقعة
    except Exception as e:
        # إرجاع خطأ HTTP 500
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# تعريف نقطة نهاية لـ GET /download/playlist/video
@app.get("/download/playlist/video")
# الدالة التي تُعالج الطلب بشكل متزامن
async def download_playlist_video(
    # تعريف معلمة الرابط
    url: str = Query(...),
    # تعريف معلمة الجودة
    quality: str = Query("720p"),
    # إضافة BackgroundTasks لإدارة المهام الخلفية
    background_tasks: BackgroundTasks = None,
):
    try:
        # التحقق من قيمة الجودة
        try:
            # استخراج القيمة العددية من سلسلة الجودة
            quality_value = int(quality.rstrip("p"))
            # تحديد الحد الأدنى
            if quality_value < 144:
                quality_value = 144
            # تحديد الحد الأقصى
            elif quality_value > 4320:
                quality_value = 4320
        except:
            quality_value = 720

        # إنشاء مجلد مؤقت لقائمة التشغيل
        temp_dir = tempfile.mkdtemp(prefix="playlist_video_")
        # تحويل المسار إلى كائن Path
        playlist_dir = Path(temp_dir)

        # الحصول على معلومات قائمة التشغيل أولاً
        playlist_info = extract_playlist_info(url)
        # تنظيف اسم القائمة لاستخدامه كاسم لملف ZIP
        playlist_name = sanitize_filename(
            playlist_info.get("playlist_name", "playlist")
        )

        # إعداد خيارات yt-dlp لتنزيل قائمة التشغيل
        ydl_opts = {
            # تحديد صيغة التنزيل (أفضل فيديو وصوت)
            "format": f"bestvideo[height<={quality_value}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality_value}]/best",
            # تحديد مسار واسم الملفات التي سيتم تنزيلها داخل المجلد المؤقت
            "outtmpl": str(playlist_dir / "%(title)s.%(ext)s"),
            # تحديد صيغة الدمج لتكون mp4
            "merge_output_format": "mp4",
            # تشغيل العملية في الوضع الصامت
            "quiet": True,
            # تحديد عدم استخلاص المعلومات المسطحة (flat extraction)
            "extract_flat": False,
        }

        # بدء عملية تنزيل قائمة التشغيل
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # تشغيل عملية التنزيل في خيط منفصل
            await asyncio.to_thread(ydl.download, [url])

        # إنشاء اسم ملف ZIP
        zip_filename = f"{playlist_name}_videos.zip"
        # تحديد مسار ملف ZIP
        zip_path = DOWNLOAD_DIR / zip_filename

        # إنشاء ملف ZIP وكتابة الملفات فيه
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            file_count = 0
            # التكرار على جميع الملفات والمجلدات داخل المجلد المؤقت
            for file_path in playlist_dir.rglob("*"):
                # التحقق مما إذا كان المسار يشير إلى ملف
                if file_path.is_file():
                    # الحصول على المسار النسبي للملف داخل مجلد ZIP
                    arcname = file_path.relative_to(playlist_dir)
                    # إضافة الملف إلى ملف ZIP
                    zipf.write(file_path, arcname)
                    # زيادة عداد الملفات
                    file_count += 1
                    # تسجيل رسالة تفيد بإضافة الملف إلى ZIP
                    logger.info(f"Added to zip: {arcname}")

            # تسجيل رسالة تفيد بإنشاء ملف ZIP
            logger.info(f"Created zip with {file_count} files: {zip_path}")

        # التحقق من أن ملف ZIP قد تم إنشاؤه
        if not zip_path.exists():
            # إذا لم يتم إنشاؤه، إرجاع خطأ
            raise HTTPException(status_code=500, detail="Failed to create zip file")

        # اختبار سلامة ملف ZIP
        try:
            # فتح ملف ZIP للقراءة
            with zipfile.ZipFile(zip_path, "r") as test_zip:
                # اختبار سلامة الأرشيف
                test_zip.testzip()
            # تسجيل رسالة تفيد بنجاح الاختبار
            logger.info(f"Zip file integrity verified: {zip_path}")
        except Exception as e:
            # تسجيل أي خطأ يحدث أثناء الاختبار
            logger.error(f"Zip file integrity check failed: {e}")
            # إرجاع خطأ HTTP 500
            raise HTTPException(status_code=500, detail="Created zip file is corrupted")

        # جدولة مهمة تنظيف الملفات بعد تأخير
        if background_tasks:
            background_tasks.add_task(
                delayed_cleanup, playlist_dir, zip_path, delay=300
            )

        # إرجاع استجابة ملف
        return FileResponse(
            # المسار إلى ملف ZIP
            zip_path,
            # نوع وسائط الملف
            media_type="application/zip",
            # اسم الملف الذي سيتم تنزيله
            filename=zip_filename,
        )

    # التعامل مع أخطاء التنزيل المحددة من yt_dlp
    except yt_dlp.utils.DownloadError as e:
        # إرجاع خطأ HTTP 400
        raise HTTPException(status_code=400, detail=f"Download error: {str(e)}")
    # التعامل مع أي أخطاء أخرى غير متوقعة
    except Exception as e:
        # تسجيل معلومات الخطأ التفصيلية
        logger.error(f"Playlist video download error: {e}")
        logger.error(traceback.format_exc())
        # إرجاع خطأ HTTP 500
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# تعريف نقطة نهاية لـ GET /download/playlist/audio
@app.get("/download/playlist/audio")
# الدالة التي تُعالج الطلب بشكل متزامن
async def download_playlist_audio(
    # تعريف معلمة الرابط
    url: str = Query(...),
    # إضافة BackgroundTasks لإدارة المهام الخلفية
    background_tasks: BackgroundTasks = None,
):
    try:
        # إنشاء مجلد مؤقت لقائمة التشغيل
        temp_dir = tempfile.mkdtemp(prefix="playlist_audio_")
        # تحويل المسار إلى كائن Path
        playlist_dir = Path(temp_dir)

        # الحصول على معلومات قائمة التشغيل أولاً
        playlist_info = extract_playlist_info(url)
        # تنظيف اسم القائمة لاستخدامه كاسم لملف ZIP
        playlist_name = sanitize_filename(
            playlist_info.get("playlist_name", "playlist")
        )

        # إعداد خيارات yt-dlp لتنزيل الصوت فقط
        ydl_opts = {
            # تحديد أفضل صيغة صوت (m4a أو غيرها)
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            # تحديد مسار واسم الملفات التي سيتم تنزيلها داخل المجلد المؤقت
            "outtmpl": str(playlist_dir / "%(title)s.%(ext)s"),
            # استخدام postprocessors لتحويل الصوت بعد التنزيل
            "postprocessors": [
                {
                    # تحديد المفتاح لـ FFmpegExtractAudio
                    "key": "FFmpegExtractAudio",
                    # تحديد الكود المفضل ليكون mp3
                    "preferredcodec": "mp3",
                    # تحديد الجودة المفضلة
                    "preferredquality": "192",
                }
            ],
            # تشغيل العملية في الوضع الصامت
            "quiet": True,
            # تحديد عدم استخلاص المعلومات المسطحة
            "extract_flat": False,
        }

        # بدء عملية تنزيل قائمة التشغيل
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # تشغيل عملية التنزيل في خيط منفصل
            await asyncio.to_thread(ydl.download, [url])

        # إنشاء اسم ملف ZIP
        zip_filename = f"{playlist_name}_audio.zip"
        # تحديد مسار ملف ZIP
        zip_path = DOWNLOAD_DIR / zip_filename

        # إنشاء ملف ZIP وكتابة الملفات فيه
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            file_count = 0
            # التكرار على جميع الملفات داخل المجلد المؤقت
            for file_path in playlist_dir.rglob("*"):
                # التحقق مما إذا كان المسار يشير إلى ملف
                if file_path.is_file():
                    # الحصول على المسار النسبي للملف
                    arcname = file_path.relative_to(playlist_dir)
                    # إضافة الملف إلى ملف ZIP
                    zipf.write(file_path, arcname)
                    # زيادة عداد الملفات
                    file_count += 1
                    # تسجيل رسالة تفيد بإضافة الملف إلى ZIP
                    logger.info(f"Added to zip: {arcname}")

            # تسجيل رسالة تفيد بإنشاء ملف ZIP
            logger.info(f"Created zip with {file_count} files: {zip_path}")

        # التحقق من أن ملف ZIP قد تم إنشاؤه
        if not zip_path.exists():
            # إذا لم يتم إنشاؤه، إرجاع خطأ
            raise HTTPException(status_code=500, detail="Failed to create zip file")

        # اختبار سلامة ملف ZIP
        try:
            # فتح ملف ZIP للقراءة
            with zipfile.ZipFile(zip_path, "r") as test_zip:
                # اختبار سلامة الأرشيف
                test_zip.testzip()
            # تسجيل رسالة تفيد بنجاح الاختبار
            logger.info(f"Zip file integrity verified: {zip_path}")
        except Exception as e:
            # تسجيل أي خطأ يحدث أثناء الاختبار
            logger.error(f"Zip file integrity check failed: {e}")
            # إرجاع خطأ HTTP 500
            raise HTTPException(status_code=500, detail="Created zip file is corrupted")

        # جدولة مهمة تنظيف الملفات بعد تأخير
        if background_tasks:
            background_tasks.add_task(
                delayed_cleanup, playlist_dir, zip_path, delay=300
            )

        # إرجاع استجابة ملف
        return FileResponse(
            # المسار إلى ملف ZIP
            zip_path,
            # نوع وسائط الملف
            media_type="application/zip",
            # اسم الملف الذي سيتم تنزيله
            filename=zip_filename,
        )

    # التعامل مع أخطاء التنزيل المحددة من yt_dlp
    except yt_dlp.utils.DownloadError as e:
        # إرجاع خطأ HTTP 400
        raise HTTPException(status_code=400, detail=f"Download error: {str(e)}")
    # التعامل مع أي أخطاء أخرى غير متوقعة
    except Exception as e:
        # تسجيل معلومات الخطأ التفصيلية
        logger.error(f"Playlist audio download error: {e}")
        logger.error(traceback.format_exc())
        # إرجاع خطأ HTTP 500
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
