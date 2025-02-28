from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from utils.database_manager import db
from utils.fsm import (AnonimProfileState, BloodPressureState, MenuState,
                       ProfileState)
from utils.keyboard_buttons.anon_edit_profile_kb_btns import \
    anonim_edit_profile_kb
from utils.keyboard_buttons.blood_pressure_kb_btns import (
    bp_kb, generate_bp_dates_buttons)
from utils.keyboard_buttons.edit_profile_kb_btns import edit_profile_kb
from utils.keyboard_buttons.menu_kb_btns import menu_kb
from utils.my_routers import router
from utils.user_class import User


@router.message(MenuState.waiting_for_choice)
async def menu_handler(message: Message, state: FSMContext) -> None:
    user_choice = message.text
    user_id = message.from_user.id

    if user_choice == "👤Профиль":
        try:
            # Get user data
            full_name, gender, reminders_number, notes_number = await db.fetchrow_user_data(user_id)

            if full_name:
                user = User.get_user(user_id)
                gender = user.translate_gender()

                message_text = f"""Профиль

Твое имя: {full_name}
Твой пол: {gender}
Количество твоих напоминаний: {reminders_number}
Количество твоих заметок: {notes_number}"""

                await state.set_state(ProfileState.waiting_for_choice)
                await message.answer(message_text, reply_markup=edit_profile_kb)
            else:
                message_text = f"""Профиль

Ваше имя: Не указано (анонимный)
Ваш пол: Не указано (анонимный)
Количество ваших напоминаний: {reminders_number}
Количество ваших заметок: {notes_number}"""

                await state.set_state(AnonimProfileState.waiting_for_choice)
                await message.answer(message_text, reply_markup=anonim_edit_profile_kb)
        except Exception:
            await message.answer("Мне не удалось получить данные профиля😢", reply_markup=menu_kb)
    elif user_choice == "🫀Дневник давления":
        try:
            measurement_dates = await db.fetch_measurement_dates(user_id)

            if measurement_dates:
                # Set dates in user and index to 0
                user = User.get_user(user_id)
                user.measurement_dates = measurement_dates
                user.current_day_index = 0

                # Last day records
                dates_kb = await generate_bp_dates_buttons(measurement_dates, 0)

                await message.answer("Даты:", reply_markup=dates_kb)
                await state.set_state(BloodPressureState.waiting_for_choice)
                await message.answer("🔝Выберите дату", reply_markup=bp_kb)
            else:
                await message.answer("Записей нет", reply_markup=bp_kb)
                await state.set_state(BloodPressureState.waiting_for_choice)
        except Exception:
            await message.answer(f"Я не могу получить записи🙁")
    elif user_choice == "🔔Напоминания":
        pass
    elif user_choice == "✍️Заметки":
        pass
