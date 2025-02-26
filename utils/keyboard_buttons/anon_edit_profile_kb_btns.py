from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

anonim_edit_profile_buttons = [
    KeyboardButton(text="Деанонимизироваться"),
    KeyboardButton(text="🔙Назад")
]

anonim_edit_profile_kb = ReplyKeyboardMarkup(
    keyboard=[anonim_edit_profile_buttons],
    is_persistent=True,
    resize_keyboard=True,
    one_time_keyboard=True
)
