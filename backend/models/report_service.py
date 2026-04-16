from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from models.schemas import ParagraphResult, SummaryMetrics


def generate_pdf_report(filename: str, rows: list[ParagraphResult], summary: SummaryMetrics) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 40
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Faculty Report: Academic Integrity Analysis")

    y -= 20
    pdf.setFont("Helvetica", 9)
    pdf.drawString(40, y, f"Generated: {datetime.now(timezone.utc).isoformat()}")
    y -= 14
    pdf.drawString(40, y, f"File: {filename}")

    y -= 20
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(40, y, "Summary")
    y -= 14
    pdf.setFont("Helvetica", 9)
    pdf.drawString(40, y, f"Paragraphs: {summary.paragraph_count}")
    y -= 12
    pdf.drawString(40, y, f"Avg plagiarism: {summary.avg_plagiarism:.2f}")
    y -= 12
    pdf.drawString(40, y, f"Avg AI probability: {summary.avg_ai_probability:.2f}")
    y -= 12
    pdf.drawString(40, y, f"High-risk sections: {summary.high_risk_sections}")

    y -= 18
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(40, y, "Top suspicious paragraphs")

    pdf.setFont("Helvetica", 9)
    for row in sorted(rows, key=lambda item: item.risk_score, reverse=True)[:8]:
        y -= 14
        if y < 80:
            pdf.showPage()
            y = height - 40
            pdf.setFont("Helvetica", 9)

        text = (
            f"P{row.paragraph_index}: risk={row.risk_score:.2f}, "
            f"plag={row.plagiarism_score:.2f}, ai={row.ai_probability:.2f}, "
            f"label={row.heatmap_color}"
        )
        pdf.drawString(40, y, text)

    pdf.save()
    return buffer.getvalue()
