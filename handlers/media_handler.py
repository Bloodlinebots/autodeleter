import os
import asyncio
from telegram import Update
from telegram.ext import MessageHandler, ContextTypes, filters

from utils.nsfw_check import is_nsfw
from config import CLEANUP_DELAY_SECONDS, LOG_CHANNEL_ID

# Auto delete safe media after X seconds
async def auto_delete_after_delay(message, delay):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass

# Log new user
async def log_new_user(user_id, context: ContextTypes.DEFAULT_TYPE):
    if LOG_CHANNEL_ID:
        await context.bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=f"👤 New user: <code>{user_id}</code>",
            parse_mode='HTML'
        )

# Main media handler
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user

    if not message or not user:
        return

    user_id = user.id

    # Download media
    file = await message.effective_attachment.get_file()
    file_path = f"downloads/{message.chat.id}_{message.message_id}.jpg"
    os.makedirs("downloads", exist_ok=True)
    await file.download_to_drive(file_path)

    # NSFW detection
    if await is_nsfw(file_path):
        await message.delete()
        return

    # Safe media: schedule auto delete
    asyncio.create_task(auto_delete_after_delay(message, CLEANUP_DELAY_SECONDS))

    # Log user if needed
    await log_new_user(user_id, context)

# Telegram handler
media_handler = MessageHandler(
    filters.PHOTO | filters.VIDEO | filters.DOCUMENT.IMAGE,
    handle_media
)
