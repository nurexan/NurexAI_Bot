"""
config.py - NurexAI v11.0 Clean Config
Faqat eng kerakli sozlamalar.
"""
import os
import json
from dotenv import load_dotenv
from pathlib import Path

# .env faylini yuklash
load_dotenv()

# Bot sozlamalari
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID", 0))

# Instagram sozlamalari
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

# Kataloglar (Fayl tizimi toza turishi uchun temp ishlatamiz)
import tempfile
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# Serverda yoki kompyuterda "Temp" (vaqtinchalik xotira) da saqlaymiz!
TEMP_ROOT = Path(tempfile.gettempdir()) / "NurexAI"
DOWNLOADS_DIR = TEMP_ROOT / "downloads"
AUDIO_CACHE_DIR = TEMP_ROOT / "audio"

for folder in [DATA_DIR, DOWNLOADS_DIR, AUDIO_CACHE_DIR]:
    folder.mkdir(parents=True, exist_ok=True)
# Statistika (Soddalashtirilgan)
STATS_FILE = DATA_DIR / "stats.json"

def increment_stats(user_info: dict):
    stats = {"count": 0, "users": []}
    if STATS_FILE.exists():
        try:
            with open(STATS_FILE, 'r') as f:
                stats = json.load(f)
        except: pass
    
    stats["count"] += 1
    if user_info.get("user") not in stats["users"]:
        stats["users"].append(user_info.get("user"))
        
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f)
