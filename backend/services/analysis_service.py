import os
import sys

"""
We explicitly add the model directory to Python path
so that analyze_document.py can correctly import:

text_extractor.py
paragraph_splitter.py
plagiarism_model.py
ai_detector.py
"""

# absolute path to root folder
ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

# add root folder to python search path
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# now safe to import natively recognizing the model module
from model.analyze_document import analyze_document

def run_analysis(file_path: str):
    """
    Executes the AI model pipeline.

    Steps:
    1. receives uploaded file path
    2. sends to analyze_document()
    3. returns structured JSON result
    """

    try:
        result = analyze_document(file_path)
        return result

    except Exception as e:
        return {
            "error": f"Model execution failed: {str(e)}"
        }