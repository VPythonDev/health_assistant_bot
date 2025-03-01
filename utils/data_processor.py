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
    """Processes blood pressure entries"""
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


def check_float(*args):
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


def check_date(*args):
    """Checks whether the string is a date"""
    for date in args:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return False, date

    return True, None


def check_pulse(*args):
    """Checks for pulse in blood pressure data"""
    for data in args:
        if data.get("pulse"):
            return True
    return False
