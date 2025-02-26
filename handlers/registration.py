import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from utils.database_manager import db
from utils.fsm import MenuState, RegistrationState
from utils.keyboard_buttons.anonymity_kb_btns import anonymity_kb
from utils.keyboard_buttons.gender_kb_btns import gender_kb
from utils.keyboard_buttons.menu_kb_btns import menu_kb
from utils.my_routers import router
from utils.user_class import User


@router.callback_query(RegistrationState.waiting_for_anonymity)
async def anonymity_callback_query_handler(callback_query, state: FSMContext) -> None:
    user_id = callback_query.from_user.id

    # Create user
    User(user_id)

    user_anonymity_choice = callback_query.data
    if user_anonymity_choice == "Anonim":
        await callback_query.message.edit_text("Хорошо. Ваш выбор будет учтен")

        # Add user in database
        is_registered = await db.registration(user_id)

        if is_registered:
            await callback_query.message.answer("Вы зарегистрированы 😀", reply_markup=menu_kb)
            await state.set_state(MenuState.waiting_for_choice)
        else:
            await callback_query.message.answer("Я не смог вас зарегистрировать ☹️")
            await callback_query.message.answer("Вы хотите остаться анонимным?",
                                                reply_markup=anonymity_kb)
    elif user_anonymity_choice == "Not anonim":
        await callback_query.message.delete()

        # Pause between messages
        await asyncio.sleep(1)
        await callback_query.message.answer("Чтобы я знал, как к вам обращаться, напишите ваше имя. Это может быть "
                                            "псевдоним, ФИО или все, что вам угодно, но не длиннее 200 символов")
        await state.set_state(RegistrationState.waiting_for_full_name)


@router.message(RegistrationState.waiting_for_full_name)
async def full_name_handler(message: Message, state: FSMContext) -> None:
    user_full_name = message.text

    # Checking that user enters name less than 200 symbols
    if len(user_full_name) > 200:
        await message.answer("Имя не может быть больше 200 символов. Пожалуйста, введите имя, чтобы я знал, "
                             "как к вам обращаться")
        return

    user_id = message.from_user.id

    user = User.get_user(user_id)
    user.full_name = user_full_name

    await message.answer(f"Ваше имя: {user_full_name}")

    await state.set_state(RegistrationState.waiting_for_gender)
    await message.answer("Теперь выберите ваш пол", reply_markup=gender_kb)


@router.callback_query(RegistrationState.waiting_for_gender)
async def gender_callback_query_handler(callback_query, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    user_gender = callback_query.data

    # Set user gender
    user = User.get_user(user_id)
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
        await callback_query.message.answer(message_text, reply_markup=menu_kb)
        await state.set_state(MenuState.waiting_for_choice)

    else:
        await callback_query.message.answer("К сожалению сейчас я не могу вас зарегистрировать 🙁")
        await state.clear()


@router.message(RegistrationState.waiting_for_gender)
async def gender_message_handler(message: Message) -> None:
    await message.answer("Вы не выбрали пол. Под этим сообщением находятся кнопки для выбора пола. Пожалуйста "
                         "выберите пол, нажав на одну из кнопок", reply_markup=gender_kb)
