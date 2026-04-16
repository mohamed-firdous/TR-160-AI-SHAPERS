import os
import json
import concurrent.futures

try:
    from .text_extractor import extract_text_from_pdf, extract_text_from_docx
    from .paragraph_splitter import split_into_paragraphs
    from .plagiarism_model import compute_plagiarism_score
    from .ai_detector import compute_ai_probability
except ImportError:
    from text_extractor import extract_text_from_pdf, extract_text_from_docx
    from paragraph_splitter import split_into_paragraphs
    from plagiarism_model import compute_plagiarism_score
    from ai_detector import compute_ai_probability

def _process_paragraph(p):
    """
    Independent functional worker explicitly designed for massive asynchronous Parallel Threading.
    """
    p_score = compute_plagiarism_score(p)
    a_score = compute_ai_probability(p)
    return {
        "paragraph": p,
        "plagiarism_score": p_score,
        "ai_probability": a_score
    }

def analyze_document(file_path):
    """
    Enhanced analysis pipeline with robust paragraph chunking and aggregation.
    """
    if not os.path.exists(file_path):
        return {"error": "File not found"}
        
    ext = file_path.lower().split('.')[-1]
    
    # 1. Extraction Layer
    raw_text = ""
    if ext == 'pdf':
        raw_text = extract_text_from_pdf(file_path)
    elif ext == 'docx':
        raw_text = extract_text_from_docx(file_path)
    elif ext == 'txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
    else:
        return {"error": f"Unsupported file type '{ext}'"}

    if not raw_text.strip():
        return {"error": "No extractable text found"}
        
    # 2. Preprocessing & Robust Chunking
    raw_paragraphs = split_into_paragraphs(raw_text)
    
    # Filter paragraphs shorter than 40 words
    filtered_p = [p for p in raw_paragraphs if len(p.split()) >= 40]
    
    if not filtered_p:
        return {"error": "No significant text found (paragraphs too short)"}

    # Chunking: Ensure chunks are between 120-350 words
    processed_paragraphs = []
    current_chunk = []
    current_count = 0
    
    for p in filtered_p:
        count = len(p.split())
        if current_count + count > 350 and current_chunk:
            processed_paragraphs.append(" ".join(current_chunk))
            current_chunk = [p]
            current_count = count
        else:
            current_chunk.append(p)
            current_count += count
            if current_count >= 120:
                processed_paragraphs.append(" ".join(current_chunk))
                current_chunk = []
                current_count = 0
    
    if current_chunk:
        processed_paragraphs.append(" ".join(current_chunk))

    if not processed_paragraphs:
        return {"error": "Could not form valid analysis chunks"}
        
    # 3. Parallel Inference
    paragraph_analysis = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(_process_paragraph, processed_paragraphs))
        paragraph_analysis.extend(results)

    # 4. Global Structural Aggregation
    ai_scores = [item["ai_probability"] for item in paragraph_analysis]
    plag_scores = [item["plagiarism_score"] for item in paragraph_analysis]
    
    if ai_scores:
        # AI score = mean of top 40% highest AI paragraph scores
        ai_scores.sort(reverse=True)
        top_k = max(1, int(len(ai_scores) * 0.40))
        overall_ai = round(sum(ai_scores[:top_k]) / top_k, 2)
    else:
        overall_ai = 0.0
        
    if plag_scores:
        # Plagiarism score = max similarity across paragraphs
        overall_plag = round(max(plag_scores), 2)
    else:
        overall_plag = 0.0
    
    return {
        "overall_plagiarism_score": overall_plag,
        "overall_ai_probability": overall_ai,
        "paragraph_analysis": paragraph_analysis
    }
