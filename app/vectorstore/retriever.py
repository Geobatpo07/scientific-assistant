"""Retriever for RAG pipeline using hybrid vector store."""

from typing import TYPE_CHECKING, List

from app.utils.logger import get_logger

if TYPE_CHECKING:
    from app.vectorstore.hybrid_store import HybridVectorStore

logger = get_logger(__name__)


class Retriever:
    """Retrieve documents from hybrid vector store (FAISS + ChromaDB + HF reranker)."""
    
    def __init__(self, vector_store: "HybridVectorStore"):
        """Initialize retriever with hybrid store."""
        self.vector_store = vector_store
    
    def retrieve(self, query: str, k: int = 5) -> List[str]:
        """Retrieve top-k relevant documents."""
        results = self.vector_store.search(query, k=k, rerank=True)
        return [result["content"] for result in results]
    
    def retrieve_with_metadata(self, query: str, k: int = 5) -> List[dict]:
        """Retrieve documents with metadata using hybrid search + reranking."""
        return self.vector_store.search(query, k=k, rerank=True)
    
    def format_context(self, documents: List[str]) -> str:
        """Format documents into context string."""
        return "\n\n---\n\n".join(documents)
