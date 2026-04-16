import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import upload

app = FastAPI(title="AI Academic Analyzer API", version="1.0.0")

# Apply wildcard CORS dynamically mapping port variations between Frontend build systems natively!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect modularized upload pipeline securely
app.include_router(upload.router)

@app.get("/")
def health_check():
    """ Verify server binds and connectivity natively. """
    return {"status": "AI Academic Analyzer Backend is successfully running!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
