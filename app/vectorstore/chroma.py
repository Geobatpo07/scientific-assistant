"""ChromaDB integration backed by Hugging Face embeddings (CPU-only)."""

from __future__ import annotations

import uuid
from typing import Dict, List, Optional

import chromadb
from chromadb.config import Settings

from app.config import settings
from app.hf.embeddings import get_hf_embeddings, HfEmbeddingService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChromaVectorStore:
    """ChromaDB wrapper that persists documents, embeddings, and metadata."""

    def __init__(
        self,
        collection_name: str = settings.CHROMA_COLLECTION_NAME,
        persist_dir: str = str(settings.CHROMA_PERSIST_DIR),
        embedding_service: Optional[HfEmbeddingService] = None,
    ) -> None:
        logger.info(f"Initializing ChromaDB (persistent) collection={collection_name}")

        self.collection_name = collection_name
        self.persist_dir = persist_dir
        self.embeddings = embedding_service or get_hf_embeddings()

        client_settings = Settings(anonymized_telemetry=False)

        if "test" in collection_name.lower():
            self.client = chromadb.EphemeralClient(settings=client_settings)
            try:
                self.client.delete_collection(name=collection_name)
            except Exception:
                pass
        else:
            self.client = chromadb.PersistentClient(path=persist_dir, settings=client_settings)

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        logger.info(f"ChromaDB ready. Count={self.count()}")

    def _normalize_inputs(
        self,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
        embeddings: Optional[List[List[float]]] = None,
    ) -> Dict[str, List]:
        if metadatas is None:
            metadatas = [{"source": "unknown"} for _ in texts]
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in texts]
        if embeddings is None:
            embeddings = self.embeddings.embed_documents(texts)

        if not (len(texts) == len(metadatas) == len(ids) == len(embeddings)):
            raise ValueError("Texts, metadatas, ids, and embeddings must align")

        return {
            "documents": texts,
            "metadatas": metadatas,
            "ids": ids,
            "embeddings": embeddings,
        }

    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
        embeddings: Optional[List[List[float]]] = None,
    ) -> List[str]:
        """Persist texts + metadata + embeddings into ChromaDB."""
        payload = self._normalize_inputs(texts, metadatas, ids, embeddings)
        self.collection.add(**payload)
        logger.info("ChromaDB add_texts", count=len(payload["ids"]))
        return payload["ids"]

    def search(self, query: str, k: int = 5) -> List[dict]:
        """Vector search using stored embeddings (no re-embedding of documents)."""
        logger.info(f"Chroma search: {query[:80]}")

        query_embedding = self.embeddings.embed_query(query)
        if not query_embedding:
            return []

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances", "ids"],
        )

        docs = results.get("documents") or [[]]
        metas = results.get("metadatas") or [[]]
        distances = results.get("distances") or [[]]
        ids = results.get("ids") or [[]]

        formatted = []
        for idx, content in enumerate(docs[0]):
            meta = metas[0][idx] if idx < len(metas[0]) else {}
            distance = distances[0][idx] if idx < len(distances[0]) else None
            doc_id = ids[0][idx] if idx < len(ids[0]) else None
            score = 1.0 / (1.0 + distance) if distance is not None else None
            formatted.append(
                {
                    "id": doc_id,
                    "content": content,
                    "metadata": meta,
                    "distance": distance,
                    "score": score,
                }
            )

        logger.info(f"Chroma search returned {len(formatted)} results")
        return formatted

    def get_by_ids(self, ids: List[str]) -> List[dict]:
        """Return documents + metadata by ids without re-embedding."""
        if not ids:
            return []

        results = self.collection.get(ids=ids, include=["documents", "metadatas", "embeddings"])
        documents = results.get("documents")
        metadatas = results.get("metadatas")
        embeddings = results.get("embeddings")
        
        # Handle None or numpy arrays
        if documents is None:
            documents = []
        if metadatas is None:
            metadatas = []
        if embeddings is None:
            embeddings = []
            
        returned_ids = ids  # Use the requested ids since ChromaDB returns them in order

        assembled = []
        for i, content in enumerate(documents):
            assembled.append(
                {
                    "id": returned_ids[i] if i < len(returned_ids) else None,
                    "content": content,
                    "metadata": metadatas[i] if i < len(metadatas) else {},
                    "embedding": embeddings[i] if i < len(embeddings) else None,
                }
            )
        return assembled

    def export_embeddings(self) -> Dict[str, List]:
        """Export embeddings + ids to allow FAISS rebuild."""
        data = self.collection.get(include=["embeddings"])
        embeddings = data.get("embeddings")
        # Handle numpy arrays or None
        if embeddings is None:
            embeddings = []
        return {
            "ids": data.get("ids") or [],
            "embeddings": embeddings if hasattr(embeddings, '__len__') else [],
        }

    def delete_collection(self) -> None:
        """Delete the entire collection."""
        logger.warning(f"Deleting collection: {self.collection_name}")
        try:
            self.client.delete_collection(name=self.collection_name)
        except Exception:
            pass

    def count(self) -> int:
        """Number of documents in collection."""
        try:
            return self.collection.count()
        except Exception:
            return 0
