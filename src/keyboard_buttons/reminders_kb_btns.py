from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

reminders_buttons = [
    [KeyboardButton(text="❗️Создай напоминание"), KeyboardButton(text="🗑Удали напоминание")],
    [KeyboardButton(text="🔙Назад")]
]

reminders_kb = ReplyKeyboardMarkup(
    keyboard=reminders_buttons,
    resize_keyboard=True,
    one_time_keyboard=True
)
