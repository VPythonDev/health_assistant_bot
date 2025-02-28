from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from utils.database_manager import db
from utils.fsm import AnonimProfileState, DeanonymizationState, ProfileState
from utils.keyboard_buttons.anon_edit_profile_kb_btns import \
    anonim_edit_profile_kb
from utils.keyboard_buttons.edit_profile_kb_btns import edit_profile_kb
from utils.my_routers import router
from utils.user_class import User


@router.message(DeanonymizationState.waiting_for_name)
async def deanonymization_handler(message: Message, state: FSMContext) -> None:
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
        await message.answer(f"Мне не удалось обновить ваши данные 🙁", reply_markup=anonim_edit_profile_kb)
        await state.set_state(AnonimProfileState.waiting_for_choice)
