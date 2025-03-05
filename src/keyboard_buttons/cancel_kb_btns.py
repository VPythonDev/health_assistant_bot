from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

cancel_buttons = [
    KeyboardButton(text="🚫Отмена")
]

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[cancel_buttons],
    resize_keyboard=True,
    one_time_keyboard=True
)
