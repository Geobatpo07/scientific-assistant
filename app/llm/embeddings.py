"""Embedding models for RAG and semantic search."""

from typing import List

from sentence_transformers import SentenceTransformer

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating embeddings using sentence-transformers."""
    
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL):
        """Initialize embedding service with specified model."""
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        logger.info(f"Embedding model loaded successfully")
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        return embeddings.tolist()
    
    def similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts."""
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        emb1 = np.array(self.embed_text(text1)).reshape(1, -1)
        emb2 = np.array(self.embed_text(text2)).reshape(1, -1)
        
        return float(cosine_similarity(emb1, emb2)[0][0])


# Global embedding service instance
_embedding_service: EmbeddingService | None = None


def get_embeddings() -> EmbeddingService:
    """Get or create embedding service instance."""
    global _embedding_service
    
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    
    return _embedding_service
