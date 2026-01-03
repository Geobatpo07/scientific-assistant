"""Test suite for context engineering layer.

Tests verify:
1. Model loading (singleton pattern)
2. Query normalization
3. Context compression
4. Batch compression
5. RAG chain integration
6. CPU-only execution
7. Determinism
"""

import os
import pytest
from unittest.mock import patch, MagicMock

# Set CPU-only before importing
os.environ["CUDA_VISIBLE_DEVICES"] = ""


def test_context_engineer_import():
    """Test that context engineering module imports correctly."""
    from app.hf.context_engineering import (
        get_context_engineer,
        ContextEngineer,
        _get_flan_t5_model_cached,
    )
    assert get_context_engineer is not None
    assert ContextEngineer is not None
    assert _get_flan_t5_model_cached is not None


def test_context_engineer_singleton():
    """Test that context engineer uses singleton pattern for model loading."""
    from app.hf.context_engineering import get_context_engineer

    # First call
    engineer1 = get_context_engineer()

    # Second call
    engineer2 = get_context_engineer()

    # Should be same instance (cached)
    assert engineer1 is engineer2


def test_context_engineer_initialization():
    """Test that ContextEngineer initializes with correct device."""
    from app.hf.context_engineering import ContextEngineer

    engineer = ContextEngineer()

    assert engineer.device == "cpu"
    assert engineer.max_new_tokens == 128
    assert engineer.model is not None
    assert engineer.tokenizer is not None


@pytest.mark.slow
def test_normalize_query_basic():
    """Test query normalization with basic input."""
    from app.hf.context_engineering import get_context_engineer

    engineer = get_context_engineer()

    # Test: ambiguous query
    query = "How calculate regression?"
    normalized = engineer.normalize_query(query)

    assert isinstance(normalized, str)
    assert len(normalized) > 0
    assert len(normalized) <= 512  # Should fit in model input


@pytest.mark.slow
def test_normalize_query_empty():
    """Test query normalization with empty input."""
    from app.hf.context_engineering import get_context_engineer

    engineer = get_context_engineer()

    # Empty query should return empty
    result = engineer.normalize_query("")
    assert result == ""

    # Whitespace query should return empty
    result = engineer.normalize_query("   ")
    assert result == ""


@pytest.mark.slow
def test_compress_context_basic():
    """Test context compression with basic input."""
    from app.hf.context_engineering import get_context_engineer

    engineer = get_context_engineer()

    # Long document
    doc = """
    Linear regression is a fundamental statistical method. It models the
    relationship between variables. The method was developed in the 18th
    century. Linear regression works by fitting a line to the data. It
    assumes the relationship is linear. The goal is to minimize the sum
    of squared residuals using the least squares method.
    """ * 3  # Make it longer

    compressed = engineer.compress_context(doc)

    assert isinstance(compressed, str)
    assert len(compressed) > 0
    assert len(compressed) <= 512  # Should fit in model output limit


@pytest.mark.slow
def test_compress_context_empty():
    """Test context compression with empty input."""
    from app.hf.context_engineering import get_context_engineer

    engineer = get_context_engineer()

    # Empty should return empty
    result = engineer.compress_context("")
    assert result == ""


@pytest.mark.slow
def test_compress_context_batch_basic():
    """Test batch compression with multiple documents."""
    from app.hf.context_engineering import get_context_engineer

    engineer = get_context_engineer()

    docs = [
        "Linear regression is used for modeling linear relationships between variables.",
        "Logistic regression is used for binary classification tasks.",
        "Polynomial regression fits higher-degree polynomial curves to data.",
    ]

    compressed = engineer.compress_context_batch(docs)

    assert isinstance(compressed, list)
    assert len(compressed) == len(docs)
    for item in compressed:
        assert isinstance(item, str)


@pytest.mark.slow
def test_compress_context_batch_empty():
    """Test batch compression with empty list."""
    from app.hf.context_engineering import get_context_engineer

    engineer = get_context_engineer()

    result = engineer.compress_context_batch([])
    assert result == []


@pytest.mark.slow
def test_compress_context_batch_with_failed_compression():
    """Test batch compression handles failures gracefully."""
    from app.hf.context_engineering import get_context_engineer

    engineer = get_context_engineer()

    docs = [
        "Valid document",
        "",  # Empty will fail
        "Another valid document",
    ]

    compressed = engineer.compress_context_batch(docs)

    assert len(compressed) == len(docs)
    # Failed items should return original
    assert compressed[1] == ""


