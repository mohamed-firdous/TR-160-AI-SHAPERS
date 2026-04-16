from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.analyze import router as analyze_router


app = FastAPI(title="Academic Integrity Detector API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)


@app.get("/")
def root() -> dict:
    return {
        "message": "Academic Integrity Detector API is running.",
        "health": "/health",
        "docs": "/docs",
        "analyze": "/analyze",
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
