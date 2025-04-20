from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.fsm import (BloodPressureState, CreateBPEntryState,
                     GenerateBPGraphState, MenuState)
from src.keyboard_buttons.blood_pressure_kb_btns import (
    bp_kb, generate_bp_dates_buttons)
from src.keyboard_buttons.cancel_kb_btns import cancel_kb
from src.keyboard_buttons.menu_kb_btns import menu_kb
from src.models.database_manager import db
from src.models.user_class import User
from src.my_routers import router
from utils.data_processor import change_day_index, process_bp_entries


@router.message(BloodPressureState.waiting_for_choice)
async def bp_msg_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    user_choice = message.text

    user = User.get_user(user_id)
    user_full_name = user.full_name

    if user_choice == "✍️Создай новую запись":
        enter_word = "Введи" if user_full_name else "Введите"

        await state.set_state(CreateBPEntryState.waiting_for_bp)
        await message.answer(f"""
{enter_word} значения давления в миллиметрах ртутного столба (мм рт. ст.) в формате: 120 80 (с пробелом, а не '-')
""")
    elif user_choice == "📈Создай график":
        # Records obj, not int
        bp_entries_amount = await db.count_bp_entries(user_id)

        if bool(bp_entries_amount[0]):
            specify_word = "Укажи" if user_full_name else "Укажите"

            await state.set_state(GenerateBPGraphState.waiting_for_period)
            await message.answer(f"""{specify_word} за какой период мне создать график
За один день: 2025-01-01
За период: 2025-01-01 2025-12-31""", reply_markup=cancel_kb)
        else:
            await message.answer("Чтобы я мог сделать график, нужно создать запись")
    elif user_choice == "🔙Назад":
        await state.set_state(MenuState.waiting_for_choice)
        await message.answer("Чем могу быть полезен?", reply_markup=menu_kb)


@router.callback_query(BloodPressureState.waiting_for_choice)
async def show_bp_info_cbq_handler(callback_query) -> None:
    user_id = callback_query.from_user.id
    user_choice = callback_query.data

    user = User.get_user(user_id)

    if user_choice == "Next":
        measurement_dates = user.measurement_dates

        index = user.current_day_index
        new_index = change_day_index(measurement_dates, index, is_previous=False)
        # Update index
        user.current_day_index = new_index

        dates_kb = generate_bp_dates_buttons(measurement_dates, new_index)

        await callback_query.message.edit_text("Даты:", reply_markup=dates_kb)
    elif user_choice == "Previous":
        measurement_dates = user.measurement_dates

        index = user.current_day_index
        new_index = change_day_index(measurement_dates, index)
        # Update index
        user.current_day_index = new_index

        dates_kb = generate_bp_dates_buttons(measurement_dates, new_index)

        await callback_query.message.edit_text("Даты:", reply_markup=dates_kb)
    else:
        # Covert date to date object
        user_date = datetime.strptime(user_choice, "%Y-%m-%d")

        try:
            blood_pressure_entries = await db.fetch_bp_entries_for_day(user_date, user_id)

            message_text = process_bp_entries(blood_pressure_entries)

            await callback_query.message.answer(message_text, reply_markup=bp_kb)
        except Exception:
            await callback_query.message.answer("Я не могу получить ваши записи за эту дату🙁", reply_markup=bp_kb)
