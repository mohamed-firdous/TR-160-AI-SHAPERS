from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REFERENCE_FILE = BASE_DIR / "data" / "reference_corpus.txt"


def load_reference_corpus(custom_reference: str = "") -> list[str]:
    corpus: list[str] = []

    if REFERENCE_FILE.exists():
        corpus.extend([line.strip() for line in REFERENCE_FILE.read_text(encoding="utf-8").splitlines() if line.strip()])

    if custom_reference and custom_reference.strip():
        corpus.extend([line.strip() for line in custom_reference.splitlines() if line.strip()])

    return corpus
