import re

def split_into_paragraphs(text):
    """
    Robust paragraph splitter that identifies breaks using multiple newline variations.
    Handles \n\n, \r\n\r\n, and multiple consecutive whitespace line breaks.
    """
    if not text:
        return []

    # 1. Normalize line endings and split by double-newline or more
    blocks = re.split(r'\n\s*\n|\r\n\s*\r\n', text)
    
    cleaned_paragraphs = []
    for b in blocks:
        cleaned = b.strip()
        if cleaned:
            # Fallback for greedy PDF extractions: split on lines ending in terminal punct
            sub_splits = re.split(r'(?<=[.!?])\n', cleaned)
            for s in sub_splits:
                s_cleaned = s.strip()
                if len(s_cleaned) >= 1:
                    cleaned_paragraphs.append(s_cleaned)
                    
    return cleaned_paragraphs
