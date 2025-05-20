import asyncio
from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.fsm import BloodPressureAnalysisState, BloodPressureState
from src.keyboard_buttons.blood_pressure_kb_btns import bp_kb
from src.keyboard_buttons.cancel_kb_btns import cancel_kb
from src.models.database_manager import db
from src.models.user_class import User
from src.my_routers import router
from utils.bp_analyze import analyze_bp, analyze_pulse
from utils.data_processor import validate_datetime_format


@router.message(BloodPressureAnalysisState.waiting_for_type)
async def choose_bp_type_analysis_msg_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    user_choice = message.text

    user = User.get_user(user_id)
    user_full_name = user.full_name

    if user_choice == "🚫Отмена":
        await state.set_state(BloodPressureState.waiting_for_choice)
        await message.answer("Анализ прерван", reply_markup=bp_kb)

    elif user_choice == "Быстрый":
        bp_last_10 = await db.fetch_last_10_bp_entries(user_id)

        if bp_last_10:
            contact_word = "обращайся" if user_full_name else "обращайтесь"
            forget_word = "Не забывай" if user_full_name else "Не забывайте"

            await message.answer(f"""⚠️ВАЖНО:
Я не могу заменить консультацию квалифицированного врача.
Для точной диагностики и получения рекомендаций по лечению всегда {contact_word} к медицинскому специалисту.

{forget_word}, что правильное лечение требует профессионального подхода!""")
            # Pause between messages
            await asyncio.sleep(1)

            bp_analysis = analyze_bp(bp_last_10)
            pulse_analysis = analyze_pulse(bp_last_10)

            await state.set_state(BloodPressureState.waiting_for_choice)
            await message.answer(bp_analysis, reply_markup=bp_kb)
            if pulse_analysis:
                await message.answer(pulse_analysis)

        else:
            you_word = f"тебя, {user_full_name}," if user_full_name else "вас"
            await message.answer(f"Я не могу провести анализ по скольку у {you_word} все еще нет записей о давлении",
                                 reply_markup=bp_kb)

    elif user_choice == "Расширенный":
        await state.set_state(BloodPressureAnalysisState.waiting_for_period)
        await message.answer("""За какой период мне провести анализ?
Пример, как указать период: 
2025-01-01 2025-12-31
(с 2025-01-01 до 2025-12-31, то есть по 30)""", reply_markup=cancel_kb)


@router.message(BloodPressureAnalysisState.waiting_for_period)
async def input_period_msg_handler(message: Message, state: FSMContext) -> None:
    user_message = message.text

    if user_message == "🚫Отмена":
        await state.set_state(BloodPressureState.waiting_for_choice)
        await message.answer("Анализ прерван", reply_markup=bp_kb)
        return

    user_id = message.from_user.id

    start_date = None
    final_date = None

    user_period = user_message.split()
    user_period_len = len(user_period)

    if user_period_len > 2 or user_period_len < 2:
        await message.answer("""Неверный формат. Вот пример:
2025-01-01 2025-12-31 (две даты)
(с 2025-01-01 до 2025-12-31, то есть по 30)""")
        return

    if user_period_len == 2:
        is_date, date = validate_datetime_format(user_period[0], user_period[1])

        if not is_date:
            await message.answer(f"Это не подходящая дата - {date}")
            return
        else:
            start_date = datetime.strptime(user_period[0], "%Y-%m-%d")
            final_date = datetime.strptime(user_period[1], "%Y-%m-%d")

    # Get bp data for period
    bp_data = await db.fetch_bp_entries_for_period(start_date, final_date, user_id)

    if bp_data:
        user = User.get_user(user_id)
        user_full_name = user.full_name

        contact_word = "обращайся" if user_full_name else "обращайтесь"
        forget_word = "Не забывай" if user_full_name else "Не забывайте"

        await message.answer(f"""⚠️ВАЖНО:
Я не могу заменить консультацию квалифицированного врача.
Для точной диагностики и получения рекомендаций по лечению всегда {contact_word} к медицинскому специалисту.

{forget_word}, что правильное лечение требует профессионального подхода!""")
        # Pause between messages
        await asyncio.sleep(1)

        bp_analysis = analyze_bp(bp_data)
        pulse_analysis = analyze_pulse(bp_data)

        await state.set_state(BloodPressureState.waiting_for_choice)
        await message.answer(bp_analysis, reply_markup=bp_kb)
        if pulse_analysis:
            await message.answer(pulse_analysis)
    else:
        start_date_str = start_date.strftime("%Y-%m-%d")
        final_date_str = final_date.strftime("%Y-%m-%d")

        await message.answer(f"Нет записей в период с {start_date_str} до {final_date_str}")
