import os
from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Paragraph

from ..config import settings

MID_BLUE = HexColor("#3454a8")
LIGHT_BLUE = HexColor("#75defe")
TEXT_DARK = HexColor("#1a1a1a")
TEXT_GREY = HexColor("#55575c")
DARK_BLUE = HexColor("#0d1f6e")


def _draw_header_waves(c: canvas.Canvas, width: float, height: float):
    """Two overlapping solid-color wave bands across the top (the filled
    version), purely decorative."""
    band_height = 3.6 * cm
    top = height

    c.setFillColor(LIGHT_BLUE)
    p = c.beginPath()
    p.moveTo(0, top)
    p.lineTo(0, top - band_height)
    p.curveTo(width * 0.35, top - band_height * 1.6, width * 0.6, top - band_height * 0.3, width, top - band_height * 1.1)
    p.lineTo(width, top)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    c.setFillColor(DARK_BLUE)
    p2 = c.beginPath()
    p2.moveTo(0, top)
    p2.lineTo(0, top - band_height * 0.75)
    p2.curveTo(width * 0.3, top - band_height * 1.3, width * 0.55, top - band_height * 0.15, width * 0.78, top - band_height * 0.55)
    p2.curveTo(width * 0.9, top - band_height * 0.75, width * 0.95, top - band_height * 0.5, width, top - band_height * 0.6)
    p2.lineTo(width, top)
    p2.close()
    c.drawPath(p2, fill=1, stroke=0)

    

def _draw_justified_paragraph(c: canvas.Canvas, text: str, x: float, y: float, width: float, font_size: int = 11, leading: float = 16) -> float:
    style = ParagraphStyle(
        name="Body", fontName="Helvetica", fontSize=font_size, leading=leading,
        alignment=TA_JUSTIFY, textColor=TEXT_DARK,
    )
    para = Paragraph(text, style)
    _, para_height = para.wrap(width, 1000)
    para.drawOn(c, x, y - para_height)
    return y - para_height


