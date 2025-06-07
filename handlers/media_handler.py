import os
import asyncio
import logging
from telegram import Update
from telegram.ext import MessageHandler, ContextTypes, filters

from utils.nsfw_check import is_nsfw
from config import CLEANUP_DELAY_SECONDS, LOG_CHANNEL_ID

logger = logging.getLogger(__name__)

# Auto delete safe media after X seconds
async def auto_delete_after_delay(message, delay):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        logger.error(f"Auto-delete failed: {e}")

# Log new user
async def log_new_user(user_id, context: ContextTypes.DEFAULT_TYPE):
    if LOG_CHANNEL_ID:
        try:
            await context.bot.send_message(
                chat_id=LOG_CHANNEL_ID,
                text=f"👤 New user: <code>{user_id}</code>",
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Logging user failed: {e}")

# Main media handler
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user

    if not message or not user:
        return

    user_id = user.id

    file = None
    ext = None

    # Determine type of media
    try:
        if message.photo:
            file = await message.photo[-1].get_file()
            ext = "jpg"
        elif message.video:
            file = await message.video.get_file()
            ext = "mp4"
        elif message.document and message.document.mime_type in ["image/jpeg", "image/png"]:
            file = await message.document.get_file()
            ext = "jpg"
        else:
            return  # Unsupported media

        # Download media
        os.makedirs("downloads", exist_ok=True)
        file_path = f"downloads/{message.chat.id}_{message.message_id}.{ext}"
        await file.download_to_drive(file_path)

        # NSFW check
        if await is_nsfw(file_path):
            await message.delete()
            os.remove(file_path)
            return

        # Safe media: delete after delay
        asyncio.create_task(auto_delete_after_delay(message, CLEANUP_DELAY_SECONDS))

        # Log user
        await log_new_user(user_id, context)

        # Clean up file
        os.remove(file_path)

    except Exception as e:
        logger.error(f"Error handling media: {e}")

# Handler setup
media_handler = MessageHandler(
    filters.PHOTO | filters.VIDEO | (filters.Document.MimeType("image/jpeg") | filters.Document.MimeType("image/png")),
    handle_media
)
