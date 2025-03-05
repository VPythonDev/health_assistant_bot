from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

anonymity_buttons = [
    InlineKeyboardButton(text="Да", callback_data="Anonim"),
    InlineKeyboardButton(text="Нет", callback_data="Not anonim")
]

anonymity_kb = InlineKeyboardMarkup(inline_keyboard=[anonymity_buttons])
