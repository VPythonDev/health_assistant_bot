from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

edit_profile_buttons = [
    KeyboardButton(text="Изменить имя"),
    KeyboardButton(text="Изменить пол"),
    KeyboardButton(text="Стать анонимным"),
    KeyboardButton(text="🔙Назад")
]

edit_profile_kb = ReplyKeyboardMarkup(
    keyboard=[edit_profile_buttons],
    is_persistent=True,
    resize_keyboard=True,
    one_time_keyboard=True
)
