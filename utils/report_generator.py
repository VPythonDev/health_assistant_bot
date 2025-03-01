import io

import matplotlib.pyplot as plt
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate


def generate_bp_graph(data):
    """Generates pdf graph with blood pressure data"""
    systolic_pressure_data = []
    diastolic_pressure_data = []
    dates = []

    for record_obj in data:
        systolic_pressure = record_obj["systolic_pressure"]
        diastolic_pressure = record_obj["diastolic_pressure"]
        date_time = record_obj["measurement_time"].strftime("%Y-%m-%d %H:%M")

        systolic_pressure_data.append(systolic_pressure)
        diastolic_pressure_data.append(diastolic_pressure)
        dates.append(date_time)

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
            date_time = record_obj["measurement_time"].strftime("%Y-%m-%d %H:%M")

            pulses.append(pulse)
            dates.append(date_time)

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

    remark_text = ""
    for record_obj in data:
        remark = record_obj.get("remark")
        if remark:
            date_time = record_obj["measurement_time"].strftime("%Y-%m-%d %H:%M")
            remark_text += f"{date_time} - {remark}<br/>"  # Используем <br/> для переносов строк

    if remark_text:
        final_remark_text = "".join(["Замечания<br/><br/>", remark_text])
        # Буфер для нового PDF с текстом
        text_pdf_buffer = io.BytesIO()

        styles = getSampleStyleSheet()
        style = styles["Normal"]

        font_path = "C:\\Windows\\Fonts\\segoeui.ttf"
        pdfmetrics.registerFont(TTFont("Segoe UI", font_path))

        style.fontName = "Segoe UI"
        style.encoding = 'utf-8'  # Укажите кодировку

        p = Paragraph(final_remark_text, style)

        # Создаем полноценный PDF с переносами страниц
        doc = SimpleDocTemplate(text_pdf_buffer, pagesize=A4)
        doc.build([p])  # Автоматически переносит текст на новые страницы

        # Теперь добавляем ВСЕ страницы текстового PDF в основной
        text_pdf_buffer.seek(0)
        text_pdf_reader = PdfReader(text_pdf_buffer)

        for page in text_pdf_reader.pages:  # ✅ Перебираем все страницы
            pdf_writer.add_page(page)

    pdf_writer.write(bp_report_pdf)

    bp_report_pdf.seek(0)

    return bp_report_pdf
