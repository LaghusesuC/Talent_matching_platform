"""
Embeddings service for semantic similarity scoring.
Uses Google Gemini Embeddings API (models/text-embedding-004) when available,
with local Sentence-Transformers or token similarity fallback.
Zero heavy local dependencies (PyTorch/CUDA free) for serverless deployment (< 50MB).
"""
from typing import Optional
from app.core.config import get_settings

settings = get_settings()

_model = None
_model_failed = False
_gemini_configured = False
_gemini_failed = False


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
    """Compute semantic similarity between two texts.
    1. Primary: Google Gemini text-embedding-004 (lightweight, zero bundle size overhead)
    2. Secondary: Local SentenceTransformer if installed
    3. Fallback: Pure-Python Jaccard & N-gram token similarity
    """
    global _gemini_configured, _gemini_failed
    if not text1 or not text2:
        return 50.0

    # 1. Try Gemini Embeddings API if configured and hasn't failed
    if not _gemini_failed and settings.GEMINI_API_KEY and not settings.GEMINI_API_KEY.startswith("your-"):
        try:
            import google.generativeai as genai
            if not _gemini_configured:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                _gemini_configured = True
            r1 = genai.embed_content(
                model="models/text-embedding-004",
                content=text1[:1000],
                task_type="semantic_similarity"
            )
            r2 = genai.embed_content(
                model="models/text-embedding-004",
                content=text2[:1000],
                task_type="semantic_similarity"
            )
            v1 = r1.get('embedding', [])
            v2 = r2.get('embedding', [])
            if v1 and v2:
                dot = sum(a * b for a, b in zip(v1, v2))
                norm1 = sum(a * a for a in v1) ** 0.5
                norm2 = sum(b * b for b in v2) ** 0.5
                if norm1 > 0 and norm2 > 0:
                    sim = dot / (norm1 * norm2)
                    return round(max(0.0, min(100.0, (sim + 1) / 2 * 100)), 2)
        except Exception:
            _gemini_failed = True

    # 2. Try local SentenceTransformer if available in environment
    model = _get_model()
    if model is not None:
        try:
            import numpy as np
            embeddings = model.encode([text1[:1000], text2[:1000]])
            a, b = embeddings[0], embeddings[1]
            sim = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))
            return round(max(0.0, min(100.0, (sim + 1) / 2 * 100)), 2)
        except Exception:
            pass

    # 3. Lightweight pure-Python fallback (zero dependencies, instant execution)
    try:
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 50.0
        overlap = len(words1 & words2)
        union = len(words1 | words2)
        jaccard = (overlap / union) * 100 if union > 0 else 50.0
        return round(min(95.0, max(25.0, jaccard * 2.8 + 20.0)), 2)
    except Exception:
        return 50.0
