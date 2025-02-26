from utils.my_routers import router
from utils.fsm import MenuState, ProfileState, AnonimProfileState
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from utils.user_class import User
from utils.keyboard_buttons.edit_profile_kb_btns import edit_profile_kb
from utils.keyboard_buttons.anon_edit_profile_kb_btns import anonim_edit_profile_kb
from utils.keyboard_buttons.menu_kb_btns import menu_kb
from utils.database_manager import db

from utils.data_processor import process_blood_pressure_records


@router.message(MenuState.waiting_for_choice)
async def menu_handler(message: Message, state: FSMContext) -> None:
    user_choice = message.text
    user_id = message.from_user.id

    if user_choice == "👤Профиль":
        try:
            # Get user data
            full_name, gender, reminders_number, notes_number = await db.get_user_data(user_id)

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
            await state.set_state(MenuState.waiting_for_choice)
            await message.answer("Мне не удалось получить данные профиля😢", reply_markup=menu_kb)
    elif user_choice == "🫀Дневник давления":
        try:
            measurement_dates = await db.get_measurement_dates(user_id)

            # Last day records
            if measurement_dates:
                # Set dates in user
                user = User.get_user(user_id)
                user.measurement_dates = measurement_dates

                # Obj asyncpg.Record than data
                last_day = measurement_dates[0][0]
                blood_pressure_records = await db.get_blood_pressure_records(last_day, user_id)

                message_text = await process_blood_pressure_records(blood_pressure_records)

                await message.answer(message_text)
            else:
                await message.answer("Записей нет")
        except Exception:
            await state.set_state(MenuState.waiting_for_choice)
            await message.answer(f"Я не могу получить записи🙁")
    elif user_choice == "🔔Напоминания":
        pass
    elif user_choice == "✍️Заметки":
        pass
