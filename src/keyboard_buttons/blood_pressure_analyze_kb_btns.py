from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

bp_analysis_buttons = [
    [KeyboardButton(text="Быстрый"), KeyboardButton(text="Расширенный")],
    [KeyboardButton(text="🚫Отмена")]
]

bp_analysis_kb = ReplyKeyboardMarkup(
    keyboard=bp_analysis_buttons,
    is_persistent=True,
    resize_keyboard=True,
    one_time_keyboard=True
)
