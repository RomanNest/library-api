import os
from telegram import Bot
import asyncio
from dotenv import load_dotenv

load_dotenv()


def send_telegram_message(message: str):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    bot_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    bot = Bot(token=bot_token)

    async def async_send_message():
        await bot.send_message(chat_id=bot_chat_id, text=message)

    asyncio.run(async_send_message())
