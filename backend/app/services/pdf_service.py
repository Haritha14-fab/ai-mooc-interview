"""Build trusted, multi-page assessment reports as PDF documents."""

from datetime import datetime
from html import escape
from io import BytesIO
from pathlib import Path
import os
import re

from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

INK = colors.HexColor("#15253d")
BLUE = colors.HexColor("#1a5490")
MUTED = colors.HexColor("#5d6b7c")
PALE = colors.HexColor("#eef3f8")


def _register_readable_fonts() -> tuple[str, str]:
    """Prefer a Unicode TTF and fall back to ReportLab's bundled Vera font."""
    candidates = []
    windows_dir = os.environ.get("WINDIR", r"C:\Windows")
    candidates.extend([
        (Path(windows_dir) / "Fonts" / "arial.ttf", Path(windows_dir) / "Fonts" / "arialbd.ttf"),
        (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")),
        (Path(rl_config.TTFSearchPath[0]) / "Vera.ttf", Path(rl_config.TTFSearchPath[0]) / "VeraBd.ttf"),
    ])
    for regular_path, bold_path in candidates:
        if regular_path.is_file() and bold_path.is_file():
            pdfmetrics.registerFont(TTFont("AssessmentUnicode", str(regular_path)))
            pdfmetrics.registerFont(TTFont("AssessmentUnicode-Bold", str(bold_path)))
            return "AssessmentUnicode", "AssessmentUnicode-Bold"
    return "Helvetica", "Helvetica-Bold"


def _safe_text(value) -> str:
    text = str(value if value is not None else "")
    text = "".join(char for char in text if char in "\n\t" or ord(char) >= 32)
    return escape(text).replace("\n", "<br/>")


def _date(value) -> str:
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M UTC")
    return str(value or "N/A")


class PDFService:
    """Generate a report from values loaded and evaluated by the backend."""

    @staticmethod
    def generate_report(assessment_data: dict, questions_results: list) -> BytesIO:
        buffer = BytesIO()
        regular_font, bold_font = _register_readable_fonts()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.65 * inch,
            leftMargin=0.65 * inch,
            topMargin=0.72 * inch,
            bottomMargin=0.72 * inch,
            title=f"Assessment report {assessment_data.get('assessment_id', '')}",
            author="AI MOOC Interview & Assessment System",
        )
        base_styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "AssessmentTitle",
            parent=base_styles["Title"],
            fontName=bold_font,
            fontSize=20,
            leading=25,
            textColor=INK,
            alignment=TA_CENTER,
            spaceAfter=3,
        )
        subtitle_style = ParagraphStyle(
            "AssessmentSubtitle",
            parent=base_styles["Normal"],
            fontName=regular_font,
            fontSize=9,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=16,
        )
        heading_style = ParagraphStyle(
            "AssessmentHeading",
            parent=base_styles["Heading2"],
            fontName=bold_font,
            fontSize=12,
            leading=16,
            textColor=BLUE,
            spaceBefore=10,
            spaceAfter=7,
            keepWithNext=True,
        )
        body_style = ParagraphStyle(
            "AssessmentBody",
            parent=base_styles["BodyText"],
            fontName=regular_font,
            fontSize=9,
            leading=13,
            textColor=INK,
            spaceAfter=4,
            splitLongWords=1,
        )
        label_style = ParagraphStyle(
            "AssessmentLabel",
            parent=body_style,
            fontName=bold_font,
        )
        small_style = ParagraphStyle(
            "AssessmentSmall",
            parent=body_style,
            fontSize=8,
            leading=11,
            textColor=MUTED,
        )

        def paragraph(value, style=body_style):
            return Paragraph(_safe_text(value), style)

        def information_table(rows):
            cells = [[paragraph(label, label_style), paragraph(value)] for label, value in rows]
            table = Table(cells, colWidths=[1.65 * inch, 5.05 * inch], hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, -1), PALE),
                ("TEXTCOLOR", (0, 0), (-1, -1), INK),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LINEBELOW", (0, 0), (-1, -1), 0.35, colors.HexColor("#dce4ed")),
            ]))
            return table

        elements = [
            Paragraph("AI MOOC Interview & Assessment", title_style),
            Paragraph("ASSESSMENT REPORT", subtitle_style),
            Paragraph("Candidate", heading_style),
            information_table([
                ("Name", assessment_data.get("user_name", "N/A")),
                ("Email", assessment_data.get("user_email", "N/A")),
                ("Assessment ID", assessment_data.get("assessment_id", "N/A")),
            ]),
            Spacer(1, 8),
            Paragraph("Assessment details", heading_style),
            information_table([
                ("Subject", assessment_data.get("subject", "N/A")),
                ("Difficulty", assessment_data.get("difficulty", "N/A")),
                ("Attempt", assessment_data.get("attempt_number", 1)),
                ("Created", _date(assessment_data.get("created_at"))),
                ("Submitted", _date(assessment_data.get("submitted_at"))),
                ("Final submission", _date(assessment_data.get("final_submitted_at"))),
            ]),
            Spacer(1, 8),
            Paragraph("Result", heading_style),
            information_table([
                ("Status", assessment_data.get("status", "N/A")),
                ("Total questions", assessment_data.get("total_questions", len(questions_results))),
                ("Correct", assessment_data.get("correct_count", 0)),
                ("Wrong", assessment_data.get("wrong_count", 0)),
                ("Unanswered", assessment_data.get("unanswered_count", 0)),
                ("Score", f"{assessment_data.get('score', 0)}/{assessment_data.get('total_questions', len(questions_results))}"),
                ("Percentage", f"{assessment_data.get('percentage', 0):.1f}%"),
                ("Performance", assessment_data.get("performance", "N/A")),
            ]),
            Spacer(1, 8),
            Paragraph("Question analysis", heading_style),
        ]

        for index, item in enumerate(questions_results, start=1):
            number = item.get("question_number", index)
            elements.append(Paragraph(f"Question {number}", heading_style))
            elements.append(paragraph(item.get("question_text", "")))
            user_letter = item.get("user_answer")
            user_text = item.get("user_answer_text", "Not answered")
            correct_letter = item.get("correct_answer", "N/A")
            correct_text = item.get("correct_answer_text", "")
            outcome = "Correct" if item.get("is_correct") else ("Unanswered" if not user_letter else "Wrong")
            elements.append(paragraph(f"Your answer: {user_letter or '—'} · {user_text}"))
            elements.append(paragraph(f"Correct answer: {correct_letter} · {correct_text}"))
            elements.append(paragraph(f"Result: {outcome}", label_style))
            elements.append(paragraph(f"Explanation: {item.get('explanation', 'N/A')}"))
            elements.append(Spacer(1, 8))

        if assessment_data.get("ai_feedback"):
            elements.append(Paragraph("Performance analysis", heading_style))
            feedback = re.sub(r"\n\s*\n", "\n", assessment_data["ai_feedback"])
            elements.append(paragraph(feedback))

        def draw_footer(canvas, document):
            canvas.saveState()
            canvas.setStrokeColor(colors.HexColor("#dce4ed"))
            canvas.line(doc.leftMargin, 0.52 * inch, letter[0] - doc.rightMargin, 0.52 * inch)
            canvas.setFont(regular_font, 8)
            canvas.setFillColor(MUTED)
            canvas.drawString(doc.leftMargin, 0.34 * inch, "AI MOOC Interview & Assessment System")
            canvas.drawRightString(letter[0] - doc.rightMargin, 0.34 * inch, f"Page {document.page}")
            canvas.restoreState()

        doc.build(elements, onFirstPage=draw_footer, onLaterPages=draw_footer)
        buffer.seek(0)
        return buffer
