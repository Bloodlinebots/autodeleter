# handlers.py

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from utils.nsfw_check import is_nsfw
from logger import log_user_if_new
from config import CLEANUP_DELAY_SECONDS
import asyncio
import tempfile
import os

# Track safe media messages for delayed deletion
safe_media = []

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or (not update.message.photo and not update.message.video):
        return

    user = update.effective_user
    chat = update.effective_chat
    message = update.message

    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    file = await context.bot.get_file(file_id)

    # 🛠️ Use tempfile to avoid permanent files
    suffix = ".jpg" if message.photo else ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        await file.download_to_drive(tmp.name)
        file_path = tmp.name

    # 🔍 Check for NSFW content
    if await is_nsfw(file_path):
        await message.delete()
        os.remove(file_path)
        return

    # ✅ Not NSFW — log user if new
    await log_user_if_new(user, context)

    # 🧹 Schedule message for delayed deletion
    safe_media.append((chat.id, message.message_id, asyncio.get_event_loop().time()))

    # 🧼 Remove temp file
    os.remove(file_path)

async def cleanup_safe_media(context: ContextTypes.DEFAULT_TYPE):
    current_time = asyncio.get_event_loop().time()
    to_delete = [item for item in safe_media if current_time - item[2] > CLEANUP_DELAY_SECONDS]

    for chat_id, message_id, _ in to_delete:
        try:
            await context.bot.delete_message(chat_id, message_id)
        except:
            pass

    for item in to_delete:
        safe_media.remove(item)

def setup_handlers(app):
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    app.job_queue.run_repeating(cleanup_safe_media, interval=60)
