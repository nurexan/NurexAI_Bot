"""
downloader.py - NurexAI v12.2 Ultra Fast Edition
Max Speed | Samsung S8 Emulation | Integrated Portable FFmpeg
"""
import os
import yt_dlp
import uuid
import logging
import re
import subprocess
from pathlib import Path
from instagrapi import Client
from config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, DATA_DIR, AUDIO_CACHE_DIR

# PRO: Initialize Portable FFmpeg
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
    print("⚔️ [SYSTEM] Portable FFmpeg muvaffaqiyatli ulandi!")
except ImportError:
    print("⚠️ [SYSTEM] static-ffmpeg topilmadi. Ovoz ajratish ishlamasligi mumkin.")

logger = logging.getLogger(__name__)

# PRO IDENTITY: Samsung S8
PRO_DEVICE = {
    "app_version": "269.0.0.18.75",
    "android_version": 26,
    "android_release": "8.0.0",
    "dpi": "480dpi",
    "resolution": "1080x1920",
    "manufacturer": "samsung",
    "device": "SM-G950F",
    "model": "dreamqlte",
    "cpu": "exynos8895",
    "version_code": "443213193",
}

SESSION_FILE = Path("data/instagram_session.json")
_ig_client = None


def get_shortcode(url: str) -> str:
    patterns = [r"/reels?/([^/?#&]+)", r"/p/([^/?#&]+)", r"/tv/([^/?#&]+)"]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return str(uuid.uuid4().hex[:10])


def local_extract_audio(video_path: str, output_mp3: str) -> bool:
    """PRO: Extracts audio from local video using Integrated FFmpeg (Instant)"""
    try:
        print(f"🎵 [AUDIO] Ovoz ajratilmoqda: {video_path}")
        cmd = [
            "ffmpeg", "-y", "-i", video_path,
            "-vn", "-acodec", "libmp3lame", "-q:a", "2",
            "-threads", "4",
            output_mp3,
        ]
        subprocess.run(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )
        print(f"✅ [AUDIO] Tayyor: {output_mp3}")
        return True
    except Exception as e:
        print(f"❌ [AUDIO] FFmpeg xatosi: {e}")
        return False


def get_pro_client():
    global _ig_client
    if _ig_client:
        return _ig_client
    cl = Client()
    cl.delay_range = [0, 1]  # TEZLASHTIRISH: eski [3, 8] edi
    cl.set_device(PRO_DEVICE)
    try:
        if SESSION_FILE.exists():
            cl.load_settings(str(SESSION_FILE))
            try:
                cl.get_timeline_feed()
                _ig_client = cl
                return _ig_client
            except Exception:
                pass
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        cl.dump_settings(str(SESSION_FILE))
        _ig_client = cl
        return _ig_client
    except Exception:
        return None


def download_instagram_video(url: str, output_dir: Path, progress_callback=None) -> str:
    # 1-usul: instagrapi (tez, autentifikatsiyalangan)
    cl = get_pro_client()
    if cl:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            pk = cl.media_pk_from_url(url)
            path = cl.video_download(pk, folder=str(output_dir))
            return str(path)
        except Exception as ex:
            print(f"⚠️ [INSTAGRAPI] Xato: {ex}, fallback-ga o'tilmoqda...")

    # 2-usul: yt-dlp (IRON FALLBACK) — TEZLASHTIRILGAN
    unique_id = uuid.uuid4().hex[:8]

    def hook(d):
        if progress_callback and d.get("status") == "downloading":
            p = d.get("_percent_str", "0%").strip()
            s = d.get("_speed_str", "N/A")
            progress_callback(f"{p} | {s}")

    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": str(output_dir / f"vid_{unique_id}.%(ext)s"),
        "quiet": True,
        "noplaylist": True,
        "noprogress": False,
        "progress_hooks": [hook],
        # === TEZLASHTIRISH SOZLAMALARI ===
        "concurrent_fragment_downloads": 16,  # Ko'proq parallel yuklab olish
        "http_chunk_size": 10485760,          # 10MB chunk
        "retries": 3,
        "fragment_retries": 3,
        "buffersize": 1024 * 16,
        "timeout": 30,
        "socket_timeout": 30,
        "source_address": "0.0.0.0",
        "user_agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.4.1 Mobile/15E148 Safari/604.1"
        ),
        "headers": {
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "*/*",
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("🌍 [YT-DLP] Yuklanmoqda (ultra fast mode)...")
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        print(f"❌ [FAIL] Hech qaysi usul ishlamadi: {e}")
        return None
