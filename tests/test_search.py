"""Tests for search functionality."""

import pytest

from app.tools.duckduckgo_search import DuckDuckGoSearcher


@pytest.fixture
def searcher():
    """Create search instance."""
    return DuckDuckGoSearcher()


def test_search_scientific(searcher):
    """Test scientific search."""
    results = searcher.search_scientific("machine learning", safe_search="moderate")
    
    # May return 0 results if no internet, but should not raise
    assert isinstance(results, list)


def test_search_types(searcher):
    """Test different search types."""
    # These may fail without internet, but we test the interface
    assert isinstance(searcher.search_arxiv("optimization"), list)
    assert isinstance(searcher.search_scholar("statistics"), list)
    assert isinstance(searcher.search_code("python neural network"), list)
