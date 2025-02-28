from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from utils.data_processor import change_day_index, process_bp_entries
from utils.database_manager import db
from utils.fsm import BloodPressureState, CreateBPEntryState, MenuState
from utils.keyboard_buttons.blood_pressure_kb_btns import (
    bp_kb, generate_bp_dates_buttons)
from utils.keyboard_buttons.menu_kb_btns import menu_kb
from utils.my_routers import router
from utils.user_class import User


@router.callback_query(BloodPressureState.waiting_for_choice)
async def show_bp_info_callback_query_handler(callback_query) -> None:
    user_id = callback_query.from_user.id
    user_choice = callback_query.data

    user = User.get_user(user_id)

    if user_choice == "Next":
        measurement_dates = user.measurement_dates

        index = user.current_day_index
        new_index = await change_day_index(measurement_dates, index, is_previous=False)
        # Update index
        user.current_day_index = new_index

        dates_kb = await generate_bp_dates_buttons(measurement_dates, new_index)

        await callback_query.message.edit_text("Даты:", reply_markup=dates_kb)
    elif user_choice == "Previous":
        measurement_dates = user.measurement_dates

        index = user.current_day_index
        new_index = await change_day_index(measurement_dates, index)
        # Update index
        user.current_day_index = new_index

        dates_kb = await generate_bp_dates_buttons(measurement_dates, new_index)

        await callback_query.message.edit_text("Даты:", reply_markup=dates_kb)
    else:
        # Covert date to date object
        user_date = datetime.strptime(user_choice, "%Y-%m-%d")

        try:
            blood_pressure_entries = await db.fetch_bp_entries(user_date, user_id)

            message_text = await process_bp_entries(blood_pressure_entries)

            await callback_query.message.answer(message_text, reply_markup=bp_kb)
        except Exception:
            await callback_query.message.answer("Я не могу получить ваши записи за эту дату🙁", reply_markup=bp_kb)


@router.message(BloodPressureState.waiting_for_choice)
async def bp_message_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    user_choice = message.text

    if user_choice == "✍️Создай новую запись":
        user = User.get_user(user_id)
        user_full_name = user.full_name

        enter_word = "Введи" if user_full_name else "Введите"

        await state.set_state(CreateBPEntryState.waiting_for_bp)
        await message.answer(f"{enter_word} данные давления в формате: 120 80 (с пробелом, а не '-')")
    elif user_choice == "🔙Назад":
        await state.set_state(MenuState.waiting_for_choice)
        await message.answer("Чем могу быть полезен?", reply_markup=menu_kb)
