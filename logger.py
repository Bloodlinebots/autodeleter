# logger.py

import json
from config import LOG_CHANNEL_ID
from datetime import datetime

# Memory-based user store (can be replaced with DB)
logged_users = set()

async def log_user_if_new(user, context):
    user_id = user.id
    if user_id in logged_users:
        return

    logged_users.add(user_id)

    if LOG_CHANNEL_ID:
        msg = (
            f"👤 <b>New Media Sender Detected</b>\n"
            f"🆔 <b>User:</b> @{user.username or 'NoUsername'} ({user_id})\n"
            f"🕒 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await context.bot.send_message(chat_id=LOG_CHANNEL_ID, text=msg, parse_mode="HTML")
