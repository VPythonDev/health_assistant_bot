import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.fsm import MenuState, RegistrationState
from src.keyboard_buttons.anonymity_kb_btns import anonymity_kb
from src.keyboard_buttons.gender_kb_btns import gender_kb
from src.keyboard_buttons.menu_kb_btns import menu_kb
from src.models.database_manager import db
from src.models.user_class import User
from src.my_routers import router


@router.callback_query(RegistrationState.waiting_for_anonymity)
async def choose_anonymity_cbq_handler(callback_query, state: FSMContext) -> None:
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
        await asyncio.sleep(0.5)
        await callback_query.message.answer("В таком случае, как я могу к вам обращаться?")
        await state.set_state(RegistrationState.waiting_for_full_name)


@router.message(RegistrationState.waiting_for_full_name)
async def input_full_name_msg_handler(message: Message, state: FSMContext) -> None:
    user_full_name = message.text

    # Checking that user enters name less than 200 symbols
    if len(user_full_name) > 200:
        await message.answer("К сожалению, я не могу запомнить имя больше 200 символов. "
                             "Пожалуйста, введите имя, чтобы я знал, как к вам обращаться")
        return

    user_id = message.from_user.id

    user = User.get_user(user_id)
    user.full_name = user_full_name

    await message.answer(f"Ваше имя: {user_full_name}")

    await state.set_state(RegistrationState.waiting_for_gender)
    await message.answer("Теперь выберите ваш пол", reply_markup=gender_kb)


@router.callback_query(RegistrationState.waiting_for_gender)
async def choose_gender_cbq_handler(callback_query, state: FSMContext) -> None:
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
        await callback_query.message.answer("К сожалению, сейчас я не могу вас зарегистрировать 🙁")
        await state.clear()


@router.message(RegistrationState.waiting_for_gender)
async def repeat_choose_gender_msg_handler(message: Message) -> None:
    await message.answer("Вы не выбрали пол. Под этим сообщением находятся кнопки. Пожалуйста, "
                         "выберите пол, нажав на одну из кнопок", reply_markup=gender_kb)
