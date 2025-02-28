from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

confirm_buttons = [
    KeyboardButton(text="Да✅"),
    KeyboardButton(text="Нет❌")
]

confirm_kb = ReplyKeyboardMarkup(
    keyboard=[confirm_buttons],
    is_persistent=True,
    resize_keyboard=True,
    one_time_keyboard=True
)
