import uuid
from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.fsm import CreateReminderState, MenuState, RemindersState
from src.keyboard_buttons.menu_kb_btns import menu_kb
from src.keyboard_buttons.reminder_types_kb_btns import (reminder_types_kb,
                                                         repeat_modes_kb)
from src.keyboard_buttons.reminders_kb_btns import reminders_kb
from src.models.database_manager import db
from src.models.user_class import User
from src.my_routers import router
from src.reminders.reminder import scheduler
from src.reminders.reminder_func import send_reminder
from utils.data_processor import (convert_day_of_week, convert_months,
                                  validate_datetime_format)


@router.message(CreateReminderState.waiting_for_text)
async def input_reminder_text_msg_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id

    user_reminder_text = message.text

    await state.update_data(reminder_text=user_reminder_text)

    user = User.get_user(user_id)
    user_full_name = user.full_name

    choose_word = "выбери" if user_full_name else "выберите"

    await state.set_state(CreateReminderState.waiting_for_type)
    await message.answer(f"Теперь {choose_word} вид напоминания", reply_markup=reminder_types_kb)


@router.callback_query(CreateReminderState.waiting_for_type)
async def input_reminder_type_cbq_handler(callback_query, state: FSMContext):
    user_id = callback_query.from_user.id
    reminder_type = callback_query.data

    user = User.get_user(user_id)
    user_full_name = user.full_name

    if reminder_type == "Single":
        await state.update_data(trigger="date")

        write_word = "Напиши" if user_full_name else "Напишите"

        await state.set_state(CreateReminderState.waiting_for_date_time)
        await callback_query.message.edit_text(f"{write_word} дату и время в формате - Июль 02 12:00")
    elif reminder_type == "Repeated":
        choose_word = "Выбери" if user_full_name else "Выберите"

        await state.set_state(CreateReminderState.waiting_for_mode)
        await callback_query.message.edit_text(f"{choose_word} режим", reply_markup=repeat_modes_kb)


@router.message(CreateReminderState.waiting_for_date_time)
async def create_reminder_msg_handler(message: Message, state: FSMContext):
    user_date_time = message.text.split()

    if len(user_date_time) < 3:
        await message.answer("Мало данных. Пример - Июль 02 12:00")
        return

    month = convert_months(user_date_time[0])

    if month:
        current_year = str(datetime.now().year)
        reminder_date_time = f"{current_year}-{month[0]}-{user_date_time[1]} {user_date_time[2]}"

        is_date_time, date_time = validate_datetime_format(reminder_date_time, frmt="%Y-%m-%d %H:%M")

        if is_date_time:
            data = await state.get_data()

            trigger = data.get("trigger")

            user_id = message.from_user.id
            reminder_text = data.get("reminder_text")

            reminder_id = str(uuid.uuid4())

            reminder_data = {
                "func": send_reminder,
                "trigger": trigger,
                "kwargs": {"user_id": user_id, "reminder_text": reminder_text},
                "id": reminder_id
            }

            parsed_date_time = datetime.strptime(reminder_date_time, "%Y-%m-%d %H:%M")

            if trigger == "date":
                reminder_data["run_date"] = parsed_date_time
            elif trigger == "interval":
                reminder_data["seconds"] = data.get("seconds")
                reminder_data["minutes"] = data.get("minutes")
                reminder_data["hours"] = data.get("hours")
                reminder_data["days"] = data.get("days")
                reminder_data["weeks"] = data.get("weeks")

                reminder_data["start_date"] = parsed_date_time
            elif trigger == "cron":
                reminder_data["minute"] = data.get("minute")
                reminder_data["hour"] = data.get("hour")
                reminder_data["day_of_week"] = data.get("day_of_week")
                reminder_data["day"] = data.get("day")
                reminder_data["month"] = data.get("month")

                reminder_data["start_date"] = parsed_date_time

            try:
                print(reminder_data)
                scheduler.add_job(**reminder_data)
            except Exception:
                await state.clear()
                await state.set_state(RemindersState.waiting_for_choice)
                await message.answer("Некорректные данные, я не могу создать напоминание", reply_markup=reminders_kb)
            else:
                parameters = data.get("parameters") or reminder_date_time
                did_create = await db.create_reminder(reminder_id, trigger, reminder_text, parameters, user_id)

                await state.clear()

                if did_create:
                    await db.update_reminders_number(user_id)
                    await db.update_last_activity(user_id)

                    await state.set_state(MenuState.waiting_for_choice)
                    await message.answer("Я создал напоминание😀", reply_markup=menu_kb)
                else:
                    try:
                        # There is a bug with trigger date
                        # If user input passed date, it will be an error that id doesn't exist
                        scheduler.remove_job(id=reminder_id)
                    except Exception:
                        pass

                    await state.set_state(RemindersState.waiting_for_choice)

                    await message.answer("Я не смог создать напоминание🙁", reply_markup=reminders_kb)
        else:
            await message.answer(f"Неверный формат даты и времени - {reminder_date_time}")
    else:
        await message.answer("Такого месяца нет")


