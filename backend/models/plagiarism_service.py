from __future__ import annotations

from functools import lru_cache
from typing import Sequence

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def detect_plagiarism(paragraphs: Sequence[str], references: Sequence[str]) -> list[dict]:
    if not paragraphs:
        return []

    if not references:
        references = ["No reference corpus provided."]

    model = get_embedding_model()
    para_embeddings = model.encode(list(paragraphs), normalize_embeddings=True)
    ref_embeddings = model.encode(list(references), normalize_embeddings=True)

    sim_matrix = cosine_similarity(para_embeddings, ref_embeddings)

    results: list[dict] = []
    for idx in range(sim_matrix.shape[0]):
        best_idx = int(np.argmax(sim_matrix[idx]))
        score = float(np.clip(sim_matrix[idx, best_idx], 0.0, 1.0))
        results.append(
            {
                "plagiarism_score": round(score, 4),
                "confidence": _confidence_label(score),
                "matched_reference": references[best_idx],
            }
        )

    return results


def _confidence_label(score: float) -> str:
    if score >= 0.8:
        return "High"
    if score >= 0.55:
        return "Medium"
    return "Low"
