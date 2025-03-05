from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.fsm import DeleteReminderState, RemindersState
from src.keyboard_buttons.reminders_kb_btns import reminders_kb
from src.models.database_manager import db
from src.my_routers import router
from src.reminders.reminder import scheduler


@router.message(DeleteReminderState.waiting_for_number)
async def delete_reminder_message_handler(message: Message, state: FSMContext) -> None:
    user_message = message.text

    if user_message == "🚫Отмена":
        await state.set_state(RemindersState.waiting_for_choice)
        await message.answer("Удаление отменено", reply_markup=reminders_kb)
        return
    elif not user_message.isdigit():
        await message.answer("Это не номер")
    else:
        await state.set_state(RemindersState.waiting_for_choice)

        user_id = message.from_user.id
        reminders = await db.fetch_reminders(user_id)

        if reminders:
            index = int(user_message)

            if index > len(reminders):
                await message.answer("Такого номера нет")
                return

            reminder_id = reminders[index - 1]["reminder_id"]

            scheduler.remove_job(reminder_id)

            await message.answer("Удалено", reply_markup=reminders_kb)
        else:
            await message.answer("Напоминаний нет", reply_markup=reminders_kb)
