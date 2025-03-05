import asyncio

from aiogram import Dispatcher

from src.bot import bot
from src.handlers import (anon_profile, blood_pressure, create_bp_entry,
                          create_reminder, deanonymization, delete_reminder,
                          edit_profile, generate_bp_graph, menu, profile,
                          registration, reminders, start)
from src.models.database_manager import db
from src.my_routers import router
from src.reminders.reminder import scheduler

# Dispatcher
dispatcher = Dispatcher()

# Add routers in dispatcher
dispatcher.include_router(router)


async def start_bot():
    """Start scheduler, initialize pool in database, start bot"""
    try:
        scheduler.start()
        await db.init_pool()
        await bot.delete_webhook(True)
        await dispatcher.start_polling(bot)
    finally:
        await db.close_connections()
        scheduler.shutdown()

asyncio.run(start_bot())
