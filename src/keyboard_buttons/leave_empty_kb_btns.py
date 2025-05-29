from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

leave_empty_buttons = [
    KeyboardButton(text="Оставь пустым")
]

leave_empty_kb = ReplyKeyboardMarkup(
    keyboard=[leave_empty_buttons],
    resize_keyboard=True,
    one_time_keyboard=True
)
