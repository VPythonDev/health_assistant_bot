from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

notes_buttons = [
    KeyboardButton(text="Создай заметку"),
    KeyboardButton(text="Удали заметку"),
    KeyboardButton(text="🔙Назад")
]

notes_kb = ReplyKeyboardMarkup(
    keyboard=[notes_buttons],
    is_persistent=True,
    resize_keyboard=True,
    one_time_keyboard=True
)
