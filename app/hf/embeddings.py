"""CPU-optimized Hugging Face embeddings for Teslas.ai.

Provides a singleton SentenceTransformer encoder restricted to CPU usage
and capped batch sizes to protect RAM/CPU budgets.
"""

from __future__ import annotations

import os
from functools import lru_cache
from threading import Lock
from typing import Dict, Iterable, List, Sequence

from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Enforce on-disk cache and CPU-only execution
os.environ.setdefault("HF_HOME", "/data/hf")
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

_DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
_BATCH_LIMIT = 32


class HfEmbeddingService(Embeddings):
    """Hugging Face embedding service backed by sentence-transformers.

    Implements LangChain's Embeddings interface for compatibility with existing
    Chroma usage while ensuring CPU-only execution and a capped batch size.
    """

    def __init__(self, model_name: str | None = None) -> None:
        chosen_model = model_name or getattr(settings, "EMBEDDING_MODEL", None) or _DEFAULT_MODEL
        logger.info(f"Loading HF embedding model (CPU): {chosen_model}")
        self.model = SentenceTransformer(chosen_model, device="cpu")
        self.model.max_seq_length = getattr(self.model, "max_seq_length", 512)
        self._cache: Dict[str, List[float]] = {}
        self._lock = Lock()
        logger.info("HF embedding model ready (CPU)")

    def _encode(self, texts: Sequence[str]) -> List[List[float]]:
        if not texts:
            return []

        # De-duplicate to avoid redundant computation
        missing = [t for t in texts if t not in self._cache]
        if missing:
            embeddings = self.model.encode(
                missing,
                batch_size=min(_BATCH_LIMIT, len(missing)),
                convert_to_numpy=True,
                convert_to_tensor=False,
                show_progress_bar=False,
                device="cpu",
                normalize_embeddings=False,
            )
            for text, vector in zip(missing, embeddings):
                # Store as plain list to keep serialization/lightweight
                self._cache[text] = vector.tolist()

        return [self._cache[t] for t in texts]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents using CPU-only encoder."""
        with self._lock:
            return self._encode(texts)

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query string."""
        with self._lock:
            return self._encode([text])[0] if text else []

    # Backwards-compatible helpers used elsewhere in the codebase
    def embed_text(self, text: str) -> List[float]:
        return self.embed_query(text)

    def embed_texts(self, texts: Iterable[str]) -> List[List[float]]:
        return self.embed_documents(list(texts))


# Singleton access
@lru_cache(maxsize=1)
def get_hf_embeddings() -> HfEmbeddingService:
    """Return a process-wide singleton embedding service."""
    return HfEmbeddingService()
