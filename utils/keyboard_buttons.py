from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)

# Anonim
anonim_buttons_list = [
    InlineKeyboardButton(text="Да", callback_data="Anonim"),
    InlineKeyboardButton(text="Нет", callback_data="Not anonim")
]
anonim_keyboard = InlineKeyboardMarkup(inline_keyboard=[anonim_buttons_list])

# Gender
gender_buttons_list = [
    InlineKeyboardButton(text="🚹Мужчина", callback_data="Male"),
    InlineKeyboardButton(text="🚺Женщина", callback_data="Female"),
    InlineKeyboardButton(text="🚫Не указывать", callback_data="Do not specify")
]
gender_keyboard = InlineKeyboardMarkup(inline_keyboard=[gender_buttons_list])

# Menu
menu_buttons_list = [
    KeyboardButton(text="👤Профиль"),
    KeyboardButton(text="🫀Дневник давления"),
    KeyboardButton(text="🔔Напоминания"),
    KeyboardButton(text="✍️Заметки")
]
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[menu_buttons_list],
    is_persistent=True,
    resize_keyboard=True,
    one_time_keyboard=True
)

# Edit profile
edit_profile_buttons_list = [
    KeyboardButton(text="Изменить имя"),
    KeyboardButton(text="Изменить пол"),
    KeyboardButton(text="Стать анонимным"),
    KeyboardButton(text="🔙Назад")
]
edit_profile_keyboard = ReplyKeyboardMarkup(
    keyboard=[edit_profile_buttons_list],
    is_persistent=True,
    resize_keyboard=True,
    one_time_keyboard=True
)

# Anonim edit profile
anonim_edit_profile_buttons_list = [
    KeyboardButton(text="Деанонимизация"),
    KeyboardButton(text="🔙Назад")
]
anonim_edit_profile_keyboard = ReplyKeyboardMarkup(
    keyboard=[anonim_edit_profile_buttons_list],
    is_persistent=True,
    resize_keyboard=True,
    one_time_keyboard=True
)
