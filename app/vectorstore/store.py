"""Vector store factory and singleton manager.

Returns HybridVectorStore (FAISS + ChromaDB + HF Reranker)
"""

from typing import Optional

from app.vectorstore.hybrid_store import HybridVectorStore
from app.utils.logger import get_logger

logger = get_logger(__name__)

_hybrid_store: Optional[HybridVectorStore] = None


def get_vector_store() -> HybridVectorStore:
    """Get or create hybrid vector store singleton.
    
    Returns a HybridVectorStore combining:
    - HF Embeddings (CPU-only)
    - FAISS (fast retrieval)
    - ChromaDB (persistence)
    - HF CrossEncoder Reranker (scientific relevance)
    """
    global _hybrid_store
    if _hybrid_store is None:
        logger.info("Creating HybridVectorStore singleton")
        _hybrid_store = HybridVectorStore()
    return _hybrid_store
