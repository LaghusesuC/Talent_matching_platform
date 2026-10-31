"""
Sentence-Transformer embeddings service for semantic similarity scoring.
"""
from typing import Optional
from app.core.config import get_settings

settings = get_settings()

_model = None
_model_failed = False


def _get_model():
    global _model, _model_failed
    if _model_failed:
        return None
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(settings.EMBEDDING_MODEL)
        except Exception:
            _model = None
            _model_failed = True
    return _model


def semantic_similarity(text1: str, text2: str) -> float:
    """Compute cosine similarity between two texts using MiniLM embeddings."""
    model = _get_model()
    if model is None:
        return 0.5  # neutral fallback

    try:
        import numpy as np
        embeddings = model.encode([text1[:1000], text2[:1000]])
        # Cosine similarity
        a, b = embeddings[0], embeddings[1]
        sim = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))
        # Map from [-1,1] to [0,100]
        return round(max(0.0, min(100.0, (sim + 1) / 2 * 100)), 2)
    except Exception:
        return 50.0
