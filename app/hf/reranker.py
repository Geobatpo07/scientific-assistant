"""Hugging Face CrossEncoder reranker (CPU-only).

Implements a lightweight reranker for scientific retrieval using
cross-encoder/ms-marco-MiniLM-L-6-v2. The model is loaded once and reused
across all requests, with conservative batch sizing for CPU efficiency.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Dict, List, Sequence

from sentence_transformers import CrossEncoder

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Keep HF artifacts on disk and disable GPU usage
os.environ.setdefault("HF_HOME", "/data/hf")
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

_DEFAULT_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
_BATCH_LIMIT = 32


class HfCrossEncoderReranker:
    """CPU-only CrossEncoder reranker for scientific retrieval."""

    def __init__(self, model_name: str | None = None, default_top_k: int = 5) -> None:
        chosen_model = model_name or _DEFAULT_MODEL
        logger.info(f"Loading HF CrossEncoder reranker (CPU): {chosen_model}")
        self.model = CrossEncoder(chosen_model, device="cpu")
        self.default_top_k = default_top_k
        logger.info("HF CrossEncoder reranker ready (CPU)")

    def rerank(self, query: str, candidates: Sequence[Dict], top_k: int | None = None) -> List[Dict]:
        """Rerank candidates using cross-encoder relevance scores.

        Args:
            query: User query string.
            candidates: Sequence of dicts containing at least a ``content`` key.
            top_k: Optional override for number of items to return.
        """
        if not candidates:
            return []

        top_n = top_k or self.default_top_k
        pairs = [(query, c.get("content", "")) for c in candidates if c.get("content")]
        if not pairs:
            return []

        scores = self.model.predict(
            pairs,
            batch_size=min(_BATCH_LIMIT, len(pairs)),
            show_progress_bar=False,
        )

        # Align scores back to original candidate ordering
        scored: List[Dict] = []
        score_iter = iter(scores.tolist() if hasattr(scores, "tolist") else list(scores))
        for candidate in candidates:
            content = candidate.get("content")
            if not content:
                continue
            score = next(score_iter)
            enriched = dict(candidate)
            enriched["score"] = float(score)
            scored.append(enriched)

        scored.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        return scored[:top_n]


@lru_cache(maxsize=1)
def get_hf_reranker() -> HfCrossEncoderReranker:
    """Return a process-wide singleton reranker."""
    return HfCrossEncoderReranker(default_top_k=getattr(settings, "RERANK_TOP_K", 5))
