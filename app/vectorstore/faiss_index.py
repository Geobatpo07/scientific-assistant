"""
FAISS index for fast vector candidate retrieval (Teslas.ai).

CPU-friendly wrapper that stores only embeddings + ids and caps FAISS threads.
"""

from typing import Iterable, List

import faiss
import numpy as np

from app.utils.logger import get_logger

logger = get_logger(__name__)


class FaissIndex:
    """Lightweight FAISS index storing embeddings + ids only."""

    def __init__(self, dim: int, num_threads: int = 2):
        self.dim = dim
        self.ids: list[str] = []
        faiss.omp_set_num_threads(num_threads)
        self.index = faiss.IndexFlatL2(dim)

    def add(self, embeddings: List[List[float]], ids: List[str]) -> None:
        if not embeddings:
            return
        if len(embeddings) != len(ids):
            raise ValueError("Embeddings and ids length mismatch")

        vectors = np.asarray(embeddings, dtype="float32")
        if vectors.ndim != 2 or vectors.shape[1] != self.dim:
            raise ValueError(f"Expected embeddings with dim={self.dim}, got {vectors.shape}")

        self.index.add(vectors)
        self.ids.extend(ids)

        logger.info("FAISS index updated", vectors=self.index.ntotal)

    def rebuild(self, embeddings: Iterable[List[float]], ids: Iterable[str]) -> None:
        """Rebuild index from persisted embeddings (e.g., Chroma export)."""
        embedding_list = list(embeddings)
        id_list = list(ids)
        self.index.reset()
        self.ids = []
        if embedding_list:
            self.add(embedding_list, id_list)

    def search(self, query_embedding: List[float], k: int = 20) -> List[str]:
        if self.index.ntotal == 0:
            return []

        capped_k = min(k, len(self.ids))
        query = np.asarray([query_embedding], dtype="float32")
        _, indices = self.index.search(query, capped_k)

        return [
            self.ids[i]
            for i in indices[0]
            if 0 <= i < len(self.ids)
        ]
