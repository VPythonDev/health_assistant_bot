import asyncio

from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from utils.database_manager import db
from utils.fsm import MenuState, RegistrationState
from utils.keyboard_buttons.anonymity_kb_btns import anonymity_kb
from utils.keyboard_buttons.menu_kb_btns import menu_kb
from utils.my_routers import router
from utils.user_class import User


@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id

    try:
        is_registered = await db.check_registration(user_id)
        if is_registered:
            try:
                full_name, gender, reminders_number, notes_number = await db.get_user_data(user_id)

                User(user_id, full_name, gender)

                # Change state for menu
                await state.set_state(MenuState.waiting_for_choice)

                # Greeting
                if full_name:
                    await message.answer(f"Здравствуйте, {full_name}!", reply_markup=menu_kb)
                else:
                    await message.answer("Здравствуйте", reply_markup=menu_kb)
            except Exception:
                await message.answer("Я не могу сейчас получить ваши данные. Попробуйте позже")
        else:
            await message.answer(
                "Привет, я бот-ассистент по здоровью. Я помогу вам следить за вашим здоровьем, пока вы "
                "занимаетесь своими делами")

            # Pause between messages
            await asyncio.sleep(5)
            await message.answer("Вижу вы здесь в первый раз. Вам необходимо зарегистрироваться для того, чтобы я "
                                 "стал вашим персональным ассистентом. Если вы хотите зарегестрироваться, ответьте на "
                                 "вопрос")

            await state.set_state(RegistrationState.waiting_for_anonymity)
            await message.answer("Вы хотите остаться анонимным?", reply_markup=anonymity_kb)
    except Exception:
        await message.answer(f"Произошла ошибка при проверке вашей регистрации. Попробуйте позже")
