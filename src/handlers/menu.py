from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.fsm import (AnonimProfileState, BloodPressureState, MenuState,
                     NotesState, ProfileState, RemindersState)
from src.keyboard_buttons.anon_edit_profile_kb_btns import \
    anonim_edit_profile_kb
from src.keyboard_buttons.blood_pressure_kb_btns import (
    bp_kb, generate_bp_dates_buttons)
from src.keyboard_buttons.edit_profile_kb_btns import edit_profile_kb
from src.keyboard_buttons.menu_kb_btns import menu_kb
from src.keyboard_buttons.notes_kb_btns import notes_kb
from src.keyboard_buttons.reminders_kb_btns import reminders_kb
from src.models.database_manager import db
from src.models.user_class import User
from src.my_routers import router
from utils.data_processor import process_notes, process_reminders


@router.message(MenuState.waiting_for_choice)
async def menu_msg_handler(message: Message, state: FSMContext) -> None:
    user_choice = message.text
    user_id = message.from_user.id

    # Get user data
    full_name, gender, reminders_number, notes_number = await db.fetchrow_user_data(user_id)
    # User object
    user = User.get_user(user_id)

    if user_choice == "👤Профиль":
        try:
            if full_name:
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
                user.measurement_dates = measurement_dates
                user.current_day_index = 0

                # Generate keyboard buttons of dates by bp measurement dates
                dates_kb = generate_bp_dates_buttons(measurement_dates, 0)

                await message.answer("Даты:", reply_markup=dates_kb)
                await state.set_state(BloodPressureState.waiting_for_choice)

                choose_word = "Выбери" if full_name else "Выберите"
                await message.answer(f"🔝{choose_word} дату", reply_markup=bp_kb)
            else:
                await message.answer("Записей нет", reply_markup=bp_kb)
                await state.set_state(BloodPressureState.waiting_for_choice)
        except Exception:
            await message.answer("Я не могу получить записи🙁")
    elif user_choice == "🔔Напоминания":
        await state.set_state(RemindersState.waiting_for_choice)

        reminders = await db.fetch_reminders(user_id)

        if reminders:
            reminders_message = process_reminders(reminders)

            await message.answer(reminders_message, reply_markup=reminders_kb)
        else:
            await message.answer("Напоминаний нет", reply_markup=reminders_kb)
    elif user_choice == "📓Заметки":
        await state.set_state(NotesState.waiting_for_choice)

        notes = await db.fetch_notes(user_id)

        if notes:
            notes_message = process_notes(notes)

            await message.answer(notes_message, reply_markup=notes_kb)
        else:
            await message.answer("Заметок нет", reply_markup=notes_kb)