def generate_certificate(
    student_id: str,
    student_name: str,
    course_name: str,
    domain: str,
    start_date: date,
    end_date: date,
) -> str:
    """
    Renders a course completion certificate as a PDF, styled after a
    hand-sketched letterhead layout: thin wave line-art, a letter+arch logo
    mark, centered course-center name, then a justified letter body.
    Returns the absolute file path. Signature is fixed to settings.SIGNATORY_NAME.
    """
    filename = f"certificate_{student_id}.pdf"
    filepath = os.path.join(settings.CERTIFICATES_DIR, filename)

    width, height = A4
    c = canvas.Canvas(filepath, pagesize=A4)
    left = 2.5 * cm
    right = width - 2.5 * cm
    content_width = right - left

    c.setFillColor(HexColor("#ffffff"))
    c.rect(0, 0, width, height, fill=1, stroke=0)

    _draw_header_waves(c, width, height)

    

    # Course center name, centered, up to two lines
    name_y = height - 5.9 * cm
    c.setFillColor(LIGHT_BLUE)
    name_text = settings.COURSE_CENTER_NAME.upper()
    name_font_size = 20
    max_name_width = content_width
    while stringWidth(name_text, "Helvetica-Bold", name_font_size) > max_name_width and name_font_size > 11:
        name_font_size -= 1
    c.setFont("Helvetica-Bold", name_font_size)
    c.drawCentredString(width / 2, name_y, name_text)
    y = name_y - 1.5 * cm

    # Title
    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(TEXT_DARK)
    title = "Course Completion Certificate"
    c.drawCentredString(width / 2, y, title)
    c.setStrokeColor(TEXT_DARK)
    c.setLineWidth(0.8)
    tw = stringWidth(title, "Helvetica-Bold", 15)
    c.line(width / 2 - tw / 2, y - 0.22 * cm, width / 2 + tw / 2, y - 0.22 * cm)

    # "To whomsoever it may concern"
    y -= 1.2 * cm
    c.setFont("Helvetica-Bold", 11.5)
    c.setFillColor(TEXT_DARK)
    concern = "To Whomsoever It May Concern"
    c.drawCentredString(width / 2, y, concern)
    cw = stringWidth(concern, "Helvetica-Bold", 11.5)
    c.setLineWidth(0.7)
    c.line(width / 2 - cw / 2, y - 0.18 * cm, width / 2 + cw / 2, y - 0.18 * cm)

    # Body paragraph 1 — fully justified
    y -= 1.3 * cm
    body1 = (
        f"This is to certify that {student_name} has successfully completed the course "
        f"\"{course_name}\" in the domain of {domain} at {settings.COURSE_CENTER_NAME}, "
        f"conducted from {start_date.strftime('%d-%m-%y')} to {end_date.strftime('%d-%m-%y')}."
    )
    y = _draw_justified_paragraph(c, body1, left, y, content_width)

    # Body paragraph 2
    y -= 0.5 * cm
    body2 = (
        "During the course, the student demonstrated consistent effort, sincerity, and a "
        "genuine willingness to learn. Their conduct throughout the program was found to be satisfactory."
    )
    y = _draw_justified_paragraph(c, body2, left, y, content_width)

    # Closing line
    y -= 0.6 * cm
    c.setFont("Helvetica", 11)
    c.setFillColor(TEXT_DARK)
    c.drawString(left, y, "We wish them all the best for their future endeavors.")

    # Signature block
    sig_y = 4.4 * cm
    c.setFont("Helvetica-Oblique", 18)
    c.setFillColor(MID_BLUE)
    c.drawString(left, sig_y + 0.9 * cm, settings.SIGNATORY_NAME)
    c.setStrokeColor(TEXT_GREY)
    c.setLineWidth(0.6)
    c.line(left, sig_y + 0.55 * cm, left + 4.5 * cm, sig_y + 0.55 * cm)
    c.setFont("Helvetica-Bold", 10.5)
    c.setFillColor(TEXT_DARK)
    c.drawString(left, sig_y + 0.1 * cm, settings.SIGNATORY_NAME + ".")
    c.setFont("Helvetica", 9.5)
    c.setFillColor(TEXT_GREY)
    c.drawString(left, sig_y - 0.3 * cm, settings.SIGNATORY_TITLE)

    # Certificate ID + issued date, small and unobtrusive, right side
    c.setFont("Helvetica", 8)
    c.setFillColor(TEXT_GREY)
    c.drawRightString(right, sig_y + 0.1 * cm, f"Certificate ID: {student_id}")
    c.drawRightString(right, sig_y - 0.3 * cm, f"Issued on: {date.today().strftime('%d %b %Y')}")

    # Footer contact strip (unchanged)
    footer_parts = []
    if settings.COURSE_CENTER_EMAIL:
        footer_parts.append(settings.COURSE_CENTER_EMAIL)
    if settings.COURSE_CENTER_PHONE:
        footer_parts.append(settings.COURSE_CENTER_PHONE)
    if settings.COURSE_CENTER_WEBSITE:
        footer_parts.append(settings.COURSE_CENTER_WEBSITE)

    footer_y = 1.6 * cm
    c.setStrokeColor(MID_BLUE)
    c.setLineWidth(0.5)
    c.line(left, footer_y + 0.55 * cm, right, footer_y + 0.55 * cm)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(DARK_BLUE)
    c.drawCentredString(width / 2, footer_y + 0.15 * cm, settings.COURSE_CENTER_NAME.upper())
    if footer_parts:
        c.setFont("Helvetica", 8)
        c.setFillColor(TEXT_GREY)
        c.drawCentredString(width / 2, footer_y - 0.25 * cm, "   |   ".join(footer_parts))
    if settings.COURSE_CENTER_ADDRESS:
        c.setFont("Helvetica", 7.5)
        c.setFillColor(TEXT_GREY)
        c.drawCentredString(width / 2, footer_y - 0.6 * cm, settings.COURSE_CENTER_ADDRESS)

    c.showPage()
    c.save()

    return filepath