from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse
from services.report_service import generate_report_pdf
from schemas import AnalysisResponse
import io

router = APIRouter()

@router.post("/export-report")
async def export_report(analysis_data: AnalysisResponse):
    """
    Expert Report Generation Endpoint.
    Converts semantic analysis results into a structured faculty-facing PDF report,
    including evidence heatmaps and logic-driven summary assessments.
    """
    report_buffer = generate_report_pdf(analysis_data.model_dump())
    
    return Response(
        content=report_buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=analysis_report.pdf"}
    )
