"""Document reranking for improved retrieval."""

from typing import List

from app.llm.embeddings import get_embeddings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentReranker:
    """Rerank documents based on relevance."""
    
    def __init__(self):
        """Initialize reranker."""
        self.embeddings = get_embeddings()
    
    def rerank(self, query: str, documents: List[str], top_k: int = 3) -> List[str]:
        """Rerank documents by semantic similarity to query."""
        logger.info(f"Reranking {len(documents)} documents")
        
        # Compute similarities
        query_embedding = self.embeddings.embed_text(query)
        
        scores = []
        for doc in documents:
            doc_embedding = self.embeddings.embed_text(doc)
            
            # Cosine similarity
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity
            
            sim = cosine_similarity(
                np.array(query_embedding).reshape(1, -1),
                np.array(doc_embedding).reshape(1, -1)
            )[0][0]
            scores.append(sim)
        
        # Sort and return top-k
        ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        reranked_docs = [doc for doc, _ in ranked[:top_k]]
        
        logger.info(f"Reranked to top {len(reranked_docs)} documents")
        return reranked_docs
