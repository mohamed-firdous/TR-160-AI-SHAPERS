import asyncio
import os
import tempfile
import uuid
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

# Ensure project root is importable for model package imports.
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT_DIR))

from model.analyze_document import analyze_document

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.getenv("FRONTEND_ORIGIN", "*")}})

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def _run_analysis(file_path: str):
    return asyncio.run(analyze_document(file_path))


@app.route("/analyze", methods=["POST"])
def analyze_endpoint():
    payload = request.get_json(silent=True) or {}
    file_path = payload.get("file_path")

    if not file_path:
        return jsonify({"error": "Missing 'file_path' in request body"}), 400

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        result = _run_analysis(file_path)
        status_code = 400 if isinstance(result, dict) and "error" in result else 200
        return jsonify(result), status_code
    except Exception as exc:
        return jsonify({"error": f"Analysis failed: {str(exc)}"}), 500


@app.route("/upload", methods=["POST"])
def upload_endpoint():
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]
    if not file or not file.filename:
        return jsonify({"error": "No file selected"}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": f"Unsupported file extension '{ext}'"}), 400

    temp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}{ext}")

    try:
        file.save(temp_path)
        result = _run_analysis(temp_path)
        status_code = 400 if isinstance(result, dict) and "error" in result else 200
        return jsonify(result), status_code
    except Exception as exc:
        return jsonify({"error": f"Upload processing failed: {str(exc)}"}), 500
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
