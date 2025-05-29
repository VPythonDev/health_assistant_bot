from decimal import Decimal, ROUND_HALF_UP


def get_bp_category(systolic_value, diastolic_value):
    """Define category of blood pressure by average of systolic and diastolic values"""
    if systolic_value >= Decimal('135') and diastolic_value < Decimal('85'):
        return ("Изолированная систолическая гипертония", "Изолированная систолическая гипертония",
                "Изолированная систолическая гипертония")

    if systolic_value < Decimal('135') and diastolic_value >= Decimal('85'):
        return ("Изолированная диастолическая гипертония", "Изолированная диастолическая гипертония",
                "Изолированная диастолическая гипертония")

    bp_categories = {
        "🔵Гипотония (пониженное давление)":
            {
                "systolic_values": (Decimal('0'), Decimal('89.9')),
                "diastolic_values": (Decimal('0'), Decimal('59.9')),
                "level": 1
            },
        "🟢Оптимальное давление":
            {
                "systolic_values": (Decimal('90'), Decimal('104.9')),
                "diastolic_values": (Decimal('60'), Decimal('64.9')),
                "level": 2
            },
        "🟢Нормальное давление":
            {
                "systolic_values": (Decimal('105'), Decimal('119.9')),
                "diastolic_values": (Decimal('65'), Decimal('69.9')),
                "level": 3
            },
        "🟡Высокое нормальное давление":
            {
                "systolic_values": (Decimal('120'), Decimal('134.9')),
                "diastolic_values": (Decimal('70'), Decimal('84.9')),
                "level": 4
            },
        "🟠Гипертония 1 степени":
            {
                "systolic_values": (Decimal('135'), Decimal('149.9')),
                "diastolic_values": (Decimal('85'), Decimal('89.9')),
                "level": 5
            },
        "🔴Гипертония 2 степени":
            {
                "systolic_values": (Decimal('150'), Decimal('164.9')),
                "diastolic_values": (Decimal('90'), Decimal('94.9')),
                "level": 6
            },
        "🔴Гипертония 3 степени":
            {
                "systolic_values": (Decimal('165'), Decimal('1000')),
                "diastolic_values": (Decimal('95'), Decimal('1000')),
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


def is_out_of_normal(systolic, diastolic):
    if systolic < Decimal('90') or diastolic < Decimal('60'):
        return True
    if systolic > Decimal('119.9') or diastolic > Decimal('69.9'):
        return True
    return False


def calculate_bp_deviation_percentage(systolic_values, diastolic_values):
    deviations = 0

    i = 0
    while i < len(systolic_values):
        systolic_value = systolic_values[i]
        diastolic_value = diastolic_values[i]

        if is_out_of_normal(systolic_value, diastolic_value):
            deviations += 1

        i += 1

    total = len(systolic_values)

    return Decimal((deviations / total) * 100).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)


def get_pulse_category(pulse):
    """Define category of pulse by average value"""
    if pulse < Decimal('50'):
        return "🟣Брадикардия (очень низкий пульс)"
    elif Decimal('50') <= pulse <= Decimal('59.9'):
        return "🟣Пониженный пульс (нижняя граница нормы)"
    elif Decimal('60') <= pulse <= Decimal('90.9'):
        return "🟢Нормальный пульс"
    elif Decimal('91') <= pulse <= Decimal('100'):
        return "🟢Пограничная тахикардия (умеренно повышен)"
    else:
        return "🔴Тахикардия (высокий пульс)"


def analyze_bp(entries, is_advanced=False):
    """Analyze blood pressure according to records"""
    last_measurement_time = entries[-1]["measurement_time"].strftime("%Y-%m-%d %H:%M")
    systolic_values = []
    diastolic_values = []

    for entry in entries:
        systolic_pressure = entry["systolic_pressure"]
        diastolic_pressure = entry["diastolic_pressure"]

        systolic_values.append(systolic_pressure)
        diastolic_values.append(diastolic_pressure)

    # Average values
    avg_systolic = (sum(systolic_values) / len(systolic_values)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
    avg_diastolic = (sum(diastolic_values) / len(diastolic_values)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)

    # Definition of blood pressure category
    bp_category, systolic_category, diastolic_category = get_bp_category(avg_systolic, avg_diastolic)

    result = f"""💓Анализ артериального давления

Анализ по домашнему измерению (ДМАД) с применением адаптированной классификации давления

Всего записей: {len(entries)}
Дата и время последнего замера: {last_measurement_time}

Среднее давление: {avg_systolic}/{avg_diastolic} мм рт. ст.
Категория давления: {bp_category}

Категория САД (систолического/верхнего): {systolic_category}
Категория ДАД (диастолического/нижнего): {diastolic_category}"""

    if is_advanced:
        # Max and min systolic and diastolic pressure
        max_systolic = max(systolic_values)
        min_systolic = min(systolic_values)

        max_diastolic = max(diastolic_values)
        min_diastolic = min(diastolic_values)

        deviation_percentage = calculate_bp_deviation_percentage(systolic_values, diastolic_values)

        pulse_pressure_values = []

        for systolic_value, diastolic_value in zip(systolic_values, diastolic_values):
            pulse_pressure = systolic_value - diastolic_value
            pulse_pressure_values.append(pulse_pressure)

        avg_pulse_pressure = (sum(pulse_pressure_values) / len(pulse_pressure_values)).quantize(Decimal('0.1'),
                                                                                                rounding=ROUND_HALF_UP)

        advanced_part = f"""

Дополнительный анализ

Максимальные значения: {max_systolic}/{max_diastolic} (САД/ДАД)
Минимальные значения: {min_systolic}/{min_diastolic} (САД/ДАД)

Среднее пульсовое давление: {avg_pulse_pressure} мм рт. ст.
Процент отклонений от нормы: {deviation_percentage}%"""
        result += advanced_part

    recommendations = {
        "🔵Гипотония (пониженное давление)":
            "Давление ниже нормы.\n"
            "Возможны слабость, головокружение, потемнение в глазах при вставании.\n"
            "Пейте больше жидкости. Регулярно ешьте, не пропускайте периоды приёма пищи.\n"
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
            "Давление находится на верхней границе нормы. "
            "Это может быть предвестником развития гипертонии, особенно при наличии факторов риска.\n\n"
            "Рекомендуется:\n"
            "Отказаться от курения и алкоголя.\n"
            "Уменьшить потребление соли и сахара.\n"
            "Регулярно двигаться (не менее 30 минут в день).\n\n"
            "Контролируйте давление не реже трех раз в неделю.",
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
            "Возможны головные боли, усталость, шум в ушах.\n\n"
            "Необходимо:\n"
            "Консультация врача\n"
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

    result += f"""

Оценка и рекомендации:
{health_advice}"""

    return result


def analyze_pulse(entries, is_advanced=False):
    """Analyze pulse according to records"""
    pulse_values = []
    last_measurement_time = None

    for entry in entries:
        pulse = entry["pulse"]

        if pulse:
            pulse_values.append(pulse)

            last_measurement_time = entry["measurement_time"].strftime("%Y-%m-%d %H:%M")

    if pulse_values:
        # Average value
        avg_pulse = (sum(pulse_values) / len(pulse_values)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)

        # Definition of pulse category
        pulse_category = get_pulse_category(avg_pulse)

        result = f"""💗Анализ пульса

Всего записей: {len(pulse_values)}
Дата и время последнего замера: {last_measurement_time or "Не могу определить"}

Средний пульс: {avg_pulse} уд/мин
Категория пульса: {pulse_category}"""

        if is_advanced:
            # Max and min
            max_pulse = max(pulse_values)
            min_pulse = min(pulse_values)

            difference_pulse = max_pulse - min_pulse

            advanced_part = f"""

Дополнительный анализ

Максимальное значение: {max_pulse} уд/мин
Минимальное значение: {min_pulse} уд/мин

Разница: {difference_pulse} уд/мин"""
            result += advanced_part

        recommendations = {
            "🟣Брадикардия (очень низкий пульс)":
                "Нужно проконсультироваться с врачом, если это сопровождается головокружениями или слабостью.",
            "🟣Пониженный пульс (нижняя граница нормы)":
                "Для большинства людей не вызывает опасений, но важно следить за самочувствием.",
            "🟢Нормальный пульс":
                "Это идеальный диапазон для большинства людей в состоянии покоя, особенно утром после пробуждения.",
            "🟢Пограничная тахикардия (умеренно повышен)":
                "Пульс может быть повышен из-за физической активности, стресса или усталости.\n"
                "Важно проверить, не сопровождается ли это другими симптомами.",
            "🔴Тахикардия (высокий пульс)":
                "При постоянном повышении пульса важно обратиться к врачу, "
                "чтобы исключить заболевания или рассматривать возможные причины "
                "(например, стресс или проблемы с сердцем)."
        }

        health_advice = recommendations.get(pulse_category, "Я не могу оценить и дать рекомендации.")

        result += f"""

Оценка и рекомендации:
{health_advice}"""

        return result
    else:
        return
