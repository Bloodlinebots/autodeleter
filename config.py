# config.py

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DEEPAI_API_KEY = os.getenv("DEEPAI_API_KEY")
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")
CLEANUP_DELAY_SECONDS = int(os.getenv("CLEANUP_DELAY_SECONDS", 900))
