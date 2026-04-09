"""
bot.py - NurexAI Professional Downloader Bot v12.3 (Super Clean + Ultra Fast)
Admin Notifications, Group Tracking, Professional Video Downloader & Instant Audio.
"""
import os
import sys
import asyncio
import logging
import re
import json
import time
from datetime import date
from pathlib import Path

# --- RENDER UCHUN MUHIM: Papkalarni avtomatik yaratish ---
for folder in ["downloads", "data", "audio_cache"]:
    os.makedirs(folder, exist_ok=True)

# Windows konsoli uchun UTF-8 majburiy
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
)

from config import (
    BOT_TOKEN, ADMIN_TELEGRAM_ID, DOWNLOADS_DIR, DATA_DIR, increment_stats
)
from downloader import (
    download_instagram_video, local_extract_audio, get_shortcode, AUDIO_CACHE_DIR
)

# === LOGGING ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('data/bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === DATA FILES ===
USERS_FILE = DATA_DIR / "users.json"
GROUPS_FILE = DATA_DIR / "groups.json"
STATS_FILE = DATA_DIR / "stats.json"

# ============================================================
# === DATA LOGIC ===
# ============================================================

def load_json(file_path):
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []
    return []

def save_json(file_path, data):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_stats():
    if STATS_FILE.exists():
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"today_videos": 0, "total_videos": 0}

async def notify_admin(context: ContextTypes.DEFAULT_TYPE, text: str):
    if ADMIN_TELEGRAM_ID:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_TELEGRAM_ID, 
                text=f"[ADMIN] *Admin Xabarnomasi:*\n\n{text}", 
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Admin notify error: {e}")

