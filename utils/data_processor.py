async def get_profile(full_name, gender, reminders_number, notes_number):
    """Get profile info"""
    pass


async def get_anon_profile():
    """Get anonim profile info"""
    pass


async def change_day_index(dates, index, is_previous=True):
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


async def process_bp_entries(entries):
    """Processes blood pressure entries"""
    # Date
    measurement_date_time = entries[0]["measurement_time"]
    measurement_date = measurement_date_time.strftime("%Y-%m-%d")

    result_message = f"Дата - {measurement_date}\n"

    for entry in entries:
        measurement_time = entry["measurement_time"].strftime("%H:%M")
        systolic_pressure = entry["systolic_pressure"]
        diastolic_pressure = entry["diastolic_pressure"]

        pulse = entry.get("pulse") or "Не указано"
        remark = entry.get("remark") or "Не указано"

        record_text = f"""\nВремя замера - {measurement_time}
Верхнее (систолическое): {systolic_pressure}
Нижнее (диастолическое): {diastolic_pressure}
Пульс: {pulse}
Замечания: {remark}\n"""

        result_message += record_text

    return result_message


async def check_float(*args):
    """checks whether the string is a number"""
    for num in args:
        replaced_num = num.replace(".", "", 1)
        if not replaced_num.isdigit() or "-" in num:
            return False, num

    return True, None


async def convert_number(number_str):
    """Converts number from str to int or float"""
    if "." in number_str and number_str.index(".") < 4:
        return float(number_str[:5])
    else:
        return int(number_str[:3])
