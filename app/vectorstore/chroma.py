"""ChromaDB integration for vector storage and retrieval using langchain-chroma."""

from typing import List, Optional

import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from app.config import settings
from app.llm.embeddings import get_embeddings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChromaVectorStore:
    """Wrapper around ChromaDB for semantic search and RAG using langchain-chroma."""
    
    def __init__(
        self,
        collection_name: str = settings.CHROMA_COLLECTION_NAME,
        persist_dir: str = str(settings.CHROMA_PERSIST_DIR),
    ):
        """Initialize ChromaDB vector store with langchain-chroma integration."""
        logger.info(f"Initializing ChromaDB with langchain-chroma integration: {collection_name}")
        
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        self.embeddings = get_embeddings()
        
        # Create ChromaDB client (use ephemeral in tests)
        if "test" in collection_name.lower():
            self.client = chromadb.EphemeralClient()
            # For tests, ensure a clean collection
            try:
                self.client.delete_collection(name=collection_name)
            except Exception:
                pass
        else:
            self.client = chromadb.PersistentClient(path=persist_dir)
        
        # Initialize Chroma with langchain-chroma integration
        self.vectorstore = Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embeddings,
            collection_metadata={"hnsw:space": "cosine"}
        )
        
        # Keep reference to underlying collection for direct operations
        self.collection = self.vectorstore._collection
        
        logger.info(f"ChromaDB initialized with langchain-chroma. Collection size: {self.count()}")
    
    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Add texts to the vector store using langchain-chroma."""
        logger.info(f"Adding {len(texts)} texts to ChromaDB via langchain-chroma")
        
        # Ensure metadatas is provided
        if metadatas is None:
            metadatas = [{"source": "unknown"} for _ in texts]
        
        # Use langchain-chroma's add_texts method
        # This handles embedding generation automatically
        result_ids = self.vectorstore.add_texts(
            texts=texts,
            metadatas=metadatas,
            ids=ids,
        )
        
        logger.info(f"Added {len(texts)} texts. Collection size: {self.count()}")
        return result_ids
    
    def add_documents(
        self,
        documents: List[Document],
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Add LangChain documents to the vector store."""
        logger.info(f"Adding {len(documents)} documents to ChromaDB")
        
        # Use langchain-chroma's add_documents method
        result_ids = self.vectorstore.add_documents(
            documents=documents,
            ids=ids,
        )
        
        logger.info(f"Added {len(documents)} documents. Collection size: {self.count()}")
        return result_ids
    
    def search(
        self,
        query: str,
        k: int = 5,
    ) -> List[dict]:
        """Search for similar documents using langchain-chroma similarity search."""
        logger.info(f"Searching for: {query[:100]}...")
        
        # Use langchain-chroma's similarity_search_with_score method
        results = self.vectorstore.similarity_search_with_score(
            query=query,
            k=k,
        )
        
        # Format results
        if not results:
            logger.info("No results found")
            return []
        
        formatted_results = []
        query_terms = {t.lower() for t in query.split() if len(t) > 2}
        
        for doc, distance in results:
            content = doc.page_content
            item = {
                "content": content,
                "metadata": doc.metadata,
                "distance": distance,
            }
            # Compute semantic similarity for better reranking
            try:
                # Convert distance to similarity score (lower distance = higher similarity)
                item["score"] = 1.0 / (1.0 + distance) if distance is not None else None
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
    
    def as_retriever(self, **kwargs):
        """Return a LangChain retriever interface."""
        return self.vectorstore.as_retriever(**kwargs)
    
    def delete_collection(self) -> None:
        """Delete the entire collection."""
        logger.warning(f"Deleting collection: {self.collection_name}")
        self.vectorstore.delete_collection()
        try:
            self.client.delete_collection(name=self.collection_name)
        except Exception:
            pass
    
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
