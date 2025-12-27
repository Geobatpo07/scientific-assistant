"""
FAISS index for fast vector candidate retrieval (Teslas.ai).
"""

from typing import List
import faiss
import numpy as np

from app.utils.logger import get_logger

logger = get_logger(__name__)


class FaissIndex:
    """Lightweight FAISS index storing embeddings + ids only."""

    def __init__(self, dim: int):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.ids: list[str] = []

    def add(self, embeddings: List[List[float]], ids: List[str]) -> None:
        vectors = np.array(embeddings, dtype="float32")
        self.index.add(vectors)
        self.ids.extend(ids)

        logger.info(
            "FAISS index updated",
            vectors=self.index.ntotal,
        )

    def search(self, query_embedding: List[float], k: int = 20) -> List[str]:
        if self.index.ntotal == 0:
            return []

        query = np.array([query_embedding], dtype="float32")
        _, indices = self.index.search(query, k)

        return [
            self.ids[i]
            for i in indices[0]
            if 0 <= i < len(self.ids)
        ]
