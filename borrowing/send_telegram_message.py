import os
from telegram import Bot


def send_telegram_message(message: str):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    bot_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    bot = Bot(token=bot_token)

    bot.send_message(chat_id=bot_chat_id, text=message)
