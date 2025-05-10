def get_bp_category(systolic_value, diastolic_value):
    """Define category of blood pressure by average of systolic and diastolic values"""
    if systolic_value >= 135 and diastolic_value < 85:
        return ("Изолированная систолическая гипертония", "Изолированная систолическая гипертония",
                "Изолированная систолическая гипертония")

    if systolic_value < 135 and diastolic_value >= 85:
        return ("Изолированная диастолическая гипертония", "Изолированная диастолическая гипертония",
                "Изолированная диастолическая гипертония")

    bp_categories = {
        "🔵Гипотония (пониженное давление)":
            {
                "systolic_values": (0, 89.9),
                "diastolic_values": (0, 59.9),
                "level": 1
            },
        "🟢Оптимальное давление":
            {
                "systolic_values": (90, 104.9),
                "diastolic_values": (60, 64.9),
                "level": 2
            },
        "🟢Нормальное давление":
            {
                "systolic_values": (105, 119.9),
                "diastolic_values": (65, 69.9),
                "level": 3
            },
        "🟡Высокое нормальное давление":
            {
                "systolic_values": (120, 134.9),
                "diastolic_values": (70, 84.9),
                "level": 4
            },
        "🟠Гипертония 1 степени":
            {
                "systolic_values": (135, 149.9),
                "diastolic_values": (85, 89.9),
                "level": 5
            },
        "🔴Гипертония 2 степени":
            {
                "systolic_values": (150, 164.9),
                "diastolic_values": (90, 94.9),
                "level": 6
            },
        "🔴Гипертония 3 степени":
            {
                "systolic_values": (165, 1000),
                "diastolic_values": (95, 1000),
                "level": 7
            }
    }

    systolic_level, diastolic_level = 0, 0
    systolic_category, diastolic_category = "Не могу установить", "Не могу установить"

    for category, options in bp_categories.items():
        systolic_min, systolic_max = options["systolic_values"]

        if systolic_min <= systolic_value <= systolic_max:
            systolic_category = category
            systolic_level = options["level"]
            break

    for category, options in bp_categories.items():
        diastolic_min, diastolic_max = options["diastolic_values"]

        if diastolic_min <= diastolic_value <= diastolic_max:
            diastolic_category = category
            diastolic_level = options["level"]
            break

    if systolic_level >= diastolic_level:
        bp_category = systolic_category
    else:
        bp_category = diastolic_category

    return bp_category, systolic_category, diastolic_category


def get_pulse_category(pulse):
    """Define category of pulse by average value"""
    if pulse < 50:
        return "Брадикардия (очень низкий пульс)"
    elif 50 <= pulse <= 59.9:
        return "Пониженный пульс (нижняя граница нормы)"
    elif 60 <= pulse <= 90.9:
        return "Нормальный пульс"
    elif 91 <= pulse <= 100:
        return "Пограничная тахикардия (умеренно повышен)"
    else:
        return "Тахикардия (высокий пульс)"


