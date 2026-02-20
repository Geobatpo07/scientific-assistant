"""Hybrid vector store combining FAISS (speed) + ChromaDB (persistence) + HF reranker.

Pipeline:
  Query → HF Embedding → FAISS (top-N candidates) → ChromaDB (metadata) → HF Reranker → Top-K

Uses:
  - HF Embeddings: CPU-only sentence-transformers
  - FAISS: Fast vector search (embeddings + ids only)
  - ChromaDB: Persistent storage (documents + embeddings + metadata)
  - HF Reranker: Scientific relevance ranking via CrossEncoder
"""

from typing import Dict, Iterable, List

from app.config import settings
from app.hf.embeddings import get_hf_embeddings
from app.hf.reranker import get_hf_reranker
from app.vectorstore.chroma import ChromaVectorStore
from app.vectorstore.faiss_index import FaissIndex
from app.utils.logger import get_logger

logger = get_logger(__name__)


class HybridVectorStore:
    """Hybrid retrieval combining FAISS speed and ChromaDB persistence with HF reranking."""

    def __init__(self) -> None:
        logger.info("Initializing HybridVectorStore (HF embeddings + FAISS + ChromaDB + HF reranker)")
        
        self.chroma = ChromaVectorStore()
        self.embeddings = get_hf_embeddings()
        self.reranker = get_hf_reranker()

        # FAISS stores embeddings + ids only (lazy init)
        test_vec = self.embeddings.embed_query("dimension check")
        self.faiss = FaissIndex(dim=len(test_vec), num_threads=2)
        
        # Try to rebuild FAISS from persisted ChromaDB embeddings
        self._rebuild_faiss_from_chroma()
        logger.info("HybridVectorStore ready")

    def _rebuild_faiss_from_chroma(self) -> None:
        """Rebuild FAISS index from persisted ChromaDB embeddings."""
        export_data = self.chroma.export_embeddings()
        ids = export_data.get("ids") or []
        embeddings = export_data.get("embeddings")
        
        # Handle None or numpy arrays
        if embeddings is None:
            embeddings = []
        
        if ids and len(embeddings) > 0 and len(ids) == len(embeddings):
            try:
                self.faiss.rebuild(embeddings, ids)
                logger.info(f"FAISS rebuilt from ChromaDB ({len(ids)} vectors)")
            except Exception as e:
                logger.warning(f"FAISS rebuild failed: {e}, will accumulate dynamically")
        else:
            logger.info("ChromaDB empty, FAISS will accumulate from new additions")

    def add_texts(
        self,
        texts: List[str],
        metadatas: List[dict] | None = None,
        ids: List[str] | None = None,
    ) -> List[str]:
        """Add texts to ChromaDB + FAISS using HF embeddings."""
        if not texts:
            return []

        logger.info(f"Hybrid add_texts: {len(texts)} documents")

        # Add to ChromaDB (handles embedding generation)
        chroma_embeddings = self.embeddings.embed_documents(texts)
        returned_ids = self.chroma.add_texts(
            texts=texts,
            metadatas=metadatas,
            ids=ids,
            embeddings=chroma_embeddings,
        )

        # Add same embeddings to FAISS
        self.faiss.add(embeddings=chroma_embeddings, ids=returned_ids)
        
        logger.info(f"Hybrid store: added {len(returned_ids)} documents (ChromaDB + FAISS)")
        return returned_ids


    def search(
        self,
        query: str,
        k: int = 5,
        faiss_k: int = 30,
        rerank: bool = True,
    ) -> List[Dict]:
        """Hybrid search pipeline: FAISS → ChromaDB → HF Reranker.

        Args:
            query: User query string.
            k: Final top-K results to return.
            faiss_k: Number of FAISS candidates to retrieve.
            rerank: Whether to apply HF CrossEncoder reranking.
        """
        logger.info(f"Hybrid search: {query[:80]} (rerank={rerank})")

        query_embedding = self.embeddings.embed_query(query)
        if not query_embedding:
            return []

        # Step 1: FAISS fast candidate retrieval
        candidate_ids = self.faiss.search(query_embedding=query_embedding, k=faiss_k)

        if not candidate_ids:
            logger.warning("FAISS returned no candidates, falling back to ChromaDB")
            return self._chroma_search(query=query, k=k)

        # Step 2: ChromaDB metadata + content retrieval
        candidates = self.chroma.get_by_ids(candidate_ids)
        if not candidates:
            logger.warning("ChromaDB returned no results for FAISS candidates")
            return self._chroma_search(query=query, k=k)

        # Step 3: HF CrossEncoder reranking (optional)
        if rerank:
            reranked = self.reranker.rerank(query=query, candidates=candidates, top_k=k)
            logger.info(f"Hybrid search: reranked {len(candidates)} → {len(reranked)} results")
            return reranked
        else:
            logger.info(f"Hybrid search: returned {min(len(candidates), k)} results (no reranking)")
            return candidates[:k]

    def _chroma_search(self, query: str, k: int = 5) -> List[Dict]:
        """Pure ChromaDB search fallback."""
        logger.info(f"Chroma fallback search: {query[:80]}")
        return self.chroma.search(query=query, k=k)


    def count(self) -> int:
        """Return number of documents in ChromaDB (source of truth)."""
        try:
            return self.chroma.count()
        except Exception:
            return 0
