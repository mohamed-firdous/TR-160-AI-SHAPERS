import torch
import requests
import asyncio
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from sentence_transformers import SentenceTransformer, util
import trafilatura
from newspaper import Article
import re

try:
    model = SentenceTransformer('all-mpnet-base-v2', device='cpu')
except Exception as e:
    print(f"Warning: Could not load mpnet model. {e}")
    model = None

def get_search_queries(text, num_queries=3):
    """
    Generate diverse queries by picking segments from the start, middle, and end.
    """
    words = text.split()
    if len(words) < 20:
        return [" ".join(words)]
    
    queries = []
    chunk_size = 12
    # 1. Start area
    queries.append(" ".join(words[2:2+chunk_size]))
    # 2. Middle area
    mid = len(words) // 2
    queries.append(" ".join(words[mid:mid+chunk_size]))
    # 3. End area
    end = len(words) - chunk_size - 2
    if end > mid:
        queries.append(" ".join(words[end:end+chunk_size]))
    
    return [q for q in queries if q]

# In-memory cache for search results to optimize performance
SEARCH_CACHE = {}

def get_search_queries(text, num_queries=2):
    """
    Generate 2-3 semantic search queries from a paragraph.
    Picks diverse segments of 10-15 words.
    """
    words = text.split()
    if len(words) < 20:
        return [text]
    
    queries = []
    chunk_size = 15
    for i in range(num_queries):
        start = (i * len(words)) // num_queries
        end = min(start + chunk_size, len(words))
        query = " ".join(words[start:end])
        if query:
            queries.append(query)
    return queries

def robust_extract(url):
    """
    Cleaner text extraction using trafilatura and newspaper3k.
    """
    # 1. Try Trafilatura
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            extracted = trafilatura.extract(downloaded)
            if extracted and len(extracted.split()) > 50:
                return extracted
    except: pass
    
    # 2. Fallback to Newspaper3k
    try:
        article = Article(url)
        article.download()
        article.parse()
        if article.text and len(article.text.split()) > 50:
            return article.text
    except: pass
    
    # 3. Final fallback to BeautifulSoup
    try:
        resp = requests.get(url, timeout=5)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        return ' '.join(soup.stripped_strings)
    except: pass
    
    return ""

def compute_plagiarism_score(paragraph):
    """
    High-fidelity plagiarism detection using live multi-query SERP and chunked semantic mapping.
    """
    if not paragraph.strip() or not model or len(paragraph.split()) < 10:
        return 0.0

    # Cache check
    cache_key = paragraph[:100]
    if cache_key in SEARCH_CACHE:
        return SEARCH_CACHE[cache_key]

    try:
        queries = get_search_queries(paragraph)
        all_urls = set()
        
        with DDGS() as ddgs:
            for q in queries:
                try:
                    results = list(ddgs.text(q, max_results=3))
                    for r in results:
                        all_urls.add(r['href'])
                except: continue
        
        if not all_urls:
            return 0.05

        paragraph_emb = model.encode(paragraph, convert_to_tensor=True)
        max_similarity = 0.0
        
        # Process top 8 URLs max
        target_urls = list(all_urls)[:8]
        for url in target_urls:
            text = robust_extract(url)
            if not text: continue
            
            # Truncate to first 1500 words
            text_words = text.split()[:1500]
            text = " ".join(text_words)
            
            # Chunk article into 150-300 word blocks
            chunk_size_words = 200
            words = text.split()
            article_chunks = [" ".join(words[i:i+chunk_size_words]) for i in range(0, len(words), 100)] # overlapping
            
            if not article_chunks: continue
            
            article_embs = model.encode(article_chunks, convert_to_tensor=True)
            similarities = util.cos_sim(paragraph_emb, article_embs)
            highest = torch.max(similarities).item()
            max_similarity = max(max_similarity, highest)

        # Scale remapping:
        # > 0.90 -> 0.90 - 1.00
        # > 0.80 -> 0.70 - 0.90
        # > 0.70 -> 0.50 - 0.70
        # > 0.60 -> 0.30 - 0.50
        # < 0.60 -> 0.00 - 0.30
        
        score = 0.0
        if max_similarity > 0.90:
            score = 0.90 + (max_similarity - 0.90) * 1.0
        elif max_similarity > 0.80:
            score = 0.70 + (max_similarity - 0.80) * 2.0
        elif max_similarity > 0.70:
            score = 0.50 + (max_similarity - 0.70) * 2.0
        elif max_similarity > 0.60:
            score = 0.30 + (max_similarity - 0.60) * 2.0
        else:
            score = max_similarity * 0.5
            
        final_score = round(min(1.0, score), 2)
        SEARCH_CACHE[cache_key] = final_score
        return final_score

    except Exception as e:
        print(f"Plagiarism Engine Error: {e}")
        return 0.0
