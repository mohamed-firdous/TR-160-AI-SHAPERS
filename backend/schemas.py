from pydantic import BaseModel
from typing import List

class ParagraphAnalysis(BaseModel):
    paragraph: str
    plagiarism_score: float
    ai_probability: float

class AnalysisResponse(BaseModel):
    overall_plagiarism_score: float
    overall_ai_probability: float
    paragraph_analysis: List[ParagraphAnalysis]

class ErrorResponse(BaseModel):
    error: str
