import os

from django.conf import settings
from django.http import HttpResponse

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

SIZE_FONT = 18
HEADER_TEXT = 'Foodgram - список покупок'
FONT_NAME = 'DejaVuSans'
LOGO_FILENAME = 'logo.png'
LOGO_HEIGHT = 50
LOGO_WIDTH = 50


def add_logo(pdf, y_cord_start):
    """Функция добавления logo в заголовок PDF-файла."""
    logo_path = os.path.join(
        settings.STATIC_ROOT, 'logo', LOGO_FILENAME
    )
    x_cord_center = (A4[0] - LOGO_WIDTH) / 2.0
    y_cord_start = y_cord_start - LOGO_HEIGHT
    pdf.drawImage(
        logo_path, x_cord_center, y_cord_start, width=LOGO_WIDTH,
        height=LOGO_HEIGHT, preserveAspectRatio=True, mask='auto')
    return y_cord_start - 10


def download_pdf_file(annotated_results):
    """
    Запись результатов аннотирования в PDF с последующим скачиванием
    файла.
    """
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="file.pdf"'
    pdf = canvas.Canvas(response)
    x_cord = 1 * inch
    y_cord_start = A4[1] * 0.95
    y_cord_start = add_logo(pdf, y_cord_start)
    font_path = os.path.join(
        settings.STATIC_ROOT, 'font', f'{FONT_NAME}.ttf'
    )
    pdfmetrics.registerFont(TTFont(FONT_NAME, font_path))

    pdf.setFont(FONT_NAME, SIZE_FONT)
    header_width = stringWidth(HEADER_TEXT, 'DejaVuSans', SIZE_FONT)
    x_cord_center = (A4[0] - header_width) / 2.0
    pdf.drawString(
        x_cord_center, y_cord_start,
        HEADER_TEXT
    )
    y_cord = y_cord_start - SIZE_FONT * 2
    pdf.setFont(FONT_NAME, SIZE_FONT * 0.8)
    for num, item in enumerate(annotated_results, start=1):
        pdf.drawString(
            x_cord, y_cord,
            f'{num}. {item}: {item.sum_ingredients}'
            f' {item.measurement_unit}'
        )
        y_cord -= SIZE_FONT * 1.1
        if y_cord <= y_cord_start * 0.05:
            pdf.showPage()
            y_cord = y_cord_start
            pdf.setFont(FONT_NAME, SIZE_FONT)
    pdf.save()
    return response
