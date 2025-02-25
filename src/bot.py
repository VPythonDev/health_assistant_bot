import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.dispatcher.router import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import CommandStart
from utils import database_manager, keyboard_buttons, user_class
import utils.fsm as fsm

BOT_API_TOKEN = os.getenv("bot_token")

# Bot
bot = Bot(token=BOT_API_TOKEN)
dispatcher = Dispatcher()

# Routers
router = Router()

# Add routers in dispatcher
dispatcher.include_router(router)

# Database
db = database_manager.Database()

# Users dict
users = {}


@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id

    try:
        is_registered = await db.check_registration(user_id)
        if is_registered:
            try:
                full_name, gender, reminders_number, notes_number = await db.get_user_data(user_id)

                users[user_id] = user_class.User(user_id, full_name, gender)

                # Change state for menu
                await state.set_state(fsm.MenuState.waiting_for_choice)

                # Greeting
                if full_name:
                    await message.answer(f"Здравствуйте, {full_name}!",
                                         reply_markup=keyboard_buttons.menu_keyboard)
                else:
                    await message.answer("Здравствуйте", reply_markup=keyboard_buttons.menu_keyboard)
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

            await state.set_state(fsm.RegistrationState.waiting_for_anonymity)
            await message.answer("Вы хотите остаться анонимным?", reply_markup=keyboard_buttons.anonim_keyboard)
    except Exception:
        await message.answer(f"Произошла ошибка при проверке вашей регистрации. Попробуйте позже")


@router.callback_query(fsm.RegistrationState.waiting_for_anonymity)
async def anonymity_callback_query_handler(callback_query, state: FSMContext) -> None:
    user_id = callback_query.from_user.id

    # Create user and add in users
    users[user_id] = user_class.User(user_id)

    user_anonymity_choice = callback_query.data
    if user_anonymity_choice == "Anonim":
        await callback_query.message.edit_text("Хорошо. Ваш выбор будет учтен")

        # Add user in database
        is_registered = await db.registration(user_id)

        if is_registered:
            await callback_query.message.answer("Вы зарегистрированы 😀", reply_markup=keyboard_buttons.menu_keyboard)
            await state.set_state(fsm.MenuState.waiting_for_choice)
        else:
            await callback_query.message.answer("Регистрация не удалась 🙁")
            await callback_query.message.answer("Вы хотите остаться анонимным?",
                                                reply_markup=keyboard_buttons.anonim_keyboard)
    elif user_anonymity_choice == "Not anonim":
        await callback_query.message.delete()

        # Pause between messages
        await asyncio.sleep(1)
        await callback_query.message.answer("Чтобы я знал, как к вам обращаться, напишите ваше имя. Это может быть "
                                            "псевдоним, ФИО или все, что вам угодно, но не длиннее 200 символов")
        await state.set_state(fsm.RegistrationState.waiting_for_full_name)


@router.message(fsm.RegistrationState.waiting_for_full_name)
async def full_name_handler(message: Message, state: FSMContext) -> None:
    user_full_name = message.text.strip()

    # Checking that user enters name less than 100 symbols
    if len(user_full_name) > 200:
        await message.answer("Имя не может быть больше 200 символов. Пожалуйста, введите имя, чтобы я знал, "
                             "как к вам обращаться")
        return

    user_id = message.from_user.id

    user = users[user_id]
    user.full_name = user_full_name

    await message.answer(f"Ваше имя: {user_full_name}")

    await state.set_state(fsm.RegistrationState.waiting_for_gender)
    await message.answer("Теперь выберите ваш пол", reply_markup=keyboard_buttons.gender_keyboard)


