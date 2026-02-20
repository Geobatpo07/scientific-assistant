"""Tests for RAG functionality."""

import pytest

from app.vectorstore.chroma import ChromaVectorStore
from app.rag.chains import RAGChain


@pytest.fixture
def vector_store():
    """Create test vector store."""
    store = ChromaVectorStore(collection_name="test_collection")
    return store


def test_vector_store_add_texts(vector_store):
    """Test adding texts to vector store."""
    texts = ["Test document 1", "Test document 2"]
    ids = vector_store.add_texts(texts)
    
    assert len(ids) == 2
    assert vector_store.count() >= 2


def test_vector_store_search(vector_store):
    """Test searching vector store."""
    texts = ["Machine learning is important", "Python is a programming language"]
    vector_store.add_texts(texts)
    
    results = vector_store.search("machine learning", k=1)
    
    assert len(results) > 0
    assert "learning" in results[0]["content"].lower()


def test_rag_chain():
    """Test RAG chain."""
    rag = RAGChain()
    
    # Add some documents
    docs = ["Calculus is the study of change", "Derivatives measure rates of change"]
    rag.vector_store.add_texts(docs)
    
    # Query
    result = rag.retrieve_and_generate("What is calculus?", k=1)
    
    assert "query" in result
    assert "response" in result
    assert len(result["sources"]) > 0
