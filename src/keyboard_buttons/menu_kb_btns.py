from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

menu_buttons = [
    [KeyboardButton(text="👤Профиль")],
    [KeyboardButton(text="🫀Дневник давления")],
    [KeyboardButton(text="🔔Напоминания")],
    [KeyboardButton(text="📓Заметки")]
]

menu_kb = ReplyKeyboardMarkup(
    keyboard=menu_buttons,
    resize_keyboard=True,
    one_time_keyboard=True
)
