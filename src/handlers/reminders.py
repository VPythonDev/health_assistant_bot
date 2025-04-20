from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.fsm import (CreateReminderState, DeleteReminderState, MenuState,
                     RemindersState)
from src.keyboard_buttons.cancel_kb_btns import cancel_kb
from src.keyboard_buttons.menu_kb_btns import menu_kb
from src.models.user_class import User
from src.my_routers import router


@router.message(RemindersState.waiting_for_choice)
async def reminders_msg_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    user_choice = message.text

    user = User.get_user(user_id)
    user_full_name = user.full_name

    if user_choice == "❗️Создай напоминание":
        you_word = "тебе" if user_full_name else "вам"

        await state.set_state(CreateReminderState.waiting_for_text)
        await message.answer(f"Что {you_word} напомнить? (не больше 300 символов)")
    elif user_choice == "🗑Удали напоминание":
        write_word = "Напиши" if user_full_name else "Напишите"

        await state.set_state(DeleteReminderState.waiting_for_number)
        await message.answer(f"{write_word} номер напоминания", reply_markup=cancel_kb)
    elif user_choice == "🔙Назад":
        await state.set_state(MenuState.waiting_for_choice)
        await message.answer("Чем могу быть полезен?", reply_markup=menu_kb)
