def translate_gender(gender):
    """Translates english gender into russian"""
    gender_words = {"Male": "Мужской",
                    "Female": "Женский",
                    "Do not specify": "Не указан"}

    return gender_words.get(gender)


async def get_profile(full_name, gender, reminders_number, notes_number):
    """Get profile info"""
    pass

async def get_anon_profile():
    """Get anonim profile info"""
    pass


async def process_blood_pressure_records(records):
    """Processes blood pressure records"""
    result_message = ""

    for record in records:
        measurement_time = record["measurement_time"]
        systolic_pressure = record["systolic_pressure"]
        diastolic_pressure = record["diastolic_pressure"]

        pulse = record.get("pulse", "Не указано")
        remark = record.get("remark", "Не указано")

        record_text = f"""Дата замера - {measurement_time}

Верхнее (систолическое): {systolic_pressure}
Нижнее (диастолическое): {diastolic_pressure}
Пульс: {pulse}
Замечания:{remark}\n"""

        result_message += record_text

    return result_message
