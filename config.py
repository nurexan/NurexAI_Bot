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

# Kataloglar
BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
DATA_DIR = BASE_DIR / "data"

for folder in [DOWNLOADS_DIR, DATA_DIR]:
    folder.mkdir(exist_ok=True)

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
