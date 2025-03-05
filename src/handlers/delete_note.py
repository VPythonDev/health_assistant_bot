from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.fsm import DeleteNoteState, NotesState
from src.keyboard_buttons.notes_kb_btns import notes_kb
from src.models.database_manager import db
from src.my_routers import router


@router.message(DeleteNoteState.waiting_for_number)
async def delete_note_message_handler(message: Message, state: FSMContext) -> None:
    user_message = message.text

    if user_message == "🚫Отмена":
        await state.set_state(NotesState.waiting_for_choice)
        await message.answer("Удаление отменено", reply_markup=notes_kb)
        return
    elif not user_message.isdigit():
        await message.answer("Это не номер")
    else:
        await state.set_state(NotesState.waiting_for_choice)

        user_id = message.from_user.id
        notes = await db.fetch_notes(user_id)

        if notes:
            index = int(user_message)

            if index > len(notes):
                await message.answer("Такого номера нет")
                return

            note_id = notes[index - 1]["note_id"]

            await db.delete_note(note_id)

            await message.answer("Заметка удалена", reply_markup=notes_kb)
        else:
            await message.answer("Заметок нет", reply_markup=notes_kb)
