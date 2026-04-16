from __future__ import annotations

import base64

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from models.ai_detection_service import detect_ai_content
from models.plagiarism_service import detect_plagiarism
from models.report_service import generate_pdf_report
from models.schemas import AnalysisResponse, ParagraphResult, SummaryMetrics
from utils.file_processing import parse_uploaded_file
from utils.reference_loader import load_reference_corpus

router = APIRouter(prefix="", tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_document(
    file: UploadFile = File(...),
    custom_reference: str = Form(default=""),
) -> AnalysisResponse:
    try:
        file_bytes = await file.read()
        parsed = parse_uploaded_file(filename=file.filename or "uploaded", file_bytes=file_bytes)

        references = load_reference_corpus(custom_reference)
        plagiarism_results = detect_plagiarism(parsed.paragraphs, references)
        ai_results = detect_ai_content(parsed.paragraphs)

        rows: list[ParagraphResult] = []
        for idx, paragraph in enumerate(parsed.paragraphs):
            plag = plagiarism_results[idx]
            ai = ai_results[idx]
            risk_score = round((0.6 * plag["plagiarism_score"]) + (0.4 * ai["ai_probability"]), 4)
            rows.append(
                ParagraphResult(
                    paragraph_index=idx + 1,
                    paragraph=paragraph,
                    plagiarism_score=plag["plagiarism_score"],
                    plagiarism_confidence=plag["confidence"],
                    matched_reference=plag["matched_reference"],
                    ai_probability=ai["ai_probability"],
                    ai_confidence=ai["confidence"],
                    confidence_score=ai["confidence_score"],
                    burstiness=ai["burstiness"],
                    perplexity=ai["perplexity"],
                    repetition_ratio=ai["repetition_ratio"],
                    classifier_ai_probability=ai["classifier_ai_probability"],
                    doc_ai_prior=ai["doc_ai_prior"],
                    risk_score=risk_score,
                    heatmap_color=_heatmap_color(risk_score),
                )
            )

        summary = SummaryMetrics(
            paragraph_count=len(rows),
            avg_plagiarism=round(sum(r.plagiarism_score for r in rows) / max(len(rows), 1), 4),
            avg_ai_probability=round(sum(r.ai_probability for r in rows) / max(len(rows), 1), 4),
            high_risk_sections=sum(1 for r in rows if r.risk_score >= 0.75),
        )

        pdf_bytes = generate_pdf_report(filename=file.filename or "uploaded", rows=rows, summary=summary)
        pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")

        return AnalysisResponse(
            filename=file.filename or "uploaded",
            summary=summary,
            paragraphs=rows,
            pdf_report_base64=pdf_b64,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _heatmap_color(risk_score: float) -> str:
    if risk_score >= 0.75:
        return "red"
    if risk_score >= 0.45:
        return "yellow"
    return "green"
