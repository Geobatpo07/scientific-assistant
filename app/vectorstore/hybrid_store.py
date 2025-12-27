"""
Hybrid vector store combining FAISS (speed) and ChromaDB (knowledge).
Built on top of existing ChromaVectorStore.
"""

from typing import List, Dict

from app.vectorstore.chroma import ChromaVectorStore
from app.vectorstore.faiss_index import FaissIndex
from app.llm.embeddings import get_embeddings
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class HybridVectorStore:
    """
    Hybrid retrieval:
    - FAISS for fast candidate selection
    - ChromaDB for rich retrieval and reranking
    """

    def __init__(self):
        self.chroma = ChromaVectorStore()
        self.embeddings = get_embeddings()

        # Infer embedding dimension dynamically
        test_vec = self.embeddings.embed_text("dimension check")
        self.faiss = FaissIndex(dim=len(test_vec))

    def add_texts(
        self,
        texts: List[str],
        metadatas: List[dict] | None = None,
        ids: List[str] | None = None,
    ) -> List[str]:
        """
        Add texts to both ChromaDB and FAISS.
        """
        # Let Chroma generate embeddings & ids
        ids = self.chroma.add_texts(
            texts=texts,
            metadatas=metadatas,
            ids=ids,
        )

        # Recompute embeddings for FAISS (explicit & controlled)
        embeddings = self.embeddings.embed_texts(texts)

        self.faiss.add(
            embeddings=embeddings,
            ids=ids,
        )

        logger.info(
            "Hybrid store updated",
            documents=len(ids),
        )

        return ids

    def search(
        self,
        query: str,
        k: int = 5,
        faiss_k: int = 25,
    ) -> List[Dict]:
        """
        Hybrid search:
        1. FAISS → candidate ids
        2. ChromaDB → refined semantic + metadata search
        """
        logger.info(f"Hybrid search for: {query[:80]}")

        query_embedding = self.embeddings.embed_text(query)

        # Step 1: FAISS candidate selection
        candidate_ids = self.faiss.search(
            query_embedding=query_embedding,
            k=faiss_k,
        )

        if not candidate_ids:
            # fallback to pure Chroma search
            logger.warning("FAISS returned no candidates, falling back to ChromaDB")
            return self.chroma.search(query=query, k=k)

        # Step 2: ChromaDB filtered retrieval
        try:
            results = self.chroma.collection.get(
                ids=candidate_ids,
                include=["documents", "metadatas"],
            )
        except Exception:
            return self.chroma.search(query=query, k=k)

        # Reuse your existing reranking logic
        documents = results.get("documents") or []
        metadatas = results.get("metadatas") or []

        formatted = []
        for i, content in enumerate(documents):
            item = {
                "content": content,
                "metadata": metadatas[i] if i < len(metadatas) else {},
            }
            try:
                item["score"] = self.embeddings.similarity(query, content)
            except Exception:
                item["score"] = None
            formatted.append(item)

        formatted.sort(
            key=lambda x: x["score"] if x["score"] is not None else float("-inf"),
            reverse=True,
        )

        logger.info(f"Hybrid search returned {len(formatted[:k])} results")
        return formatted[:k]

    def count(self) -> int:
        """Return number of documents stored in ChromaDB."""
        try:
            return self.chroma.count()
        except Exception:
            return 0
