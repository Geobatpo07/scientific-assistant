from typing import Optional
from app.vectorstore.hybrid_store import HybridVectorStore

_hybrid_store: Optional[HybridVectorStore] = None


def get_vector_store() -> HybridVectorStore:
    global _hybrid_store
    if _hybrid_store is None:
        _hybrid_store = HybridVectorStore()
    return _hybrid_store