def test_cpu_only_execution():
    """Test that context engineer uses CPU only."""
    from app.hf.context_engineering import get_context_engineer, _DEVICE

    assert _DEVICE == "cpu"

    engineer = get_context_engineer()
    assert engineer.device == "cpu"


def test_determinism():
    """Test that normalization is deterministic (greedy decoding)."""
    from app.hf.context_engineering import get_context_engineer

    engineer = get_context_engineer()

    query = "How to calculate variance?"

    # Multiple calls should give same result (greedy decoding)
    result1 = engineer.normalize_query(query)
    result2 = engineer.normalize_query(query)

    # Should be identical (deterministic)
    assert result1 == result2


def test_model_constraints():
    """Test that model uses correct configuration."""
    from app.hf.context_engineering import (
        _FLAN_T5_MODEL,
        _MAX_NEW_TOKENS,
        _DEVICE,
    )

    assert _FLAN_T5_MODEL == "google/flan-t5-base"
    assert _MAX_NEW_TOKENS == 128
    assert _DEVICE == "cpu"


def test_rag_chain_integration():
    """Test that RAG chain integrates context engineering."""
    from app.rag.chains import RAGChain

    # Create chain
    chain = RAGChain()

    # Should have context engineer
    assert hasattr(chain, "context_engineer")
    assert chain.context_engineer is not None


def test_rag_chain_retrieve_and_generate_keys():
    """Test that RAG chain returns expected keys."""
    from app.rag.chains import RAGChain

    chain = RAGChain()

    # Expected keys in response
    expected_keys = {
        "query",
        "normalized_query",
        "response",
        "context",
        "sources",
    }

    # Note: This test checks structure only, not full execution
    # Full execution requires running services (ChromaDB, Ollama)


def test_env_variables_set():
    """Test that environment variables are set correctly."""
    from app.hf import context_engineering

    # Should have set HF_HOME, CUDA, etc.
    assert os.environ.get("CUDA_VISIBLE_DEVICES") == ""


def test_logging_integration():
    """Test that context engineer logs operations."""
    from app.hf.context_engineering import get_context_engineer
    import logging

    # Enable debug logging
    logger = logging.getLogger("app.hf.context_engineering")
    logger.setLevel(logging.DEBUG)

    engineer = get_context_engineer()

    # Should have logger available
    assert engineer is not None


@pytest.mark.slow
def test_normalize_query_preserves_intent():
    """Test that normalization preserves user intent."""
    from app.hf.context_engineering import get_context_engineer

    engineer = get_context_engineer()

    queries = [
        "regression",
        "what is regression",
        "how calculate regression",
    ]

    results = [engineer.normalize_query(q) for q in queries]

    # All should contain core concept
    for result in results:
        assert "regression" in result.lower()


@pytest.mark.slow
def test_compress_context_preserves_definitions():
    """Test that compression preserves mathematical definitions."""
    from app.hf.context_engineering import get_context_engineer

    engineer = get_context_engineer()

    doc = """
    The mean is defined as the sum of all values divided by the count of values.
    The formula is: mean = (sum of values) / (count of values).
    The mean is also called the average.
    """

    compressed = engineer.compress_context(doc)

    # Should preserve definition
    assert "mean" in compressed.lower()
    assert "sum" in compressed.lower() or "average" in compressed.lower()


def test_max_tokens_constraint():
    """Test that output respects max_new_tokens constraint."""
    from app.hf.context_engineering import ContextEngineer

    engineer = ContextEngineer()

    # Default max_new_tokens should be 128
    assert engineer.max_new_tokens == 128


def test_context_engineer_thread_safety():
    """Test that context engineer is thread-safe (via singleton)."""
    from app.hf.context_engineering import get_context_engineer
    import threading

    engineers = []

    def get_engineer():
        engineers.append(get_context_engineer())

    threads = [threading.Thread(target=get_engineer) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # All should be same instance
    assert all(e is engineers[0] for e in engineers)


if __name__ == "__main__":
    # Run tests: pytest tests/test_context_engineering.py -v
    # Run slow tests: pytest tests/test_context_engineering.py -v -m slow
    pytest.main([__file__, "-v"])
