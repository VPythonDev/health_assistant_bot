from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.fsm import CreateNoteState, NotesState
from src.models.database_manager import db
from src.models.user_class import User
from src.my_routers import router


@router.message(CreateNoteState.waiting_for_text)
async def create_note_msg_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(NotesState.waiting_for_choice)

    user_id = message.from_user.id

    was_create = await db.create_note(user_id, message.text)

    if was_create:
        await db.update_notes_number(user_id)
        await db.update_last_activity(user_id)

        user = User.get_user(user_id)
        user_full_name = user.full_name

        user_addressing = f"{user_full_name}, я" if user_full_name else "Я"

        await message.answer(f"{user_addressing} создал заметку🙂")
    else:
        await message.answer("У меня не получилось создать заметку🙁")
