from datetime import datetime


def get_profile(full_name, gender, reminders_number, notes_number):
    """Get profile info"""
    pass


def get_anon_profile():
    """Get anonim profile info"""
    pass


def change_day_index(dates, index, is_previous=True):
    """Check index before scrolling dates and change, if out of index in date"""
    if is_previous:
        if index + 5 <= len(dates) - 1:
            return index + 5
        else:
            return index
    else:
        if index - 5 >= 0:
            return index - 5
        else:
            return 0


def process_bp_entries(entries):
    """Create message text with blood pressure data"""
    format_num = lambda num: int(num) if num == int(num) else num

    # Date
    measurement_date_time = entries[0]["measurement_time"]
    measurement_date = measurement_date_time.strftime("%Y-%m-%d")

    result_message = f"Дата - {measurement_date}\n"

    for entry in entries:
        measurement_time = entry["measurement_time"].strftime("%H:%M")
        systolic_pressure = format_num(entry["systolic_pressure"])
        diastolic_pressure = format_num(entry["diastolic_pressure"])

        pulse = format_num(entry.get("pulse")) if entry.get("pulse") else "Не указано"
        remark = entry.get("remark") or "Не указано"

        record_text = f"""\nВремя замера - {measurement_time}
Верхнее (систолическое): {systolic_pressure}
Нижнее (диастолическое): {diastolic_pressure}
Пульс: {pulse}
Замечания: {remark}\n"""

        result_message += record_text

    return result_message


def validate_numeric_string(*args):
    """checks whether the string is a number"""
    for num in args:
        replaced_num = num.replace(".", "", 1)
        if not replaced_num.isdigit() or "-" in num:
            return False, num

    return True, None


def convert_number(number_str):
    """Converts number from str to int or float"""
    if "." in number_str and number_str.index(".") < 4:
        return float(number_str[:5])
    else:
        return int(number_str[:3])


def validate_datetime_format(*args, frmt="%Y-%m-%d"):
    """Checks whether the string is datetime"""
    for date_time in args:
        try:
            datetime.strptime(date_time, frmt)
        except ValueError:
            return False, date_time

    return True, None


def check_pulse(*args):
    """Checks for pulse in blood pressure data"""
    for data in args:
        if data.get("pulse"):
            return True
    return False


def convert_months(*months):
    """Convert months to number format"""
    months_dict = {
        "январь": "01",
        "февраль": "02",
        "март": "03",
        "апрель": "04",
        "май": "05",
        "июнь": "06",
        "июль": "07",
        "август": "08",
        "сентябрь": "09",
        "октябрь": "10",
        "ноябрь": "11",
        "декабрь": "12",
    }

    converted_months = []

    for month in months:
        converted_months.append(months_dict.get(month.lower()))

    return tuple(converted_months)


def convert_day_of_week(day):
    """Convert day of week to english format"""
    days_of_week_dict = {
        "понедельник": "MON",
        "вторник": "TUE",
        "среда": "WED",
        "четверг": "THU",
        "пятница": "FRI",
        "суббота": "SAT",
        "воскресенье": "SUN"
    }

    return days_of_week_dict.get(day.lower())


def process_reminders(reminders):
    """Create message text with reminders data"""
    rus_types = {"date": "Одноразовый",
                 "interval": "Интервал",
                 "cron": "Определенное время"}

    result_message = ""

    for i, record_obj in enumerate(reminders):
        reminder_type = record_obj["reminder_type"]
        text = record_obj["reminder_text"]

        rus_type = rus_types.get(reminder_type)

        if rus_type != "date":
            parameters = record_obj["parameters"]

            result_message += f"""\n{i + 1}) Вид: {rus_type}
Параметры: {parameters}
{text}\n"""
        else:
            result_message += f"""\n{i + 1}) Вид: {rus_type}
{text}\n"""

    return result_message


def process_notes(notes):
    """Create message text with notes"""
    result_message = ""

    for i, record_obj in enumerate(notes):
        text = record_obj["note_text"]

        result_message += f"\n{i + 1}) {text}\n"

    return result_message
