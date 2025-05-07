from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.fsm import AnonimProfileState, DeanonymizationState, ProfileState
from src.keyboard_buttons.anon_edit_profile_kb_btns import \
    anonim_edit_profile_kb
from src.keyboard_buttons.edit_profile_kb_btns import edit_profile_kb
from src.models.database_manager import db
from src.models.user_class import User
from src.my_routers import router


@router.message(DeanonymizationState.waiting_for_name)
async def deanonymization_msg_handler(message: Message, state: FSMContext) -> None:
    user_full_name = message.text

    # Checking that user enters name less than 200 symbols
    if len(user_full_name) > 200:
        await message.answer("Имя не может быть больше 200 символов. Пожалуйста, введите имя, чтобы я знал, "
                             "как к вам обращаться")
        return

    # User deanonymization
    user_id = message.from_user.id

    try:
        await db.deanonymization(user_id, user_full_name)

        # Change user in users
        user = User.get_user(user_id)
        user.full_name = user_full_name
        user.gender = "Do not specify"

        await message.answer(f"Твое имя: {user_full_name}", reply_markup=edit_profile_kb)
        await state.set_state(ProfileState.waiting_for_choice)
    except Exception:
        await message.answer("Мне не удалось обновить ваши данные 🙁", reply_markup=anonim_edit_profile_kb)
        await state.set_state(AnonimProfileState.waiting_for_choice)