# ============================================================
# === MENYULAR ===
# ============================================================

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📥 Qo'llanma (Qanday ishlatish)", callback_data="help")],
        [
            InlineKeyboardButton("📊 Statistika", callback_data="stats"),
            InlineKeyboardButton("👥 Guruhda ishlash", callback_data="group_setup")
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

# ============================================================
# === HANDLERS ===
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    if chat.type == "private":
        users = load_json(USERS_FILE)
        if user.id not in users:
            users.append(user.id)
            save_json(USERS_FILE, users)
            await notify_admin(context, f"🆕 *Yangi foydalanuvchi!*\n\nID: `{user.id}`\nIsm: {user.full_name}\nUsername: @{user.username or 'yoq'}")

    welcome_text = (
        f"👋 Salom, *{user.first_name}*!\n\n"
        f"🦅 *NurexAI Downloader* — tezkor media yuklovchi botga xush kelibsiz!\n\n"
        f"📌 *Nima qila olaman?*\n"
        f"⚡️ Instagram, YouTube, TikTok videolarini tezda yuklayman\n"
        f"🎵 Videodan musiqani bir zumda ajratib beraman\n"
        f"👥 Guruhlarda linklarni o'chirib, videoni o'zim tashlayman\n\n"
        f"🔗 *Foydalanish:* Shunchaki link yuboring — qolganini men qilaman!"
    )

    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=main_menu_keyboard())

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "main_menu":
        stats = load_stats()
        await query.edit_message_text(
            f"🏠 *Asosiy Menyu*\n\n📊 Bugun: *{stats.get('today_videos', 0)} ta* | Jami: *{stats.get('total_videos', 0)} ta*",
            parse_mode='Markdown', reply_markup=main_menu_keyboard()
        )
    elif data == "help":
        help_text = (
            "📥 *Qo'llanma — Qanday ishlatish?*\n\n"
            "1️⃣ Instagram, YouTube yoki TikTok linkini botga yuboring\n"
            "2️⃣ Bot avtomatik ravishda yuklab, sizga yuboradi\n"
            "3️⃣ Musiqa kerak bo'lsa — *'🎵 Musiqani olish'* tugmasini bosing\n\n"
            "👥 *Guruhda ishlash:*\n"
            "   • Botni guruhga qo'shing va admin qiling\n"
            "   • 'Delete messages' huquqini bering\n"
            "   • Endi bot linklarni o'chirib, videoni o'zi tashlab beradi!"
        )
        await query.edit_message_text(help_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Orqaga", callback_data="main_menu")]]))
    elif data == "stats":
        stats = load_stats()
        stats_text = (
            f"📊 *Bot Statistikasi*\n\n"
            f"📅 Bugungi sana: *{date.today()}*\n"
            f"🎬 Bugun yuklangan: *{stats.get('today_videos', 0)} ta*\n"
            f"📦 Jami yuklangan: *{stats.get('total_videos', 0)} ta*"
        )
        await query.edit_message_text(stats_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Orqaga", callback_data="main_menu")]]))
    elif data == "group_setup":
        setup_text = (
            "👥 *Guruhda ishlash — Sozlash*\n\n"
            "1️⃣ Botni guruhga qo'shing\n"
            "2️⃣ Botga *Admin* huquqini bering\n"
            "3️⃣ *'Delete messages'* huquqini yoqing\n\n"
            "✅ Tayyor! Endi guruhga link tashlasangiz, bot uni o'chirib, videoni o'zi yuboradi!"
        )
        await query.edit_message_text(setup_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Orqaga", callback_data="main_menu")]]))
    elif data == "auth_chrome_ui":
        await auth_chrome_start(query, context)
    elif data.startswith("aud|"):
        sc = data.split("|")[1]
        audio_path = AUDIO_CACHE_DIR / f"{sc}.mp3"
        if os.path.exists(audio_path):
            await query.message.reply_audio(audio=open(audio_path, 'rb'), caption="🎵 Video musiqasi")
        else:
            await query.message.reply_text("❌ Musiqa topilmadi.")

def cleanup_old_files():
    """1 soatdan eski qolib ketgan musiqa/videolarni tozalaydi."""
    now = time.time()
    for folder in [DOWNLOADS_DIR, AUDIO_CACHE_DIR]:
        if not os.path.exists(folder): continue
        for filename in os.listdir(folder):
            path = os.path.join(folder, filename)
            if os.path.isfile(path) and (now - os.path.getmtime(path) > 3600):
                try: os.remove(path)
                except: pass

async def handle_media_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    text = msg.text or msg.caption
    if not text: return
    
    # Har safar link tashlanganda eskilarni tozalaymiz
    cleanup_old_files()

    pattern = r'https?://(?:www\.)?(?:instagram\.com|youtube\.com|youtu\.be|tiktok\.com|vimeo\.com|reels)/[\w?=&/.\-]+'
    match = re.search(pattern, text)
    if not match: return

    url = match.group(0)
    user = update.effective_user
    chat = update.effective_chat
    chat_id = chat.id
    message_id = msg.message_id
    sc = get_shortcode(url)

    # 1. Group Tracking
    if chat.type in ["group", "supergroup"]:
        groups = load_json(GROUPS_FILE)
        group_ids = [g["id"] for g in groups]
        if chat_id not in group_ids:
            groups.append({"id": chat_id, "title": chat.title, "type": chat.type})
            save_json(GROUPS_FILE, groups)
            await notify_admin(context, f"[GROUP] Bot yangi guruhga qo'shildi!\n\nNomi: {chat.title}\nID: `{chat_id}`")

    status = await msg.reply_text("📥 *Video yuklanmoqda...*", parse_mode="Markdown")

    try:
        # Video yuklab olinadi (Ultra-fast usulida)
        video_file = await asyncio.to_thread(download_instagram_video, url, DOWNLOADS_DIR)

        if video_file and os.path.exists(video_file):
            from telegram.helpers import escape_markdown
            u_name = escape_markdown(user.first_name, version=2)
            caption = fr"[USER] *[{u_name}](tg://user?id={user.id})* so'ragan video\!{'\n\n'}\#downloader"

            # Agar private chat bo'lsa audio ham ajratamiz, guruhlarga shart emas
            btn = None
            if chat.type == "private":
                audio_path = str(AUDIO_CACHE_DIR / f"{sc}.mp3")
                await asyncio.to_thread(local_extract_audio, video_file, audio_path)
                btn = InlineKeyboardMarkup([[InlineKeyboardButton("🎵 Musiqasini olish", callback_data=f"aud|{sc}")]])

            await context.bot.send_video(
                chat_id=chat_id, 
                video=open(video_file, 'rb'), 
                caption=caption, 
                parse_mode="MarkdownV2",
                reply_markup=btn
            )
            await status.delete()

            # Linkni guruhda tozalash
            if chat.type in ["group", "supergroup"]:
                try: 
                    await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
                except Exception: 
                    pass

            increment_stats({"user": user.id})
            
            # Faylni serverda tozalab yuboramiz xotira to'lmasligi uchun
            if os.path.exists(video_file):
                os.remove(video_file)
        else:
            await status.edit_text("❌ *Xatolik:* Instagram rad etdi yoki video topilmadi.", parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Downloader error: {e}")
        await status.edit_text("❌ Yuklash imkoni bo'lmadi.")

# ============================================================
# === ADMIN COMMANDS ===
# ============================================================

async def list_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_TELEGRAM_ID: return
    groups = load_json(GROUPS_FILE)
    if not groups:
        await update.message.reply_text("Bot hozircha guruhlarda yo'q.")
        return

    text = f"[GROUP] *Bot joylashgan guruhlar ({len(groups)} ta):*\n\n"
    for g in groups:
        text += f"- {g['title']} (ID: `{g['id']}`)\n"
    await update.message.reply_text(text, parse_mode="Markdown")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_TELEGRAM_ID: return
    users = load_json(USERS_FILE)
    await update.message.reply_text(f"[USER] *Jami foydalanuvchilar:* {len(users)} ta", parse_mode="Markdown")

async def auth_chrome_start(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    user_id = update_or_query.message.chat_id if isinstance(update_or_query, Update) else update_or_query.from_user.id
    if user_id != ADMIN_TELEGRAM_ID: return

    msg = await (update_or_query.message.reply_text if isinstance(update_or_query, Update) else update_or_query.edit_message_text)(
        "[SESSION] *Chrome'dan sessiya qidirilmoqda...*", parse_mode="Markdown"
    )
    try:
        from extract_cookies import extract_instagram_cookies
        cookies, err = await asyncio.to_thread(extract_instagram_cookies)
        
        if err:
            await msg.edit_text(f"[ERROR] *Xatolik:* {err}", parse_mode="Markdown")
            return
            
        SESSION_FILE = Path("data/instagram_session.json")
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(cookies, f)
            
        await msg.edit_text("[SUCCESS] *Sessiya yangilandi!*", parse_mode="Markdown")
    except Exception as e:
        await msg.edit_text(f"[ERROR] Xato: {e}")

# ============================================================
# === MAIN ===
# ============================================================

def main():
    print("🦅 NurexAI v12.3 (Super Clean Edition) - Launching...")
    
    # Raliway xatosi oldini olish
    if not BOT_TOKEN:
        print("\n" + "="*50)
        print("❌ XATO: BOT_TOKEN topilmadi!")
        print("Railway/Render 'Variables' bo'limiga BOT_TOKEN kiritishingiz shart!")
        print("="*50 + "\n")
        sys.exit(1)
        
    # Railway o'zi konteyner boshqaradi, kill_other_instances kerak emas
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_router))
    
    link_regex = re.compile(r'https?://(?:www\.)?(?:instagram\.com|youtube\.com|youtu\.be|tiktok\.com|reels)/[\w?=&/.\-]+')
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(link_regex) & ~filters.COMMAND, handle_media_link))
    
    print("✨ Bot aktiv! Railway serverda ishlayapti!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()