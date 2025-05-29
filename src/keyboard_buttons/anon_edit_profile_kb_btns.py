from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

anonim_edit_profile_buttons = [
    [KeyboardButton(text="Раскрыть профиль")],
    [KeyboardButton(text="🔙Назад")]
]

anonim_edit_profile_kb = ReplyKeyboardMarkup(
    keyboard=anonim_edit_profile_buttons,
    resize_keyboard=True,
    one_time_keyboard=True
)
