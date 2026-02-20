"""Context Engineering layer using Flan-T5 for query normalization and context compression.

This module provides lightweight, CPU-only preprocessing of user queries and retrieved
context BEFORE they are passed to the main LLM (Ollama / ChatOllama).

Key responsibilities:
- Normalize and clarify user queries
- Compress retrieved documents while preserving essential information
- Structure context for downstream reasoning

What this module does NOT do:
- NO reasoning or inference
- NO conclusions or decisions
- NO generation of final answers
- NO replacement of the main LLM

Architecture:
- Uses google/flan-t5-base (CPU-only)
- Model loaded ONCE per process (singleton pattern with lru_cache)
- max_new_tokens = 128 (conservative)
- No batching > 1
- No GPU usage

The ContextEngineer is intentionally lightweight and deterministic. It operates
as a preprocessing stage only, delegating all reasoning to ChatOllama.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Disable GPU and parallelize tokenizers
os.environ.setdefault("HF_HOME", str(settings.CACHE_DIR / "hf"))
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# Model constraints (MANDATORY)
_FLAN_T5_MODEL = "google/flan-t5-base"
_MAX_NEW_TOKENS = 128
_DEVICE = "cpu"


@lru_cache(maxsize=1)
def _get_flan_t5_model_cached():
    """Load Flan-T5 model once and cache it (singleton pattern).

    Returns
    -------
    tuple
        (model, tokenizer) - both loaded on CPU
    """
    logger.info(f"Loading Flan-T5 model for context engineering (CPU): {_FLAN_T5_MODEL}")

    tokenizer = AutoTokenizer.from_pretrained(_FLAN_T5_MODEL)
    model = AutoModelForSeq2SeqLM.from_pretrained(_FLAN_T5_MODEL, device_map=_DEVICE)
    model.eval()  # Inference mode

    logger.info("Flan-T5 context engineering model ready (CPU, inference mode)")
    return model, tokenizer


class ContextEngineer:
    """Lightweight context preprocessing using Flan-T5.

    This class provides two core operations:
    1. Query normalization: Clarify and standardize user queries
    2. Context compression: Compress retrieved documents while preserving
       definitions, assumptions, and equations

    The class maintains NO state about the user query or context.
    All operations are deterministic and independent.

    Attributes
    ----------
    model : transformers.AutoModelForSeq2SeqLM
        Cached Flan-T5 model (loaded once)
    tokenizer : transformers.AutoTokenizer
        Cached Flan-T5 tokenizer
    device : str
        Compute device ("cpu" only)
    max_new_tokens : int
        Maximum output length (≤ 128)
    """

    def __init__(self) -> None:
        """Initialize ContextEngineer with cached Flan-T5 model."""
        self.model, self.tokenizer = _get_flan_t5_model_cached()
        self.device = _DEVICE
        self.max_new_tokens = _MAX_NEW_TOKENS

    def _generate(self, prompt: str, max_length: Optional[int] = None) -> str:
        """Generate text using Flan-T5 in a single forward pass (no batching).

        Parameters
        ----------
        prompt : str
            Input prompt for the model
        max_length : int, optional
            Maximum output tokens (default: self.max_new_tokens)

        Returns
        -------
        str
            Generated text (deterministic for inference mode)
        """
        max_length = max_length or self.max_new_tokens

        # Tokenize input
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        ).to(self.device)

        # Generate output (no batching, single forward pass)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_length,
                temperature=1.0,  # Deterministic (greedy decoding)
                do_sample=False,  # No sampling
                num_beams=1,  # No beam search
            )

        # Decode output
        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return result.strip()

    def normalize_query(self, query: str) -> str:
        """Normalize and clarify a user query.

        This function:
        - Expands abbreviations and implicit references
        - Clarifies mathematical or domain-specific terminology
        - Removes redundancy and noise
        - Structures the query for retrieval

        The output is a clarified, explicit version of the query
        suitable for passage retrieval (NOT reasoning).

        Parameters
        ----------
        query : str
            User query string (may be ambiguous or noisy)

        Returns
        -------
        str
            Normalized query (typically < 128 tokens)

        Example
        -------
        >>> engineer = ContextEngineer()
        >>> query = "How do u calculate regression?"
        >>> normalized = engineer.normalize_query(query)
        >>> print(normalized)
        # Output (example): "How do you calculate linear regression analysis?"
        """
        if not query or not query.strip():
            return query

        # Craft a minimal prompt for query normalization
        # Do NOT ask for reasoning, only clarification
        prompt = (
            f"Normalize this query for scientific retrieval. "
            f"Expand abbreviations and clarify terminology. "
            f"Output only the normalized query:\n\n"
            f"Query: {query}"
        )

        normalized = self._generate(prompt, max_length=128)
        logger.debug(f"Normalized query: {query} → {normalized}")
        return normalized

    def compress_context(self, text: str, max_length: Optional[int] = None) -> str:
        """Compress retrieved context while preserving essential information.

        This function:
        - Removes redundancy and noise
        - Preserves definitions, assumptions, and equations
        - Keeps numerical values and citations
        - Avoids paraphrasing or reinterpretation
        - Produces deterministic, concise output

        The output is suitable for passage-level context assembly,
        NOT for reasoning or conclusion-drawing.

        Parameters
        ----------
        text : str
            Retrieved document chunk (typically 500-2000 chars)
        max_length : int, optional
            Maximum output tokens (default: self.max_new_tokens)

        Returns
        -------
        str
            Compressed context (typically 50-128 tokens)

        Example
        -------
        >>> engineer = ContextEngineer()
        >>> doc = "Linear regression is a method... [lots of verbose text]"
        >>> compressed = engineer.compress_context(doc)
        >>> print(compressed)
        # Output (example): "Linear regression: method for modeling linear relationships
        #                    between dependent and independent variables using least
        #                    squares. Key assumptions: linearity, independence, normality."
        """
        if not text or not text.strip():
            return text

        max_length = max_length or self.max_new_tokens

        # Craft a prompt for context compression
        # Do NOT ask for conclusions, only compression
        prompt = (
            f"Compress this scientific passage. "
            f"Keep definitions, equations, and numerical values. "
            f"Remove redundancy. Output only the compressed passage:\n\n"
            f"Passage: {text}"
        )

        compressed = self._generate(prompt, max_length=max_length)
        logger.debug(f"Compressed context: {len(text)} chars → {len(compressed)} chars")
        return compressed

    def compress_context_batch(self, texts: list[str], max_length: Optional[int] = None) -> list[str]:
        """Compress multiple context chunks sequentially (no parallel batching).

        This function processes each chunk independently to avoid
        GPU memory issues and maintain deterministic behavior.

        Parameters
        ----------
        texts : list[str]
            List of retrieved document chunks
        max_length : int, optional
            Maximum output tokens per chunk (default: self.max_new_tokens)

        Returns
        -------
        list[str]
            List of compressed chunks (same order)

        Note
        ----
        This function does NOT use batching; each chunk is processed
        sequentially to maintain strict CPU-only operation and
        deterministic behavior.
        """
        results = []
        for i, text in enumerate(texts):
            try:
                compressed = self.compress_context(text, max_length=max_length)
                results.append(compressed)
            except Exception as e:
                logger.warning(f"Failed to compress chunk {i}: {e}")
                # Fallback to original if compression fails
                results.append(text)

        return results


def get_context_engineer() -> ContextEngineer:
    """Get or create a ContextEngineer instance (singleton pattern via caching).

    The underlying Flan-T5 model is loaded only once and reused across all
    requests. This function provides a thread-safe way to access it.

    Returns
    -------
    ContextEngineer
        Singleton context engineer instance

    Example
    -------
    >>> from app.hf.context_engineering import get_context_engineer
    >>> engineer = get_context_engineer()
    >>> normalized_query = engineer.normalize_query(user_input)
    >>> compressed_docs = engineer.compress_context_batch(retrieved_docs)
    """
    return ContextEngineer()
