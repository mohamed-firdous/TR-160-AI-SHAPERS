# AI Content Detector

A full-stack academic document analyzer that estimates:
- AI-generated writing probability
- Plagiarism similarity risk
- Paragraph-level breakdown for review

## Project Structure
- backend: FastAPI API server
- model: AI and plagiarism analysis pipeline
- frontend: Vite + React web app
- sample_data: sample reference articles

## Prerequisites
- Python 3.10 or newer
- Node.js 18 or newer
- npm

## Safe Setup (Windows PowerShell)
1. Open a terminal in the project root.
2. Create and activate a virtual environment:
   - python -m venv .venv
   - .\.venv\Scripts\Activate.ps1
3. Install Python dependencies:
   - pip install -r requirements.txt
4. Install frontend dependencies:
   - cd frontend
   - npm install
   - cd ..

## Run the Application
Run backend:
1. cd backend
2. uvicorn main:app --reload

Run frontend in a second terminal:
1. cd frontend
2. npm run dev

Default local URLs:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Backend docs: http://localhost:8000/docs

## API Endpoint
- POST /upload
  - Accepts: .pdf, .docx
  - Form field name: file

## Safety Notes
- Do not upload sensitive or confidential documents to production systems without access controls.
- Keep .env, private keys, and local model cache directories out of source control.
- Validate uploaded files by extension and size before processing in production deployments.
- Resource-heavy model loading can increase startup time and memory usage; monitor system limits.

## Troubleshooting
- If frontend shows Network Error:
  1. Confirm backend is running on port 8000.
  2. Open http://localhost:8000 and verify health response.
  3. Check backend terminal logs for Python import or model-loading errors.
- If upload returns validation errors:
  - Ensure file has extractable text and is at least 25 words.
  - Use supported formats only (.pdf, .docx).

## Development Tips
- Keep backend and frontend running in separate terminals.
- Use backend requirements in backend/requirements.txt and model requirements in model/requirements.txt for module-scoped installs, or use the root requirements.txt for a single environment install.

## Author
- MOHAMMED FIRDOUS S
- SAI NITHICK ROSHAAN S
- RAVIN S
- PRADEEP M