@router.callback_query(CreateReminderState.waiting_for_mode)
async def input_reminder_mode_cbq_handler(callback_query, state: FSMContext):
    user_id = callback_query.from_user.id
    reminder_mode = callback_query.data

    user = User.get_user(user_id)
    user_full_name = user.full_name

    if reminder_mode == "Interval":
        await state.update_data(trigger="interval")

        await state.set_state(CreateReminderState.waiting_for_interval)

        write_word = "Укажи" if user_full_name else "Укажите"

        await callback_query.message.edit_text(f"""{write_word} интервал

Единицы времени: секунда, минута, час, день, неделя

Пример: 1 час 2 дня 30 минут (сработает через 2 дня, 1 час и 30 минут)

Главное - чтобы числовое значение было перед единицей времени""")
    elif reminder_mode == "Cron":
        await state.update_data(trigger="cron")

        await state.set_state(CreateReminderState.waiting_for_cron_schedule)

        may_word = f"{user_full_name}, ты можешь" if user_full_name else "Вы можете"

        await callback_query.message.edit_text(f"""{may_word} написать конкретные числа или периоды.
Конкретные числа: 1,2,5 10,12,31
Периоды: 0-12 5-10
Дни недели можно указать словами - понедельник,вторник и т.д.

Формат:
минуты [значение]
часы [значение]
дни недели [значение]
дни месяца [значение]
месяцы [значение]

⚠️Между названиями секций (например, *часы*, *дни недели*) обязательно должен быть пробел.
Значения внутри секции (например, *9,12,15*) пишутся без пробелов.

Примеры:
дни недели понедельник-среда,суббота
часы 9,12,15
(с понедельника по среду и в субботу в 9, 12 и 15 часов)

минуты 0-30,35 месяцы 1-12
(с января по декабрь с 0 по 30 и в 35 минут)""")


@router.message(CreateReminderState.waiting_for_interval)
async def input_reminder_interval_msg_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id

    user = User.get_user(user_id)
    user_full_name = user.full_name

    user_interval = message.text.lower()

    intervals_dict = {"seconds": 0, "minutes": 0, "hours": 0, "days": 0, "weeks": 0}
    time_units = {"сек": "seconds", "мин": "minutes", "час": "hours", "дн": "days", "день": "days", "нед": "weeks"}

    for rus_time_unit, time_unit in time_units.items():
        rus_time_unit_index = user_interval.find(rus_time_unit)

        if rus_time_unit_index != -1:
            subinterval = user_interval[:rus_time_unit_index].split()

            if not subinterval:
                write_word = "Укажи" if user_full_name else "Укажите"

                await message.answer(f"{write_word} значение в виде числа перед "
                                     f"'{user_interval[rus_time_unit_index:]}', а не после")
                return

            time_value = subinterval[-1]

            if time_value.isdigit():
                intervals_dict[time_unit] = int(time_value)
            else:
                repeat_word = "Повтори" if user_full_name else "Повторите"

                await message.answer(f"Это не целое положительное число - {time_value}. {repeat_word} еще раз")
                return

    if all(value == 0 for value in intervals_dict.values()):
        reply_text = """Параметры указаны неверно.
Интервал можно задать в секундах, минутах, часах, днях или неделях"""

        await message.answer(reply_text)
        return

    await state.update_data(**intervals_dict)
    await state.update_data(parameters=message.text)

    write_word = "Напиши" if user_full_name else "Напишите"

    await state.set_state(CreateReminderState.waiting_for_date_time)
    await message.answer(f"{write_word} дату и время запуска напоминания в формате - Июль 02 12:00")


@router.message(CreateReminderState.waiting_for_cron_schedule)
async def input_reminder_cron_schedule_msg_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id

    user = User.get_user(user_id)
    user_full_name = user.full_name

    user_schedule = message.text.split()

    if len(user_schedule) < 2:
        await message.answer("Мало данных или нет пробела")
        return

    schedule_dict = {"minute": None, "hour": None, "day_of_week": None, "day": None, "month": None}

    for i, time_unit in enumerate(["минуты", "часы", "недели", "месяца", "месяцы"]):
        if time_unit in user_schedule:
            index = user_schedule.index(time_unit)

            time_values = user_schedule[index + 1]
            # time values without - and ,
            replaced_time_values = time_values.replace("-", "").replace(",", "")

            if replaced_time_values.isdigit():
                key = list(schedule_dict.keys())[i]
                schedule_dict[key] = time_values
            elif replaced_time_values.isalpha():
                time_values_list = time_values.replace("-", " ").replace(",", " ").split()

                list_for_replace = [time_values, time_values_list]

                for day_of_week in list_for_replace[1]:
                    converted_day_of_week = convert_day_of_week(day_of_week)

                    if converted_day_of_week:
                        list_for_replace[0] = list_for_replace[0].replace(day_of_week, converted_day_of_week)
                    else:
                        await message.answer(f"Это не подходящий день недели - {day_of_week}")
                        return

                key = list(schedule_dict.keys())[i]
                schedule_dict[key] = list_for_replace[0]
            else:
                await message.answer(f"Это значение не подходит - {time_values}")
                return

    if all(value is None for value in schedule_dict.values()):
        await message.answer("Неверный формат. Можно указать - минуты, часы, дни недели, дни месяца, месяцы")
        return

    await state.update_data(**schedule_dict)
    await state.update_data(parameters=" ".join(user_schedule))

    write_word = "Напиши" if user_full_name else "Напишите"

    await state.set_state(CreateReminderState.waiting_for_date_time)
    await message.answer(f"{write_word} дату и время запуска напоминания в формате - Июль 02 12:00")
