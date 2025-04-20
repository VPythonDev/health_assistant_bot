from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.fsm import EditProfileState, MenuState, ProfileState
from src.keyboard_buttons.gender_kb_btns import gender_kb
from src.keyboard_buttons.menu_kb_btns import menu_kb
from src.models.database_manager import db
from src.models.user_class import User
from src.my_routers import router


@router.message(ProfileState.waiting_for_choice)
async def profile_msg_handler(message: Message, state: FSMContext) -> None:
    user_choice = message.text
    user_id = message.from_user.id

    if user_choice == "Измени имя":
        await state.set_state(EditProfileState.waiting_for_full_name)
        await message.answer("Введи новое имя (не больше 200 символов)")
    elif user_choice == "Измени пол":
        await state.set_state(EditProfileState.waiting_for_gender)
        await message.answer("Выбери пол:", reply_markup=gender_kb)
    elif user_choice == "Сделай анонимным":
        try:
            await db.anonymization(user_id)

            user = User.get_user(user_id)
            user.full_name = None
            user.gender = None

            await state.set_state(MenuState.waiting_for_choice)
            await message.answer("Теперь вы анонимны", reply_markup=menu_kb)
        except Exception:
            await message.answer("Мне не удалось выполнить операцию ☹️")
    elif user_choice == "🔙Назад":
        await state.set_state(MenuState.waiting_for_choice)
        await message.answer("Чем могу быть полезен?", reply_markup=menu_kb)
