import os

from aiogram import Bot

BOT_API_TOKEN = os.getenv("bot_token")

bot = Bot(token=BOT_API_TOKEN)
