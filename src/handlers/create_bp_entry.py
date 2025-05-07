from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.fsm import BloodPressureState, CreateBPEntryState
from src.keyboard_buttons.blood_pressure_kb_btns import bp_kb
from src.keyboard_buttons.confirm_kb_btns import confirm_kb
from src.keyboard_buttons.leave_empty_kb_btns import leave_empty_kb
from src.models.database_manager import db
from src.models.user_class import User
from src.my_routers import router
from utils.data_processor import convert_number, validate_numeric_string


@router.message(CreateBPEntryState.waiting_for_bp)
async def input_bp_data_msg_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id

    user = User.get_user(user_id)
    user_full_name = user.full_name
    user_gender = user.gender

    you_word = "Ты" if user_full_name else "Вы"

    user_bp = message.text.split()

    if len(user_bp) > 2:
        if user_full_name:
            entered_word = "ввела" if user_gender == "Female" else "ввел"

            await message.answer(f"{you_word} {entered_word} слишком много данных")
            return
        else:
            await message.answer(f"{you_word} ввели слишком много данных")
            return
    elif len(user_bp) < 2:
        if user_full_name:
            entered_word = "ввела" if user_gender == "Female" else "ввел"

            await message.answer(f"{you_word} {entered_word} мало данных")
            return
        else:
            await message.answer(f"{you_word} ввели мало данных")
            return

    is_float, num = validate_numeric_string(*user_bp)

    if is_float:
        user_bp_for_db = [convert_number(user_bp[0]), convert_number(user_bp[1])]
        await state.update_data(user_bp=user_bp_for_db)

        may_word = "можешь" if user_full_name else "можете"
        await state.set_state(CreateBPEntryState.waiting_for_pulse)
        await message.answer(f"Теперь {may_word} указать частоту пульса (количество ударов в минуту, уд/мин) "
                             f"или оставить его пустым", reply_markup=leave_empty_kb)
    else:
        await message.answer(f"Неверный формат - {num}")


@router.message(CreateBPEntryState.waiting_for_pulse)
async def input_pulse_msg_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id

    user = User.get_user(user_id)
    user_full_name = user.full_name

    you_word = "Ты" if user_full_name else "Вы"
    want_word = "хочешь" if user_full_name else "хотите"

    reply_text = (f"может {you_word.lower()} {want_word} оставить замечания (например, свое самочувствие)? "
                  f"Не более 300 символов")

    user_pulse = message.text

    if user_pulse == "Оставь пустым":
        await state.update_data(user_pulse=None)

        await state.set_state(CreateBPEntryState.waiting_for_remark)
        await message.answer(f"Хорошо, {reply_text}", reply_markup=leave_empty_kb)
    else:
        if len(user_pulse.split()) > 1:
            user_gender = user.gender
            if user_full_name:
                entered_word = "ввела" if user_gender == "Female" else "ввел"

                await message.answer(f"{you_word} {entered_word} слишком много данных")
                return
            else:
                await message.answer(f"{you_word} ввели слишком много данных")
                return

        is_float, num = validate_numeric_string(user_pulse)

        if is_float:
            user_pulse_for_db = convert_number(user_pulse)
            await state.update_data(user_pulse=user_pulse_for_db)

            await state.set_state(CreateBPEntryState.waiting_for_remark)
            await message.answer(f"Записал, {reply_text}", reply_markup=leave_empty_kb)
        else:
            await message.answer(f"Неверный формат - {num}")


@router.message(CreateBPEntryState.waiting_for_remark)
async def input_remark_msg_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id

    user = User.get_user(user_id)
    user_full_name = user.full_name

    user_remark = message.text

    if len(user_remark) > 300:
        await message.answer(f"Слишком длинный текст (символов - {len(user_remark)}). "
                             f"Я могу принять не больше 300 символов")
        return

    user_remark_for_db = user_remark if user_remark != "Оставь пустым" else None

    await state.update_data(user_remark=user_remark_for_db)

    bp_data = await state.get_data()

    user_bp = bp_data.get("user_bp")
    user_systolic_pressure = user_bp[0]
    user_diastolic_pressure = user_bp[1]
    user_pulse = bp_data.get("user_pulse")

    confirm_word = "Подтверди" if user_full_name else "Подтвердите"
    message_text = f"""{confirm_word} ✅/❌
Верхнее (систолическое): {user_systolic_pressure}
Нижнее (диастолическое): {user_diastolic_pressure}
Пульс: {user_pulse or "Не указано"}
Замечания: {user_remark_for_db or "Не указано"}\n"""

    await state.set_state(CreateBPEntryState.waiting_for_confirmation)
    await message.answer(message_text, reply_markup=confirm_kb)


@router.message(CreateBPEntryState.waiting_for_confirmation)
async def bp_create_confirmation_msg_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    user_confirm = message.text

    if user_confirm == "Нет❌":
        await state.clear()

        await state.set_state(BloodPressureState.waiting_for_choice)
        await message.answer("В таком случае я не буду это сохранять", reply_markup=bp_kb)
    elif user_confirm == "Да✅":
        try:
            bp_data = await state.get_data()

            systolic_pressure = bp_data.get("user_bp")[0]
            diastolic_pressure = bp_data.get("user_bp")[1]
            pulse = bp_data.get("user_pulse")
            remark = bp_data.get("user_remark")

            await db.create_bp_entry(user_id, systolic_pressure, diastolic_pressure, pulse, remark)
            await db.update_last_activity(user_id)

            await state.clear()

            await state.set_state(BloodPressureState.waiting_for_choice)
            await message.answer("Я записал данные 😃", reply_markup=bp_kb)
        except Exception:
            await state.set_state(BloodPressureState.waiting_for_choice)

            user = User.get_user(user_id)
            user_full_name = user.full_name

            your_word = "Твои" if user_full_name else "Ваши"
            await message.answer(f"Мне очень жаль, но я не смог сохранить {your_word} данные😥", reply_markup=bp_kb)
