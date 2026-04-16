from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from detector.pipeline import run_full_analysis
from detector.visualization import summarize_metrics


app = FastAPI(title="Academic Integrity Detector API", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    custom_reference: str = Form(default=""),
    scholar_query: str = Form(default=""),
    style_guidelines: str = Form(default=""),
) -> dict:
    try:
        content = await file.read()
        output = run_full_analysis(
            filename=file.filename,
            file_bytes=content,
            extra_reference_text=custom_reference,
            scholar_query=scholar_query,
            style_guidelines=style_guidelines,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    summary = summarize_metrics(output.combined_df)
    return {
        "filename": output.filename,
        "elapsed_seconds": output.elapsed_seconds,
        "reference_count": output.reference_count,
        "summary": summary,
        "rows": output.combined_df.to_dict(orient="records"),
    }
