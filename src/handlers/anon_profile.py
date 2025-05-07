from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.fsm import AnonimProfileState, DeanonymizationState, MenuState
from src.keyboard_buttons.menu_kb_btns import menu_kb
from src.my_routers import router


@router.message(AnonimProfileState.waiting_for_choice)
async def anon_profile_msg_handler(message: Message, state: FSMContext) -> None:
    user_choice = message.text

    if user_choice == "Деанонимизироваться":
        await state.set_state(DeanonymizationState.waiting_for_name)

        await message.answer("Введите имя, чтобы я знал, как к вам обращаться")
    elif user_choice == "🔙Назад":
        await state.set_state(MenuState.waiting_for_choice)
        await message.answer("Чем могу быть полезен?", reply_markup=menu_kb)
