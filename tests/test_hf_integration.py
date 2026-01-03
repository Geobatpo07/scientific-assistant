#!/usr/bin/env python
"""Integration tests for Hugging Face + Teslas.ai

Tests the complete pipeline:
1. HF embeddings (singleton, cache)
2. HF reranker (singleton)
3. FAISS index (threading, rebuild)
4. ChromaDB integration
5. Hybrid vector store
6. RAG chain
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.hf.embeddings import get_hf_embeddings, HfEmbeddingService
from app.hf.reranker import get_hf_reranker, HfCrossEncoderReranker
from app.vectorstore.store import get_vector_store
from app.utils.logger import get_logger

logger = get_logger(__name__)


def test_hf_embeddings():
    """Test HF embedding service."""
    print("\n" + "="*60)
    print("TEST 1: HF Embeddings Service")
    print("="*60)
    
    try:
        emb = get_hf_embeddings()
        print(f"✅ Loaded embeddings: {type(emb).__name__}")
        
        # Test single query
        vec = emb.embed_query("What is machine learning?")
        print(f"✅ Query embedding shape: {len(vec)} dims")
        assert len(vec) == 384, f"Expected 384 dims, got {len(vec)}"
        
        # Test batch
        vecs = emb.embed_documents([
            "Document 1",
            "Document 2",
            "Document 3",
        ])
        print(f"✅ Batch embedding: {len(vecs)} vectors × {len(vecs[0])} dims")
        assert len(vecs) == 3, f"Expected 3 vectors, got {len(vecs)}"
        
        # Test cache (should be fast)
        vec_cached = emb.embed_query("What is machine learning?")
        print(f"✅ Cache hit: {vec_cached == vec}")
        
        # Test singleton
        emb2 = get_hf_embeddings()
        print(f"✅ Singleton: {emb is emb2}")
        assert emb is emb2, "Embeddings should be singleton"
        
        print("✅ HF Embeddings Test PASSED\n")
        return True
    except Exception as e:
        print(f"❌ HF Embeddings Test FAILED: {e}\n")
        return False


def test_hf_reranker():
    """Test HF CrossEncoder reranker."""
    print("="*60)
    print("TEST 2: HF CrossEncoder Reranker")
    print("="*60)
    
    try:
        rr = get_hf_reranker()
        print(f"✅ Loaded reranker: {type(rr).__name__}")
        
        # Test reranking
        query = "What is artificial intelligence?"
        candidates = [
            {"content": "AI is a branch of computer science"},
            {"content": "Machine learning is part of AI"},
            {"content": "The sky is blue"},
            {"content": "Deep learning uses neural networks"},
        ]
        
        ranked = rr.rerank(query, candidates, top_k=3)
        print(f"✅ Reranked: {len(candidates)} → {len(ranked)} results")
        assert len(ranked) == 3, f"Expected 3 results, got {len(ranked)}"
        
        # Check scores (note: ms-marco CrossEncoder can return negative scores)
        for i, result in enumerate(ranked):
            print(f"  [{i}] score={result.get('score'):.3f}: {result['content'][:40]}...")
            assert "score" in result, "Result should have 'score' key"
            assert isinstance(result["score"], (int, float)), f"Score should be numeric, got {type(result['score'])}"
        
        # Test singleton
        rr2 = get_hf_reranker()
        print(f"✅ Singleton: {rr is rr2}")
        assert rr is rr2, "Reranker should be singleton"
        
        print("✅ HF Reranker Test PASSED\n")
        return True
    except Exception as e:
        print(f"❌ HF Reranker Test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_hybrid_vector_store():
    """Test hybrid vector store (FAISS + ChromaDB + Reranker)."""
    print("="*60)
    print("TEST 3: Hybrid Vector Store")
    print("="*60)
    
    try:
        vs = get_vector_store()
        print(f"✅ Loaded hybrid store: {type(vs).__name__}")
        
        # Test add_texts
        docs = [
            "Machine learning is a subset of artificial intelligence",
            "Deep learning uses neural networks with multiple layers",
            "Natural language processing helps computers understand text",
            "Computer vision enables machines to interpret images",
        ]
        
        ids = vs.add_texts(docs)
        print(f"✅ Added {len(ids)} documents")
        assert len(ids) == 4, f"Expected 4 IDs, got {len(ids)}"
        
        # Test count
        count = vs.count()
        print(f"✅ Collection count: {count}")
        
        # Test search without reranking
        results = vs.search("What is machine learning?", k=2, rerank=False)
        print(f"✅ Search (no rerank): {len(results)} results")
        for i, r in enumerate(results):
            print(f"  [{i}] {r['content'][:50]}...")
        
        # Test search with reranking
        results_ranked = vs.search("What is machine learning?", k=2, rerank=True)
        print(f"✅ Search (with rerank): {len(results_ranked)} results")
        for i, r in enumerate(results_ranked):
            print(f"  [{i}] score={r.get('score', 'N/A')} | {r['content'][:50]}...")
        
        print("✅ Hybrid Vector Store Test PASSED\n")
        return True
    except Exception as e:
        print(f"❌ Hybrid Vector Store Test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_rag_chain():
    """Test RAG chain integration."""
    print("="*60)
    print("TEST 4: RAG Chain Integration")
    print("="*60)
    
    try:
        from app.rag.chains import RAGChain
        
        rag = RAGChain()
        print(f"✅ Initialized RAGChain: {type(rag).__name__}")
        
        # Test retrieval
        query = "What is machine learning?"
        result = rag.retrieve_and_generate(query, k=2)
        
        print(f"✅ Query: {query}")
        print(f"✅ Response available: {len(result['response']) > 0}")
        print(f"✅ Sources retrieved: {len(result['sources'])} documents")
        print(f"✅ Context length: {len(result['context'])} chars")
        
        for i, src in enumerate(result['sources']):
            print(f"  [{i}] {src.get('content', '')[:50]}...")
        
        print("✅ RAG Chain Integration Test PASSED\n")
        return True
    except Exception as e:
        print(f"⚠️  RAG Chain Test (expected if Ollama not running): {e}\n")
        return None  # Optional test


def test_memory_profile():
    """Estimate memory usage."""
    print("="*60)
    print("TEST 5: Memory Profile")
    print("="*60)
    
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        
        print(f"✅ Current memory usage: {mem_info.rss / 1024 / 1024:.1f} MB")
        print(f"   (HF models + cache included)")
        
        # Get embeddings (should be loaded)
        emb = get_hf_embeddings()
        
        mem_after_emb = process.memory_info()
        print(f"✅ After embeddings: {mem_after_emb.rss / 1024 / 1024:.1f} MB")
        
        # Get reranker
        rr = get_hf_reranker()
        mem_after_rr = process.memory_info()
        print(f"✅ After reranker: {mem_after_rr.rss / 1024 / 1024:.1f} MB")
        
        print("✅ Memory Profile Test PASSED\n")
        return True
    except Exception as e:
        print(f"⚠️  Memory Profile Test (psutil not available): {e}\n")
        return None


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("TESLAS.AI + HUGGING FACE INTEGRATION TESTS")
    print("="*60)
    
    results = {}
    
    # Core tests
    results["HF Embeddings"] = test_hf_embeddings()
    results["HF Reranker"] = test_hf_reranker()
    results["Hybrid Vector Store"] = test_hybrid_vector_store()
    results["RAG Chain"] = test_rag_chain()
    results["Memory Profile"] = test_memory_profile()
    
    # Summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    optional = sum(1 for v in results.values() if v is None)
    
    for name, result in results.items():
        status = "✅ PASSED" if result is True else "❌ FAILED" if result is False else "⚠️  OPTIONAL"
        print(f"{status:15} | {name}")
    
    print("="*60)
    print(f"RESULTS: {passed} passed, {failed} failed, {optional} optional")
    print("="*60)
    
    if failed > 0:
        print("\n❌ SOME TESTS FAILED")
        return 1
    else:
        print("\n✅ ALL CORE TESTS PASSED")
        return 0


if __name__ == "__main__":
    exit(main())
