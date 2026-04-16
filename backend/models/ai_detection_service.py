from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Sequence

import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold

BASE_DIR = Path(__file__).resolve().parent.parent
TRAINING_DATA_PATH = BASE_DIR / "data" / "ai_detection_training.jsonl"


@dataclass
class _ModelArtifacts:
    vectorizer: TfidfVectorizer
    model: CalibratedClassifierCV
    threshold: float


def detect_ai_content(paragraphs: Sequence[str]) -> list[dict]:
    """Return paragraph-level AI scores while preserving existing route compatibility."""
    if not paragraphs:
        return []

    artifacts = _load_artifacts()
    probabilities = predict_proba(paragraphs, artifacts=artifacts)

    feature_rows = [_engineered_feature_row(text) for text in paragraphs]
    burstiness_values = [row[0] for row in feature_rows]
    repetition_values = [row[2] for row in feature_rows]

    doc_ai_prior = float(np.mean(probabilities))
    results: list[dict] = []
    for idx, probability in enumerate(probabilities):
        confidence_score = _confidence_from_margin(probability, artifacts.threshold)
        results.append(
            {
                "ai_probability": round(float(probability), 4),
                "burstiness": round(float(burstiness_values[idx]), 4),
                "perplexity": round(float(_perplexity_proxy(probability)), 3),
                "repetition_ratio": round(float(repetition_values[idx]), 4),
                "classifier_ai_probability": round(float(probability), 4),
                "doc_ai_prior": round(doc_ai_prior, 4),
                "confidence": _confidence_label(probability, artifacts.threshold),
                "confidence_score": round(confidence_score, 4),
            }
        )
    return results


def tune_probability_threshold(
    y_true: Sequence[int],
    y_proba: Sequence[float],
    min_threshold: float = 0.55,
    max_threshold: float = 0.80,
    step: float = 0.01,
    beta: float = 0.5,
) -> dict[str, float]:
    """Tune decision threshold in [0.55, 0.80] favoring lower false positives via F-beta (beta<1)."""
    if len(y_true) != len(y_proba):
        raise ValueError("y_true and y_proba must have the same length")

    y_true_arr = np.asarray(y_true, dtype=int)
    y_proba_arr = np.asarray(y_proba, dtype=float)

    best_threshold = min_threshold
    best_score = -1.0

    threshold = min_threshold
    while threshold <= max_threshold + 1e-9:
        y_pred = (y_proba_arr >= threshold).astype(int)
        tp = int(np.sum((y_true_arr == 1) & (y_pred == 1)))
        fp = int(np.sum((y_true_arr == 0) & (y_pred == 1)))
        fn = int(np.sum((y_true_arr == 1) & (y_pred == 0)))

        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        beta_sq = beta * beta
        f_beta = (1 + beta_sq) * precision * recall / max((beta_sq * precision) + recall, 1e-12)

        if f_beta > best_score:
            best_score = f_beta
            best_threshold = threshold

        threshold += step

    return {
        "best_threshold": round(float(best_threshold), 4),
        "best_fbeta": round(float(best_score), 4),
        "beta": float(beta),
    }


def evaluate_detector(
    y_true: Sequence[int],
    y_proba: Sequence[float],
    threshold: float,
) -> dict[str, Any]:
    """Evaluation helper returning calibration-aware metrics and confusion matrix."""
    if len(y_true) != len(y_proba):
        raise ValueError("y_true and y_proba must have the same length")

    y_true_arr = np.asarray(y_true, dtype=int)
    y_proba_arr = np.asarray(y_proba, dtype=float)
    y_pred = (y_proba_arr >= threshold).astype(int)

    cm = confusion_matrix(y_true_arr, y_pred, labels=[0, 1])

    metrics = {
        "threshold": float(threshold),
        "accuracy": round(float(accuracy_score(y_true_arr, y_pred)), 4),
        "precision": round(float(precision_score(y_true_arr, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true_arr, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true_arr, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_true_arr, y_proba_arr)), 4) if len(set(y_true_arr.tolist())) > 1 else 0.0,
        "confusion_matrix": {
            "tn": int(cm[0, 0]),
            "fp": int(cm[0, 1]),
            "fn": int(cm[1, 0]),
            "tp": int(cm[1, 1]),
            "matrix": cm.tolist(),
        },
    }
    return metrics


