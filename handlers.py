# handlers.py

from telegram import Update, MessageEntity
from telegram.ext import ContextTypes, MessageHandler, filters, CommandHandler
from utils.nsfw_check import is_nsfw
from logger import log_user_if_new
from config import CLEANUP_DELAY_SECONDS
import asyncio

# Track safe media messages for delayed deletion
safe_media = []

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo and not update.message.video:
        return

    user = update.effective_user
    chat = update.effective_chat
    message = update.message

    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    file = await context.bot.get_file(file_id)
    file_path = await file.download_to_drive()

    # Check for NSFW
    if await is_nsfw(file_path):
        await message.delete()
        return

    # Not NSFW — log the user if new
    await log_user_if_new(user, context)

    # Store message for delayed deletion
    safe_media.append((chat.id, message.message_id, asyncio.get_event_loop().time()))

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
