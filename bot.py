# bot.py

import logging
from telegram.ext import ApplicationBuilder
from config import BOT_TOKEN
from handlers import setup_handlers

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Load handlers
    setup_handlers(app)

    logger.info("Bot started...")
    app.run_polling()


if __name__ == '__main__':
    main()