def confusion_matrix_table(y_true: Sequence[int], y_pred: Sequence[int]) -> list[list[int]]:
    """Simple confusion matrix helper for external reporting tools."""
    cm = confusion_matrix(np.asarray(y_true, dtype=int), np.asarray(y_pred, dtype=int), labels=[0, 1])
    return cm.tolist()


def predict_proba(paragraphs: Sequence[str], artifacts: _ModelArtifacts | None = None) -> np.ndarray:
    model_artifacts = artifacts or _load_artifacts()
    tfidf = model_artifacts.vectorizer.transform(paragraphs)
    engineered = _engineered_features_matrix(paragraphs)
    x = hstack([tfidf, engineered], format="csr")
    return model_artifacts.model.predict_proba(x)[:, 1]


def _confidence_label(probability: float, threshold: float) -> str:
    margin = abs(probability - threshold)
    if margin >= 0.22:
        return "High"
    if margin >= 0.1:
        return "Medium"
    return "Low"


def _confidence_from_margin(probability: float, threshold: float) -> float:
    return float(np.clip(abs(probability - threshold) / 0.35, 0.0, 1.0))


def _perplexity_proxy(probability: float) -> float:
    # Backward-compatible numeric field; lower proxy means higher AI confidence.
    return 130.0 - (probability * 95.0)


@lru_cache(maxsize=1)
def _load_artifacts() -> _ModelArtifacts:
    texts, labels = _load_training_data()
    if len(texts) < 20 or len(set(labels)) < 2:
        texts, labels = _fallback_bootstrap_corpus()

    y = np.asarray(labels, dtype=int)
    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        ngram_range=(1, 2),
        min_df=1,
        max_features=20000,
    )
    tfidf = vectorizer.fit_transform(texts)
    engineered = _engineered_features_matrix(texts)
    x = hstack([tfidf, engineered], format="csr")

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    grid = GridSearchCV(
        estimator=LogisticRegression(
            class_weight="balanced",
            solver="saga",
            penalty="elasticnet",
            max_iter=3000,
        ),
        param_grid={
            "C": [0.1, 0.5, 1.0, 2.0, 5.0],
            "l1_ratio": [0.0, 0.4, 0.7, 1.0],
        },
        scoring="f1",
        cv=cv,
        n_jobs=-1,
        refit=True,
    )
    grid.fit(x, y)

    calibrated_model = CalibratedClassifierCV(
        estimator=grid.best_estimator_,
        method="sigmoid",
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
    )
    calibrated_model.fit(x, y)

    train_proba = calibrated_model.predict_proba(x)[:, 1]
    tuned = tune_probability_threshold(y_true=y, y_proba=train_proba, min_threshold=0.55, max_threshold=0.80)

    return _ModelArtifacts(
        vectorizer=vectorizer,
        model=calibrated_model,
        threshold=float(tuned["best_threshold"]),
    )


def _engineered_features_matrix(paragraphs: Sequence[str]) -> csr_matrix:
    rows = [_engineered_feature_row(text) for text in paragraphs]
    return csr_matrix(np.asarray(rows, dtype=np.float32))