def analyze_bp(entries):
    """Analyze blood pressure according to records"""
    last_measurement_time = entries[0]["measurement_time"].strftime("%Y-%m-%d %H:%M")
    systolic_values = []
    diastolic_values = []

    for entry in entries:
        systolic_pressure = entry["systolic_pressure"]
        diastolic_pressure = entry["diastolic_pressure"]

        systolic_values.append(systolic_pressure)
        diastolic_values.append(diastolic_pressure)

    # Average values
    avg_systolic = round(sum(systolic_values) / len(systolic_values), 1)
    avg_diastolic = round(sum(diastolic_values) / len(diastolic_values), 1)

    # Definition of blood pressure category
    bp_category, systolic_category, diastolic_category = get_bp_category(avg_systolic, avg_diastolic)

    recommendations = {
        "🔵Гипотония (пониженное давление)":
            "Давление ниже нормы.\n"
            "Возможны слабость, головокружение, потемнение в глазах при вставании.\n"
            "Пейте больше жидкости. Регулярно ешьте, не пропускайте приёмы пищи.\n"
            "Избегайте резкого подъёма из положения лёжа.\n"
            "Если симптомы сохраняются - обратитесь к врачу "
            "для исключения анемии или нарушений гормональной регуляции.",
        "🟢Оптимальное давление":
            "Отличный результат. Продолжайте вести здоровый образ жизни.\n"
            "Если есть факторы риска, контролируйте давление 1–2 раза в неделю.",
        "🟢Нормальное давление":
            "Хороший уровень давления.\n"
            "Поддерживайте здоровый образ жизни:\n"
            "Ограничьте соль (не более 5 г в сутки)\n"
            "Регулярно двигайтесь (ходьба, плавание)\n"
            "Следите за весом и уровнем стресса\n\n"
            "Измеряйте давление 1 раз в неделю или по самочувствию. Если есть факторы риска, то 2-3 раза в неделю.",
        "🟡Высокое нормальное давление":
            "Вероятна артериальная гипертония. Обратитесь к врачу.\n\n"
            "Рекомендуется:\n"
            "Отказаться от курения и алкоголя.\n"
            "Уменьшить потребление соли и сахара.\n"
            "Регулярно двигаться (не менее 30 минут в день).\n\n"
            "Контролируйте давление не реже 3 раз в неделю.",
        "🟠Гипертония 1 степени":
            "Начальная стадия гипертонии. Возможны головные боли, усталость, шум в ушах.\n\n"
            "Необходимо:\n"
            "Консультация врача\n "
            "Коррекция образа жизни\n"
            "Ведение дневника давления (2 раза в день)\n\n"
            "Вероятно, потребуется медикаментозное лечение.",
        "🔴Гипертония 2 степени":
            "Стабильно высокое давление - повышен риск инсульта и инфаркта.\n"
            "Требуется:\n "
            "Обязательная консультация врача.\n"
            " Возможны головные боли, усталость, шум в ушах.\n\n"
            "Необходимо:\n"
            "Консультация врача\n "
            "Начало медикаментозной терапии\n"
            "Отказ от вредных привычек и контроль массы тела\n\n"
            "Не откладывайте визит к врачу.",
        "🔴Гипертония 3 степени":
            "Очень высокое давление, серьёзный риск для жизни.\n"
            "Немедленно обратитесь к врачу.\n"
            "Возможна гипертоническая болезнь с поражением органов-мишеней.\n"
            "Самостоятельное лечение недопустимо.",
    }

    health_advice = recommendations.get(bp_category, "Я не могу оценить и дать рекомендации.")

    result = f"""💓Анализ артериального давления

Анализ по Домашнее измерение (ДМАД) с применением неофициальной классификации давления

Всего записей: {len(entries)}
Дата и время последнего замера: {last_measurement_time}

Среднее давление: {avg_systolic}/{avg_diastolic} мм рт. ст.
Категория давления: {bp_category}

Категория САД (систолического/верхнего): {systolic_category}
Категория ДАД (диастолического/нижнего): {diastolic_category}

Оценка и рекомендации:
{health_advice}"""

    return result


def analyze_pulse(entries):
    """Analyze pulse according to records"""
    pulse_values = []
    last_measurement_time = None

    for entry in entries:
        pulse = entry["pulse"]

        if pulse:
            pulse_values.append(pulse)

            if not last_measurement_time:
                last_measurement_time = entry["measurement_time"].strftime("%Y-%m-%d %H:%M")

    if pulse_values:
        # Average value
        avg_pulse = round(sum(pulse_values) / len(pulse_values), 1)

        # Definition of pulse category
        pulse_category = get_pulse_category(avg_pulse)

        recommendations = {
            "Брадикардия (очень низкий пульс)":
                "Нужно проконсультироваться с врачом, если это сопровождается головокружениями или слабостью.",
            "Пониженный пульс (нижняя граница нормы)":
                "Для большинства людей не вызывает опасений, но важно следить за самочувствием.",
            "Нормальный пульс":
                "Это идеальный диапазон для большинства людей в состоянии покоя, особенно утром после пробуждения.",
            "Пограничная тахикардия (умеренно повышен)":
                "Пульс может быть повышен из-за физической активности, стресса или усталости.\n"
                "Важно проверить, не сопровождается ли это другими симптомами.",
            "Тахикардия (высокий пульс)":
                "При постоянном повышении пульса важно обратиться к врачу, "
                "чтобы исключить заболевания или рассматривать возможные причины "
                "(например, стресс или проблемы с сердцем)."
        }

        health_advice = recommendations.get(pulse_category, "Я не могу оценить и дать рекомендации.")

        result = f"""💗Анализ пульса
    
Всего записей: {len(pulse_values)}
Дата и время последнего замера: {last_measurement_time or "Не могу определить"}
    
Средний пульс: {avg_pulse} уд/мин
Категория пульса: {pulse_category}

Оценка и рекомендации:
{health_advice}"""

        return result
    else:
        return