@router.callback_query(fsm.RegistrationState.waiting_for_gender)
async def gender_callback_query_handler(callback_query, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    user_gender = callback_query.data

    # Set user gender
    user = users[user_id]
    user.gender = user_gender

    await callback_query.message.edit_text("Вы выбрали пол")

    user_full_name = user.full_name
    is_registered = await db.registration(user_id, user_full_name, user_gender)

    # Pause between messages
    await asyncio.sleep(1)

    if is_registered:
        if user_gender == "Female":
            message_text = "Ты зарегистрирована 😀"
        else:
            message_text = "Ты зарегистрирован 😀"
        await callback_query.message.answer(message_text, reply_markup=keyboard_buttons.menu_keyboard)
        await state.set_state(fsm.MenuState.waiting_for_choice)

    else:
        await callback_query.message.answer("К сожалению сейчас я не могу вас зарегистрировать 🙁")
        await state.clear()


@router.message(fsm.RegistrationState.waiting_for_gender)
async def gender_message_handler(message: Message) -> None:
    await message.answer("Вы не выбрали пол. Под этим сообщением находятся кнопки для выбора пола. Пожалуйста "
                         "выберите пол, нажав на одну из кнопок", reply_markup=keyboard_buttons.gender_keyboard)


@router.message(fsm.MenuState.waiting_for_choice)
async def menu_handler(message: Message, state: FSMContext) -> None:
    user_choice = message.text
    user_id = message.from_user.id

    if user_choice == "👤Профиль":
        try:
            # Get user data
            full_name, gender, reminders_number, notes_number = await db.get_user_data(user_id)

            if full_name:
                user = users[user_id]
                gender = user.translate_gender()

                message_text = f"""*Профиль*
    
Твое имя: *{full_name}*
Твой пол: *{gender}*
Количество твоих напоминаний: *{reminders_number}*
Количество твоих заметок: *{notes_number}*"""

                await state.set_state(fsm.ProfileState.waiting_for_choice)
                await message.answer(message_text, parse_mode="MarkdownV2",
                                     reply_markup=keyboard_buttons.edit_profile_keyboard)
            else:
                message_text = f"""*Профиль*
    
Ваше имя: *Не указано* \\(анонимный\\)
Ваш пол: *Не указано* \\(анонимный\\)
Количество ваших напоминаний: *{reminders_number}*
Количество ваших заметок: *{notes_number}*"""

                await state.set_state(fsm.AnonimProfileState.waiting_for_choice)
                await message.answer(message_text, parse_mode="MarkdownV2",
                                     reply_markup=keyboard_buttons.anonim_edit_profile_keyboard)
        except Exception:
            await state.set_state(fsm.MenuState.waiting_for_choice)
            await message.answer("Не удается получить данные профиля😢", reply_markup=keyboard_buttons.menu_keyboard)

    elif user_choice == "🫀Дневник давления":
        pass
    elif user_choice == "🔔Напоминания":
        pass
    elif user_choice == "✍️Заметки":
        pass


@router.message(fsm.ProfileState.waiting_for_choice)
async def profile_handler(message: Message, state: FSMContext) -> None:
    user_choice = message.text
    user_id = message.from_user.id

    if user_choice == "Изменить имя":
        await state.set_state(fsm.EditProfileState.waiting_for_full_name)
        await message.answer("Введите новое имя (не больше 200 символов)")
    elif user_choice == "Изменить пол":
        await state.set_state(fsm.EditProfileState.waiting_for_gender)
        await message.answer("Выбери пол:", reply_markup=keyboard_buttons.gender_keyboard)
    elif user_choice == "Стать анонимным":
        try:
            await db.anonymization(user_id)

            await state.set_state(fsm.MenuState.waiting_for_choice)
            await message.answer("Теперь вы анонимны", reply_markup=keyboard_buttons.menu_keyboard)
        except Exception:
            await message.answer("Не удалось выполнить операцию ☹️")
    elif user_choice == "🔙Назад":
        await state.set_state(fsm.MenuState.waiting_for_choice)
        await message.answer("Чем могу быть полезен?", reply_markup=keyboard_buttons.menu_keyboard)


@router.message(fsm.EditProfileState.waiting_for_full_name)
async def edit_full_name_handler(message: Message, state: FSMContext) -> None:
    new_user_full_name = message.text.strip()

    # Checking that user enters name less than 100 symbols
    if len(new_user_full_name) > 200:
        await message.answer("Имя не может быть больше 200 символов")
        return

    # Change full name
    user_id = message.from_user.id

    try:
        await db.update_user_full_name(user_id, new_user_full_name)

        user = users[user_id]
        user.full_name = new_user_full_name

        await message.answer(f"Новое имя: {new_user_full_name}",
                             reply_markup=keyboard_buttons.edit_profile_keyboard)
        await state.set_state(fsm.ProfileState.waiting_for_choice)
    except Exception:
        await message.answer(f"Не удалось сохранить новое имя 🙁",
                             reply_markup=keyboard_buttons.edit_profile_keyboard)
        await state.set_state(fsm.ProfileState.waiting_for_choice)


@router.callback_query(fsm.EditProfileState.waiting_for_gender)
async def edit_gender_callback_query_handler(callback_query, state: FSMContext) -> None:
    await callback_query.message.delete()

    user_id = callback_query.from_user.id
    new_user_gender = callback_query.data

    # Change gender
    try:
        await db.update_gender(user_id, new_user_gender)

        user = users[user_id]
        user.gender = new_user_gender

        await callback_query.message.answer(f"Пол изменен", reply_markup=keyboard_buttons.edit_profile_keyboard)
        await state.set_state(fsm.ProfileState.waiting_for_choice)
    except Exception:
        await callback_query.message.answer(f"Не удалось сохранить изменения 🙁",
                                            reply_markup=keyboard_buttons.edit_profile_keyboard)
        await state.set_state(fsm.ProfileState.waiting_for_choice)


@router.message(fsm.AnonimProfileState.waiting_for_choice)
async def anon_profile_handler(message: Message, state: FSMContext) -> None:
    user_choice = message.text
    user_id = message.from_user.id

    if user_choice == "Деанонимизация":
        await state.set_state(fsm.DeanonymizationState.waiting_for_name)

        await message.answer("Чтобы я знал, как к вам обращаться, напишите ваше имя. Это может быть псевдоним, "
                             "ФИО или все, что вам угодно, но не длиннее 200 символов")
    elif user_choice == "🔙Назад":
        await state.set_state(fsm.MenuState.waiting_for_choice)
        await message.answer("Чем могу быть полезен?", reply_markup=keyboard_buttons.menu_keyboard)


@router.message(fsm.DeanonymizationState.waiting_for_name)
async def deanonymization_handler(message: Message, state: FSMContext) -> None:
    user_full_name = message.text.strip()

    # Checking that user enters name less than 100 symbols
    if len(user_full_name) > 200:
        await message.answer("Имя не может быть больше 200 символов. Пожалуйста, введите имя, чтобы я знал, "
                             "как к вам обращаться")
        return

    # User deanonymization
    user_id = message.from_user.id

    try:
        await db.deanonymization(user_id, user_full_name)

        # Change user in users
        user = users[user_id]
        user.full_name = user_full_name
        user.gender = "Do not specify"

        await message.answer(f"Твое имя: {user_full_name}",
                             reply_markup=keyboard_buttons.edit_profile_keyboard)
        await state.set_state(fsm.ProfileState.waiting_for_choice)
    except Exception:
        await message.answer(f"Не удалось обновить ваши данные 🙁",
                             reply_markup=keyboard_buttons.anonim_edit_profile_keyboard)
        await state.set_state(fsm.AnonimProfileState.waiting_for_choice)



# @dispatcher.message()
# async def test(message: Message) -> None:
#     chat = message.chat
#     username = chat.username
#     first_name = chat.first_name
#     last_name = chat.last_name
#     full_name = chat.full_name
#
#     user = message.from_user
#     user_id = user.id
#
#     await message.answer(f"{username}, {first_name}, {last_name}, {full_name}")
#     await message.answer(f"{user_id}")
#     await message.answer("Hello, " + "d" * 200)


async def start():
    """Start bot"""
    try:
        await db.init_pool()
        await bot.delete_webhook(True)
        await dispatcher.start_polling(bot)
    finally:
        await db.close_connections()

asyncio.run(start())
