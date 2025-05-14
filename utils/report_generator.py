import io

import matplotlib.pyplot as plt
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle


def generate_bp_graph(data):
    """Generates pdf graph with blood pressure data"""
    systolic_pressure_data = []
    diastolic_pressure_data = []
    dates = []

    for record_obj in data:
        systolic_pressure = record_obj["systolic_pressure"]
        diastolic_pressure = record_obj["diastolic_pressure"]
        date_time = record_obj["measurement_time"].strftime("%Y-%m-%d\n%H:%M")

        systolic_pressure_data.append(systolic_pressure)
        diastolic_pressure_data.append(diastolic_pressure)
        dates.append(date_time)

    # Вычисляем ширину графика в зависимости от количества точек
    n_points = len(dates)
    width = min(max(24 * n_points / 14, 10), 60)  # минимум 10, максимум 60 дюймов ширина
    height = 6  # фиксированная высота

    plt.figure(figsize=(width, height))  # создаём график нужного размера

    # Generate graph
    plt.plot(
        dates,
        systolic_pressure_data,
        label="Верхнее (систолическое)",
        color="#8B0000",
        marker="o",
        linestyle="-")
    plt.plot(
        dates,
        diastolic_pressure_data,
        label="Нижнее (диастолическое)",
        color="red",
        marker="o",
        linestyle="-")

    plt.xlabel("Дата и время")
    plt.ylabel("Давление (мм рт. ст.)")
    plt.title("Давление")
    plt.legend()
    plt.grid()

    # Сохранение в буфер
    pdf_stream = io.BytesIO()
    plt.savefig(pdf_stream, format="pdf")
    plt.close()

    pdf_stream.seek(0)  # Перемещаем указатель в начало файла
    return pdf_stream


def generate_pulse_graph(data):
    """Generates pdf graph with pulse data"""
    pulses = []
    dates = []

    for record_obj in data:
        pulse = record_obj.get("pulse")

        if pulse:
            date_time = record_obj["measurement_time"].strftime("%Y-%m-%d\n%H:%M")

            pulses.append(pulse)
            dates.append(date_time)

    # Вычисляем ширину графика в зависимости от количества точек
    n_points = len(dates)
    width = min(max(24 * n_points / 14, 10), 60)  # минимум 10, максимум 60 дюймов ширина
    height = 6  # фиксированная высота

    plt.figure(figsize=(width, height))  # создаём график нужного размера

    # Generate graph
    plt.plot(dates, pulses, label="Пульс", color="blue", marker="o", linestyle="-")

    plt.xlabel("Дата и время")
    plt.ylabel("Пульс (уд/мин)")
    plt.title("Пульс")
    plt.legend()
    plt.grid()

    # Сохранение в буфер
    pdf_stream = io.BytesIO()
    plt.savefig(pdf_stream, format="pdf")
    plt.close()

    pdf_stream.seek(0)  # Перемещаем указатель в начало файла
    return pdf_stream


def generate_bp_report(data, bp_pdf_buffer, pulse_pdf_buffer=None):
    """Generate report pdf-file with blood pressure data"""
    bp_report_pdf = io.BytesIO()

    # Читаем исходный PDF
    bp_pdf_reader = PdfReader(bp_pdf_buffer)

    # Создаем PdfWriter для объединения
    pdf_writer = PdfWriter()

    # Добавляем страницы из существующего PDF
    pdf_writer.add_page(bp_pdf_reader.pages[0])

    if pulse_pdf_buffer:
        pulse_pdf_reader = PdfReader(pulse_pdf_buffer)
        pdf_writer.add_page(pulse_pdf_reader.pages[0])

    table_pdf_buffer = io.BytesIO()

    # Styles
    styles = getSampleStyleSheet()
    style = styles["Normal"]

    font_path = "C:\\Windows\\Fonts\\segoeui.ttf"
    pdfmetrics.registerFont(TTFont("Segoe UI", font_path))

    style.fontName = "Segoe UI"

    remark_style = ParagraphStyle(
        'remark_style',
        parent=style,
        fontName="Segoe UI",
        fontSize=10,
        leading=12,
        wordWrap='CJK',  # поддержка переноса длинных слов
        alignment=4,  # 0 = left, 1 = center, 2 = right, 4 = justify
    )

    # Формируем таблицу
    table_data = [["Дата и время", "Систолическое", "Диастолическое"]]
    fields = ["systolic_pressure", "diastolic_pressure"]

    if pulse_pdf_buffer:
        table_data[0].append("Пульс")
        fields.append("pulse")

    table_data[0].append("Замечания")
    fields.append("remark")

    for record_obj in data:
        row = [record_obj["measurement_time"].strftime("%Y-%m-%d %H:%M")]
        for field in fields:
            value = record_obj.get(field) or "-"

            if field == "remark":
                value = Paragraph(str(value), remark_style)

            row.append(value)

        table_data.append(row)

    # Задаём ширины столбцов вручную: 3см, 3см, 3см, 3см, 8см
    col_widths = [3.1 * cm, 3 * cm, 3 * cm]
    if pulse_pdf_buffer:
        col_widths.append(2 * cm)
    col_widths.append(8 * cm)

    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), "Segoe UI"),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # по горизонтали
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # по вертикали
    ]))

    doc = SimpleDocTemplate(table_pdf_buffer, pagesize=A4,
                            rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    doc.build([Paragraph("Таблица измерений артериального давления<br/><br/>", style), table])

    # Чтение таблицы из буфера
    table_pdf_buffer.seek(0)
    table_pdf_reader = PdfReader(table_pdf_buffer)
    for page in table_pdf_reader.pages:
        pdf_writer.add_page(page)

    # Финально сохраняем
    pdf_writer.write(bp_report_pdf)
    bp_report_pdf.seek(0)
    return bp_report_pdf
