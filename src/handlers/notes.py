from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.fsm import CreateNoteState, DeleteNoteState, MenuState, NotesState
from src.keyboard_buttons.cancel_kb_btns import cancel_kb
from src.keyboard_buttons.menu_kb_btns import menu_kb
from src.models.user_class import User
from src.my_routers import router


@router.message(NotesState.waiting_for_choice)
async def notes_msg_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    user_choice = message.text

    user = User.get_user(user_id)
    user_full_name = user.full_name

    if user_choice == "Создай заметку":
        may_word = "Можешь" if user_full_name else "Можете"

        await state.set_state(CreateNoteState.waiting_for_text)
        await message.answer(f"Текст должен быть не больше 2000 символов. {may_word} писать")
    elif user_choice == "Удали заметку":
        write_word = "Напиши" if user_full_name else "Напишите"

        await state.set_state(DeleteNoteState.waiting_for_number)
        await message.answer(f"{write_word} номер заметки", reply_markup=cancel_kb)
    elif user_choice == "🔙Назад":
        await state.set_state(MenuState.waiting_for_choice)
        await message.answer("Чем могу быть полезен?", reply_markup=menu_kb)
