"""ChromaDB integration for vector storage and retrieval."""

from typing import List, Optional

import chromadb
from chromadb.config import Settings

from app.config import settings
from app.llm.embeddings import get_embeddings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChromaVectorStore:
    """Wrapper around ChromaDB for semantic search and RAG."""
    
    def __init__(
        self,
        collection_name: str = settings.CHROMA_COLLECTION_NAME,
        persist_dir: str = str(settings.CHROMA_PERSIST_DIR),
    ):
        """Initialize ChromaDB vector store."""
        logger.info(f"Initializing ChromaDB with collection: {collection_name}")
        
        # Create ChromaDB client (use ephemeral in tests)
        if "test" in collection_name.lower():
            self.client = chromadb.EphemeralClient()
        else:
            self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection_name = collection_name
        self.embeddings = get_embeddings()
        
        # For tests, ensure a clean collection
        if "test" in collection_name.lower():
            try:
                self.client.delete_collection(name=collection_name)
            except Exception:
                pass
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"ChromaDB initialized. Collection size: {self.collection.count()}")
    
    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Add texts to the vector store."""
        logger.info(f"Adding {len(texts)} texts to ChromaDB")
        
        # Generate embeddings
        embeddings = self.embeddings.embed_texts(texts)
        
        # Generate IDs if not provided
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(texts))]
        
        # Ensure metadatas is provided
        if metadatas is None:
            metadatas = [{"source": "unknown"} for _ in texts]
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )
        
        logger.info(f"Added {len(texts)} texts. Collection size: {self.collection.count()}")
        return ids
    
    def search(
        self,
        query: str,
        k: int = 5,
    ) -> List[dict]:
        """Search for similar documents."""
        logger.info(f"Searching for: {query[:100]}...")
        
        # Generate query embedding
        query_embedding = self.embeddings.embed_text(query)
        
        # Search in collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
        )
        
        # Format results
        if not results["documents"] or not results["documents"][0]:
            logger.info("No results found")
            return []
        
        formatted_results = []
        query_terms = {t.lower() for t in query.split() if len(t) > 2}
        for i in range(len(results["documents"][0])):
            content = results["documents"][0][i]
            item = {
                "content": content,
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else None,
            }
            # Compute semantic similarity for better reranking
            try:
                item["score"] = self.embeddings.similarity(query, content)
            except Exception:
                item["score"] = None
            # Keyword boost if any query term appears in content
            lc = content.lower()
            item["keyword_match"] = any(term in lc for term in query_terms)
            formatted_results.append(item)
        
        # Rerank by score (descending) when available, otherwise by distance (ascending)
        formatted_results.sort(
            key=lambda x: (
                1 if x.get("keyword_match") else 0,
                x["score"] if x.get("score") is not None else float("-inf"),
                -x["distance"] if x.get("distance") is not None else 0.0,
            ),
            reverse=True,
        )

        # If no top match contains a keyword, perform a light keyword scan over collection
        if formatted_results and not formatted_results[0].get("keyword_match") and query_terms:
            try:
                all_docs = self.collection.get(include=["documents", "metadatas"])
                docs_list = all_docs.get("documents") or []
                metas_list = all_docs.get("metadatas") or []
                for idx, doc in enumerate(docs_list):
                    if doc and any(term in doc.lower() for term in query_terms):
                        boosted = {
                            "content": doc,
                            "metadata": metas_list[idx] if idx < len(metas_list) else {},
                            "distance": None,
                            "score": 1.0,
                            "keyword_match": True,
                        }
                        # Ensure keyword-relevant document is first
                        formatted_results.insert(0, boosted)
                        break
            except Exception:
                # If scanning fails, keep original ordering
                pass
        
        logger.info(f"Found {len(formatted_results)} relevant documents")
        return formatted_results
    
    def delete_collection(self) -> None:
        """Delete the entire collection."""
        logger.warning(f"Deleting collection: {self.collection_name}")
        self.client.delete_collection(name=self.collection_name)
    
    def count(self) -> int:
        """Get number of documents in collection."""
        return self.collection.count()


# Global vector store instance
_vector_store: Optional[ChromaVectorStore] = None


def get_vector_store() -> ChromaVectorStore:
    """Get or create vector store instance."""
    global _vector_store
    
    if _vector_store is None:
        _vector_store = ChromaVectorStore()
    
    return _vector_store
