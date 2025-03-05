from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

reminder_types_buttons = [
    InlineKeyboardButton(text="Одноразовое", callback_data="Single"),
    InlineKeyboardButton(text="Повторяющееся", callback_data="Repeated")
]

reminder_types_kb = InlineKeyboardMarkup(inline_keyboard=[reminder_types_buttons])

repeat_modes_buttons = [
    InlineKeyboardButton(text="Интервал", callback_data="Interval"),
    InlineKeyboardButton(text="Конкретное время", callback_data="Cron")
]

repeat_modes_kb = InlineKeyboardMarkup(inline_keyboard=[repeat_modes_buttons])
