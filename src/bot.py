import asyncio
import os

from aiogram import Bot, Dispatcher

from handlers import (anon_profile, blood_pressure, create_bp_entry,
                      deanonymization, edit_profile, generate_bp_graph, menu,
                      profile, registration, start)
from utils.database_manager import db
from utils.my_routers import router

BOT_API_TOKEN = os.getenv("bot_token")

# Bot
bot = Bot(token=BOT_API_TOKEN)

# Dispatcher
dispatcher = Dispatcher()

# Add routers in dispatcher
dispatcher.include_router(router)


# @dispatcher.message()
# async def test(message: Message) -> None:
#     chat = message.chat
#     username = chat.username
#     first_name = chat.first_name
#     last_name = chat.last_name
#     full_name = chat.full_name
#
#     user = message.from_user
#     user_id = user.id
#
#     await message.answer(f"{username}, {first_name}, {last_name}, {full_name}")
#     await message.answer(f"{user_id}")
#     await message.answer("Hello, " + "d" * 200)


async def start_bot():
    """Initialize pool in database and start bot"""
    try:
        await db.init_pool()
        await bot.delete_webhook(True)
        await dispatcher.start_polling(bot)
    finally:
        await db.close_connections()

asyncio.run(start_bot())
