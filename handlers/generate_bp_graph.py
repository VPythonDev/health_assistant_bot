from datetime import datetime, timedelta

from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message

from utils.data_processor import check_date, check_pulse
from utils.database_manager import db
from utils.fsm import BloodPressureState, GenerateBPGraph
from utils.keyboard_buttons.blood_pressure_kb_btns import bp_kb
from utils.keyboard_buttons.confirm_kb_btns import confirm_kb
from utils.my_routers import router
from utils.report_generator import (generate_bp_graph, generate_bp_report,
                                    generate_pulse_graph)


@router.message(GenerateBPGraph.waiting_for_period)
async def get_period_message_handler(message: Message, state: FSMContext) -> None:
    user_message = message.text

    if user_message == "🚫Отмена":
        await state.set_state(BloodPressureState.waiting_for_choice)
        await message.answer("Хорошо, я не буду создавать график", reply_markup=bp_kb)
        return

    user_id = message.from_user.id

    start_date = None
    final_date = None

    user_period = user_message.split()
    user_period_len = len(user_period)

    if user_period_len > 2:
        await message.answer("""Неверный формат. Повторяю
За один день: 2025-01-01
За период: 2025-01-01 2025-12-31""")
        return
    if user_period_len == 2:
        is_date, date = check_date(user_period[0], user_period[1])

        if not is_date:
            await message.answer(f"Это не подходящая дата - {date}")
            return
        else:
            start_date = datetime.strptime(user_period[0], "%Y-%m-%d")
            final_date = datetime.strptime(user_period[1], "%Y-%m-%d")

    if user_period_len == 1:
        is_date, date = check_date(user_period[0])

        if not is_date:
            await message.answer(f"Это не подходящая дата - {date}")
            return
        else:
            start_date = datetime.strptime(user_period[0], "%Y-%m-%d")
            final_date = start_date + timedelta(days=1)

    # Get bp data for period
    bp_data = await db.fetch_bp_entries_for_period(start_date, final_date, user_id)

    if bp_data:
        have_pulse = check_pulse(*bp_data)

        if have_pulse:
            await state.update_data(bp_data=bp_data)
            await state.set_state(GenerateBPGraph.waiting_for_confirmation)
            await message.answer("Нужно ли учитывать пульс?", reply_markup=confirm_kb)
        else:
            bp_graph_stream = generate_bp_graph(bp_data)

            bp_pdf_stream = generate_bp_report(bp_data, bp_graph_stream)

            bp_pdf = BufferedInputFile(bp_pdf_stream.read(), filename="График_давления.pdf")
            bp_graph_stream.close()

            await state.set_state(BloodPressureState.waiting_for_choice)

            await message.answer_document(bp_pdf, reply_markup=bp_kb)
            bp_pdf_stream.close()
    else:
        start_date_str = start_date.strftime("%Y-%m-%d")
        final_date_str = final_date.strftime("%Y-%m-%d")

        await message.answer(f"Нет записей в период с {start_date_str} до {final_date_str}")


@router.message(GenerateBPGraph.waiting_for_confirmation)
async def get_pulse_message_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    bp_data = data.get("bp_data")

    bp_graph_stream = generate_bp_graph(bp_data)

    user_confirm = message.text
    if user_confirm == "Нет❌":
        bp_pdf_stream = generate_bp_report(bp_data, bp_graph_stream)

        bp_pdf = BufferedInputFile(bp_pdf_stream.read(), filename="График_давления.pdf")
        bp_graph_stream.close()

        await state.clear()
        await state.set_state(BloodPressureState.waiting_for_choice)

        await message.answer_document(bp_pdf, reply_markup=bp_kb)
        bp_pdf_stream.close()
    elif user_confirm == "Да✅":
        pulse_graph_stream = generate_pulse_graph(bp_data)

        bp_pdf_stream = generate_bp_report(bp_data, bp_graph_stream, pulse_graph_stream)

        bp_pdf = BufferedInputFile(bp_pdf_stream.read(), filename="График_давления.pdf")
        bp_graph_stream.close()
        pulse_graph_stream.close()

        await state.clear()
        await state.set_state(BloodPressureState.waiting_for_choice)

        await message.answer_document(bp_pdf, reply_markup=bp_kb)
        bp_pdf_stream.close()
