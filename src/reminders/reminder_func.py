from src.bot import bot


async def send_reminder(user_id, reminder_text):
    """Send reminder to user"""
    await bot.send_message(chat_id=user_id, text=reminder_text)
