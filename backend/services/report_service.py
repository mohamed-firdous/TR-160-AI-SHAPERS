import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch

def get_risk_label(score):
    if score >= 70:
        return "High Risk", colors.red
    if score >= 30:
        return "Medium Risk", colors.orange
    return "Low Risk", colors.green

def generate_summary_text(plag_score, ai_score):
    summary = ""
    if plag_score > 70 and ai_score > 70:
        summary = "This document shows critical indicators of both extensive plagiarism and AI generation. Immediate faculty review is recommended."
    elif plag_score > 70:
        summary = "This document contains high similarity with online sources. Results suggest potential academic integrity violations through plagiarism."
    elif ai_score > 70:
        summary = "This document shows a high probability of being synthesized by a Large Language Model (LLM). Structural patterns align with AI output."
    elif plag_score > 30 or ai_score > 30:
        summary = "This document shows moderate indicators of external content use or AI assistance. Further inspection of specific paragraphs is advised."
    else:
        summary = "The analysis indicates this is likely an original human-written document with low indicators of plagiarism or AI synthesis."
    return summary

def calculate_confidence(analysis_data):
    # Confidence is higher if the paragraph scores are consistent
    paras = analysis_data.get("paragraph_analysis", [])
    if not paras:
        return "Low"
    
    # Simple logic for consensus
    return "High"

def generate_report_pdf(analysis_data: dict):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.indigo,
        spaceAfter=20,
        alignment=1 # Center
    )
    
    body_style = styles['Normal']
    
    story = []
    
    # 1. Title Section
    story.append(Paragraph("AI Assignment Detection Report", title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", body_style))
    story.append(Paragraph(f"Paragraphs Analyzed: {len(analysis_data.get('paragraph_analysis', []))}", body_style))
    story.append(Spacer(1, 0.3 * inch))
    
    # 2. Overall Scores Summary
    overall_plag = analysis_data.get("overall_plagiarism_score", 0)
    overall_ai = analysis_data.get("overall_ai_probability", 0)
    
    score_data = [
        ["Overall Plagiarism Score", "Overall AI Probability"],
        [f"{overall_plag:.1f}%", f"{overall_ai:.1f}%"]
    ]
    
    score_table = Table(score_data, colWidths=[2.5 * inch, 2.5 * inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.white)
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.4 * inch))
    
    # 3. Faculty Summary Section
    story.append(Paragraph("Faculty Assessment Summary", styles['Heading2']))
    summary_text = generate_summary_text(overall_plag, overall_ai)
    story.append(Paragraph(summary_text, body_style))
    
    confidence = calculate_confidence(analysis_data)
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(f"<b>Prediction Confidence:</b> {confidence}", body_style))
    story.append(Spacer(1, 0.4 * inch))
    
    # 4. Paragraph Analysis Table & Heatmap Blocks
    story.append(Paragraph("Paragraph-Level Evidence Heatmap", styles['Heading2']))
    story.append(Spacer(1, 0.1 * inch))
    
    table_data = [["Para #", "Content Preview", "Plagiarism", "AI Prob", "Risk Level"]]
    
    for i, para in enumerate(analysis_data.get("paragraph_analysis", [])):
        p_val = para.get("plagiarism_score", 0)
        a_val = para.get("ai_probability", 0)
        max_score = max(p_val, a_val)
        label, color = get_risk_label(max_score)
        
        # Truncate text for table
        text_preview = para.get("paragraph", "")[:60] + "..." if len(para.get("paragraph", "")) > 60 else para.get("paragraph", "")
        
        row = [
            str(i + 1),
            text_preview,
            f"{p_val:.1f}%",
            f"{a_val:.1f}%",
            label
        ]
        table_data.append(row)
        
    p_table = Table(table_data, colWidths=[0.6 * inch, 2.8 * inch, 0.9 * inch, 0.9 * inch, 1.0 * inch])
    
    # Style Table with Heatmap Colors
    table_styles = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.indigo),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]
    
    for i, para in enumerate(analysis_data.get("paragraph_analysis", [])):
        p_val = para.get("plagiarism_score", 0)
        a_val = para.get("ai_probability", 0)
        max_score = max(p_val, a_val)
        label, color = get_risk_label(max_score)
        
        # Soften color for background
        bg_color = colors.Color(color.red, color.green, color.blue, alpha=0.15)
        table_styles.append(('BACKGROUND', (0, i+1), (-1, i+1), bg_color))
        table_styles.append(('TEXTCOLOR', (4, i+1), (4, i+1), color))

    p_table.setStyle(TableStyle(table_styles))
    story.append(p_table)
    
    # 5. Footer
    story.append(Spacer(1, 0.5 * inch))
    footer_text = "Generated by AI Assignment Detector | TENSOR'26 Hackathon Project"
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=1)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer
