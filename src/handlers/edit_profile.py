from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.fsm import EditProfileState, ProfileState
from src.keyboard_buttons.edit_profile_kb_btns import edit_profile_kb
from src.models.database_manager import db
from src.models.user_class import User
from src.my_routers import router


@router.message(EditProfileState.waiting_for_full_name)
async def edit_full_name_msg_handler(message: Message, state: FSMContext) -> None:
    new_user_full_name = message.text

    # Checking that user enters name less than 200 symbols
    if len(new_user_full_name) > 200:
        await message.answer("Имя не может быть больше 200 символов")
        return

    # Change full name
    user_id = message.from_user.id

    try:
        await db.update_user_full_name(user_id, new_user_full_name)

        user = User.get_user(user_id)
        user.full_name = new_user_full_name

        await message.answer(f"Новое имя: {new_user_full_name}", reply_markup=edit_profile_kb)
        await state.set_state(ProfileState.waiting_for_choice)
    except Exception:
        await message.answer("Не получается сохранить новое имя 🙁",
                             reply_markup=edit_profile_kb)
        await state.set_state(ProfileState.waiting_for_choice)


@router.callback_query(EditProfileState.waiting_for_gender)
async def edit_gender_cbq_handler(callback_query, state: FSMContext) -> None:
    await callback_query.message.delete()

    user_id = callback_query.from_user.id
    new_user_gender = callback_query.data

    # Change gender
    try:
        await db.update_gender(user_id, new_user_gender)

        user = User.get_user(user_id)
        user.gender = new_user_gender

        await callback_query.message.answer("Пол изменен", reply_markup=edit_profile_kb)
        await state.set_state(ProfileState.waiting_for_choice)
    except Exception:
        await callback_query.message.answer("У меня не получилось сохранить изменения 🙁", reply_markup=edit_profile_kb)
        await state.set_state(ProfileState.waiting_for_choice)
