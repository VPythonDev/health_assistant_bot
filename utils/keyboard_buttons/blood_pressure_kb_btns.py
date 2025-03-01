from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)


def generate_bp_dates_buttons(dates, start_index):
    """Generates inline buttons for dates of blood pressure diary"""
    dates_inline_buttons = []
    amount_entries = 5

    dates_len = len(dates)

    if dates_len > amount_entries:
        previous_button = InlineKeyboardButton(text="⬅️Пред.", callback_data="Previous")
        next_button = InlineKeyboardButton(text="➡️След.", callback_data="Next")

        scrolling_buttons = []

        if start_index == 0:
            scrolling_buttons.append(previous_button)
        elif start_index + amount_entries > dates_len - 1:
            scrolling_buttons.append(next_button)
        else:
            scrolling_buttons.extend([previous_button, next_button])

        if len(dates[start_index:]) >= amount_entries:
            for record_obj in dates[start_index:start_index + amount_entries]:
                measurement_date = str(record_obj[0])
                dates_inline_buttons.append([InlineKeyboardButton(text=measurement_date,
                                                                  callback_data=measurement_date)])

            dates_inline_buttons.append(scrolling_buttons)
            dates_inline_kb = InlineKeyboardMarkup(inline_keyboard=dates_inline_buttons)
            return dates_inline_kb
        else:
            for record_obj in dates[start_index:]:
                measurement_date = str(record_obj[0])
                dates_inline_buttons.append([InlineKeyboardButton(text=measurement_date,
                                                                  callback_data=measurement_date)])

            dates_inline_buttons.append(scrolling_buttons)
            dates_inline_kb = InlineKeyboardMarkup(inline_keyboard=dates_inline_buttons)
            return dates_inline_kb
    else:
        for record_obj in dates:
            measurement_date = str(record_obj[0])
            dates_inline_buttons.append(InlineKeyboardButton(text=measurement_date, callback_data=measurement_date))

        dates_inline_kb = InlineKeyboardMarkup(inline_keyboard=[dates_inline_buttons])
        return dates_inline_kb


bp_buttons = [
    KeyboardButton(text="✍️Создай новую запись"),
    KeyboardButton(text="📈Создай график"),
    KeyboardButton(text="🔙Назад")
]

bp_kb = ReplyKeyboardMarkup(
    keyboard=[bp_buttons],
    is_persistent=True,
    resize_keyboard=True,
    one_time_keyboard=True
)
