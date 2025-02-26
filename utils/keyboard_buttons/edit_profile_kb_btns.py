from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

edit_profile_buttons = [
    KeyboardButton(text="Измени имя"),
    KeyboardButton(text="Измени пол"),
    KeyboardButton(text="Сделай анонимным"),
    KeyboardButton(text="🔙Назад")
]

edit_profile_kb = ReplyKeyboardMarkup(
    keyboard=[edit_profile_buttons],
    is_persistent=True,
    resize_keyboard=True,
    one_time_keyboard=True
)
