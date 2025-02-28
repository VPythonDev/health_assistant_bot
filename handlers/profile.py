from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from utils.database_manager import db
from utils.fsm import EditProfileState, MenuState, ProfileState
from utils.keyboard_buttons.gender_kb_btns import gender_kb
from utils.keyboard_buttons.menu_kb_btns import menu_kb
from utils.my_routers import router
from utils.user_class import User


@router.message(ProfileState.waiting_for_choice)
async def profile_handler(message: Message, state: FSMContext) -> None:
    user_choice = message.text
    user_id = message.from_user.id

    if user_choice == "Измени имя":
        await state.set_state(EditProfileState.waiting_for_full_name)
        await message.answer("Введите новое имя (не больше 200 символов)")
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
