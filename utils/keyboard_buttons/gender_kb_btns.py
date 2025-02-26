from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

gender_buttons = [
    InlineKeyboardButton(text="🚹Мужчина", callback_data="Male"),
    InlineKeyboardButton(text="🚺Женщина", callback_data="Female"),
    InlineKeyboardButton(text="🚫Не указывать", callback_data="Do not specify")
]

gender_kb = InlineKeyboardMarkup(inline_keyboard=[gender_buttons])
