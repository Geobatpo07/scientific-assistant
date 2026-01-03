"""Hugging Face utilities (CPU-only) for Teslas.ai.

This module provides three main components:

1. embeddings.py - HfEmbeddingService
   - Generates embeddings for documents and queries
   - Uses all-MiniLM-L6-v2 (CPU-only)

2. reranker.py - HfCrossEncoderReranker
   - Reranks retrieved documents by relevance
   - Uses cross-encoder/ms-marco-MiniLM-L-6-v2 (CPU-only)

3. context_engineering.py - ContextEngineer
   - Normalizes user queries
   - Compresses retrieved context
   - Uses google/flan-t5-base (CPU-only, preprocessing only)

All models are CPU-only and loaded once per process.
No reasoning or conclusion-drawing is performed by any module.
"""

from app.hf.embeddings import get_hf_embeddings, HfEmbeddingService
from app.hf.reranker import get_hf_reranker, HfCrossEncoderReranker
from app.hf.context_engineering import get_context_engineer, ContextEngineer

__all__ = [
    "get_hf_embeddings",
    "HfEmbeddingService",
    "get_hf_reranker",
    "HfCrossEncoderReranker",
    "get_context_engineer",
    "ContextEngineer",
]
