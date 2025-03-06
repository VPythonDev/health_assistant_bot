from src.bot import bot
from src.models.user_class import User


async def send_reminder(user_id, reminder_text):
    """Send reminder to user"""
    message_text = f"Напоминание\n\n{reminder_text}"

    user = User.get_user(user_id)

    if user:
        user_full_name = user.full_name

        if user_full_name:
            message_text = f"{user_full_name}, напоминание\n\n{reminder_text}"

    await bot.send_message(chat_id=user_id, text=message_text)
