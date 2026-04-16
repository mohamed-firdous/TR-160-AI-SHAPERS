from __future__ import annotations

from typing import List

import requests


def fetch_semantic_scholar_references(query: str, limit: int = 10, timeout: int = 8) -> List[str]:
    """Fetch paper abstracts/titles from Semantic Scholar for additional reference context."""
    if not query or not query.strip():
        return []

    endpoint = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": max(1, min(limit, 20)),
        "fields": "title,abstract,year",
    }

    try:
        response = requests.get(endpoint, params=params, timeout=timeout)
        response.raise_for_status()
    except Exception:
        return []

    payload = response.json()
    papers = payload.get("data", []) if isinstance(payload, dict) else []

    references: List[str] = []
    for paper in papers:
        title = (paper.get("title") or "").strip()
        abstract = (paper.get("abstract") or "").strip()
        year = paper.get("year")

        if not title and not abstract:
            continue

        meta = f" ({year})" if year else ""
        reference_text = f"{title}{meta}. {abstract}".strip()
        references.append(reference_text)

    return references