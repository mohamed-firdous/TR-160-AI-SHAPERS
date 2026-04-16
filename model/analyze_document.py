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

import asyncio

async def analyze_document(file_path):
    """
    HIGH-PERFORMANCE ACCURACY PIPELINE
    - Sync extraction (local)
    - Paragraph grouping for AI context
    - Async parallel inference
    - Selective Web Search
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
        
    paragraphs = split_into_paragraphs(raw_text)
    if not paragraphs and raw_text.strip():
        paragraphs = [raw_text.strip()]
    
    if not paragraphs:
        return {"error": "No extractable text found."}
        
    # --- PERFORMANCE OPTIMIZATION: SELECTIVE PLAGIARISM SEARCH ---
    search_candidates = []
    for i, p in enumerate(paragraphs):
        word_count = len(p.split())
        if word_count >= 40:
            search_candidates.append({"index": i, "text": p, "length": word_count})
    
    search_candidates.sort(key=lambda x: x["length"], reverse=True)
    top_5_indices = {c["index"] for c in search_candidates[:5]}

    # --- ACCURACY OPTIMIZATION: PARAGRAPH RE-CHUNKING FOR AI ---
    # Requirement 2: Combine adjacent paragraphs for 150-400 word chunks
    chunks = []
    current_chunk_indices = []
    current_chunk_text = ""
    current_chunk_words = 0

    for i, p in enumerate(paragraphs):
        p_words = len(p.split())
        if current_chunk_words + p_words > 400 and current_chunk_words >= 150:
            # Seal current chunk
            chunks.append({"indices": current_chunk_indices, "text": current_chunk_text.strip()})
            current_chunk_indices = [i]
            current_chunk_text = p
            current_chunk_words = p_words
        else:
            current_chunk_indices.append(i)
            current_chunk_text += "\n" + p
            current_chunk_words += p_words
            
    if current_chunk_indices:
        chunks.append({"indices": current_chunk_indices, "text": current_chunk_text.strip()})

    # --- PARALLEL ORCHESTRATION ---
    # Phase A: Plagiarism Tasks (Paragraph-level)
    plag_tasks = []
    for i, p in enumerate(paragraphs):
        skip = (i not in top_5_indices)
        plag_tasks.append(compute_plagiarism_score(p, skip_search=skip))
        
    # Phase B: AI Tasks (Chunk-level - Requirement 2)
    ai_tasks = [compute_ai_probability(c["text"]) for c in chunks]

    # Execute all
    plag_results, ai_results = await asyncio.gather(
        asyncio.gather(*plag_tasks),
        asyncio.gather(*ai_tasks)
    )

    # RE-ASSEMBLE RESULTS
    paragraph_analysis = []
    for i, p in enumerate(paragraphs):
        # Find which AI result matches this paragraph
        ai_prob = 0.0
        for chunk_idx, chunk_meta in enumerate(chunks):
            if i in chunk_meta["indices"]:
                ai_prob = ai_results[chunk_idx]
                break
        
        p_score = plag_results[i]
        
        # Requirement 3: Only reduce AI probability if plagiarism similarity > 92%
        # Graduation: Reduce by 90% instead of hard-kill to allow for 10-30% range on Wiki
        if p_score > 92.0:
            ai_prob *= 0.1
            
        paragraph_analysis.append({
            "paragraph": p,
            "plagiarism_score": p_score,
            "ai_probability": ai_prob,
            "search_performed": (i in top_5_indices)
        })

    # --- GLOBAL AGGREGATION ---
    # Requirement 3 refinement: Use 92% threshold for filter
    ai_scores = [item["ai_probability"] for item in paragraph_analysis if item["plagiarism_score"] <= 92.0]
    plag_scores = [item["plagiarism_score"] for item in paragraph_analysis]
    
    if ai_scores:
        ai_scores.sort(reverse=True)
        top_k = max(1, int(len(ai_scores) * 0.40))
        overall_ai = sum(ai_scores[:top_k]) / top_k
    else:
        overall_ai = 0.0
        
    overall_plag = max(plag_scores) if plag_scores else 0.0
    
    overall_plag = round(max(0, min(100, overall_plag)), 1)
    overall_ai = round(max(0, min(100, overall_ai)), 1)
    
    for item in paragraph_analysis:
        item["plagiarism_score"] = round(item["plagiarism_score"], 1)
        item["ai_probability"] = round(item["ai_probability"], 1)
        
    print(f"\n>>> FINAL PERFORMANCE BROADCAST -> AI: {overall_ai}%, Plag: {overall_plag}%")
    
    return {
        "overall_plagiarism_score": overall_plag,
        "overall_ai_probability": overall_ai,
        "paragraph_analysis": paragraph_analysis
    }
