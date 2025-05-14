import asyncio

from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.fsm import MenuState, RegistrationState
from src.keyboard_buttons.anonymity_kb_btns import anonymity_kb
from src.keyboard_buttons.menu_kb_btns import menu_kb
from src.models.database_manager import db
from src.models.user_class import User
from src.my_routers import router


@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id

    try:
        is_registered = await db.check_registration(user_id)
        if is_registered:
            try:
                full_name, gender, reminders_number, notes_number = await db.fetchrow_user_data(user_id)

                User(user_id, full_name, gender)

                # Change state for menu
                await state.set_state(MenuState.waiting_for_choice)

                # Greeting
                if full_name:
                    await message.answer(f"Привет, {full_name}! Рад снова тебя видеть!", reply_markup=menu_kb)
                else:
                    await message.answer("Здравствуйте, рад снова вас видеть!", reply_markup=menu_kb)
            except Exception:
                await message.answer("😵Я не могу сейчас получить ваши данные. Попробуйте позже")
        else:
            await message.answer("""
Привет, я бот-ассистент по здоровью. Я помогу вам следить за здоровьем.

В мои возможности входят:
📕 Ведение дневника артериального давления
📊 Построение графика по записям дневника
🔍 Анализ показателей давления для выявления признаков гипертонии
⏰ Напоминания с разными настройками времени
✏️ Запись заметок
""")
            # Pause between messages
            await asyncio.sleep(5)
            await message.answer("Вижу, вы здесь в первый раз. Если хотите, "
                                 "чтобы я стал вашим персональным ассистентом, мне необходимо вас зарегистрировать. "
                                 "Пожалуйста, ответьте на вопрос и я проведу регистрацию")

            await state.set_state(RegistrationState.waiting_for_anonymity)
            await message.answer("Вы хотите остаться анонимным?", reply_markup=anonymity_kb)
    except Exception:
        await message.answer("😵Произошла ошибка при проверке вашей регистрации. Попробуйте позже")
