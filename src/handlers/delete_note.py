from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.fsm import DeleteNoteState, NotesState
from src.keyboard_buttons.notes_kb_btns import notes_kb
from src.models.database_manager import db
from src.my_routers import router


@router.message(DeleteNoteState.waiting_for_number)
async def delete_note_msg_handler(message: Message, state: FSMContext) -> None:
    user_message = message.text

    if user_message == "🚫Отмена":
        await state.set_state(NotesState.waiting_for_choice)
        await message.answer("Удаление отменено", reply_markup=notes_kb)
        return
    elif not user_message.isdigit():
        await message.answer("Это не номер")
    else:
        user_id = message.from_user.id
        notes = await db.fetch_notes(user_id)

        if notes:
            index = int(user_message)

            if index > len(notes) or index == 0:
                await message.answer("Такого номера нет")
                return

            note_id = notes[index - 1]["note_id"]

            await db.delete_note(note_id)
            await db.update_notes_number(user_id)
            await db.update_last_activity(user_id)

            await state.set_state(NotesState.waiting_for_choice)
            await message.answer("Я удалил заметку", reply_markup=notes_kb)
        else:
            await state.set_state(NotesState.waiting_for_choice)
            await message.answer("Заметок нет", reply_markup=notes_kb)
