"""Retriever for RAG pipeline."""

from typing import List

from app.vectorstore.chroma import ChromaVectorStore
from app.utils.logger import get_logger

logger = get_logger(__name__)


class Retriever:
    """Retrieve relevant documents from vector store."""
    
    def __init__(self, vector_store: ChromaVectorStore):
        """Initialize retriever."""
        self.vector_store = vector_store
    
    def retrieve(self, query: str, k: int = 5) -> List[str]:
        """Retrieve top-k relevant documents."""
        results = self.vector_store.search(query, k=k)
        return [result["content"] for result in results]
    
    def retrieve_with_metadata(self, query: str, k: int = 5) -> List[dict]:
        """Retrieve documents with metadata."""
        return self.vector_store.search(query, k=k)
    
    def format_context(self, documents: List[str]) -> str:
        """Format documents into context string."""
        return "\n\n---\n\n".join(documents)