def _engineered_feature_row(paragraph: str) -> list[float]:
    tokens = re.findall(r"\b\w+\b", paragraph.lower())
    sentences = [s.strip() for s in re.split(r"[.!?]+", paragraph) if s.strip()]

    if not tokens:
        return [0.0, 0.0, 0.0]

    sentence_lengths = [len(re.findall(r"\b\w+\b", s)) for s in sentences] or [len(tokens)]
    sentence_std = float(pstdev(sentence_lengths)) if len(sentence_lengths) > 1 else 0.0
    sentence_var = float(np.clip(sentence_std / max(mean(sentence_lengths), 1.0), 0.0, 1.0))

    lexical_diversity = float(np.clip(len(set(tokens)) / max(len(tokens), 1), 0.0, 1.0))

    trigrams = [" ".join(tokens[i : i + 3]) for i in range(max(0, len(tokens) - 2))]
    repetition_ratio = 0.0
    if trigrams:
        repetition_ratio = float(np.clip((len(trigrams) - len(set(trigrams))) / len(trigrams), 0.0, 1.0))

    return [sentence_var, lexical_diversity, repetition_ratio]


def _load_training_data() -> tuple[list[str], list[int]]:
    if not TRAINING_DATA_PATH.exists():
        return [], []

    texts: list[str] = []
    labels: list[int] = []

    for line in TRAINING_DATA_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue

        text = str(obj.get("text", "")).strip()
        label = obj.get("label", None)
        if not text:
            continue
        if label in (0, 1):
            texts.append(text)
            labels.append(int(label))

    return texts, labels


def _fallback_bootstrap_corpus() -> tuple[list[str], list[int]]:
    human = [
        "The interview transcripts revealed mixed perceptions among faculty, especially regarding citation practices and incremental revisions during drafting.",
        "Our methodology section documents sampling criteria, informed consent procedures, and statistical tests selected for each hypothesis.",
        "Students compared two journal articles and discussed where the authors disagreed on interpretation of the same evidence.",
        "The lab report includes anomalies, discarded trials, and a reflection on how measurement error influenced confidence intervals.",
        "I revised this paragraph after peer feedback because my original thesis statement was too broad and lacked textual support.",
        "In historical writing, primary-source reliability depends on context, intended audience, and the political incentives of the author.",
        "The argument is persuasive in part, but the evidence from longitudinal data is not strong enough to support causality.",
        "The discussion highlights what remains uncertain and why future replication is necessary before policy recommendations are made.",
        "A close reading of the poem shows a shift in tone after line twelve, where imagery transitions from concrete to abstract.",
        "I compared three frameworks and selected the one that balanced interpretability, fairness constraints, and deployment overhead.",
    ]

    ai = [
        "This section provides a comprehensive and coherent overview of the topic, emphasizing clarity, consistency, and structured progression of ideas.",
        "In conclusion, the analysis demonstrates significant implications, highlighting key trends, notable outcomes, and practical recommendations for future work.",
        "The paragraph maintains uniform style and stable sentence cadence, ensuring readability, precision, and systematic organization throughout.",
        "Overall, the discussion integrates multiple dimensions, offering balanced insights, contextual interpretation, and logically sequenced synthesis.",
        "The response is designed to be concise yet comprehensive, presenting aligned arguments, supporting rationale, and coherent transitions.",
        "This explanation adopts an academic tone, preserving formal vocabulary, controlled rhythm, and consistent semantic framing across sentences.",
        "The generated content prioritizes fluency and structure, reducing ambiguity while maintaining a polished and standardized narrative voice.",
        "The following passage summarizes major factors, outlines implications, and reiterates findings in a smooth and methodical manner.",
        "The model-generated paragraph demonstrates repetitive construction, predictable phrasing, and high stylistic uniformity in delivery.",
        "This answer delivers a clear framework, expands each component systematically, and concludes with actionable guidance for implementation.",
    ]

    # Duplicate with slight perturbations to stabilize CV for tiny fallback data.
    texts = human + ai
    labels = [0] * len(human) + [1] * len(ai)

    texts.extend([f"{text} Additional contextual detail is included for nuance." for text in human])
    labels.extend([0] * len(human))

    texts.extend([f"{text} Furthermore, this structured summary reinforces consistency and coherence." for text in ai])
    labels.extend([1] * len(ai))

    return texts, labels
