from __future__ import annotations

from pydantic import BaseModel, Field


class SummaryMetrics(BaseModel):
    paragraph_count: int
    avg_plagiarism: float
    avg_ai_probability: float
    high_risk_sections: int


class ParagraphResult(BaseModel):
    paragraph_index: int
    paragraph: str
    plagiarism_score: float = Field(ge=0.0, le=1.0)
    plagiarism_confidence: str
    matched_reference: str
    ai_probability: float = Field(ge=0.0, le=1.0)
    ai_confidence: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    burstiness: float = Field(ge=0.0, le=1.0)
    perplexity: float = Field(ge=0.0)
    repetition_ratio: float = Field(ge=0.0, le=1.0)
    classifier_ai_probability: float = Field(ge=0.0, le=1.0)
    doc_ai_prior: float = Field(ge=0.0, le=1.0)
    risk_score: float = Field(ge=0.0, le=1.0)
    heatmap_color: str


class AnalysisResponse(BaseModel):
    filename: str
    summary: SummaryMetrics
    paragraphs: list[ParagraphResult]
    pdf_report_base64: str
