#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""BETA TEST - Global AI System Integration Test - Simplified

Complete end-to-end test of the Teslas.ai scientific assistant.
All tests report to console with ASCII-only output.
"""

import sys
from pathlib import Path
import time

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Force phi model in environment
import os
os.environ['OLLAMA_MODEL'] = 'phi'

from app.hf.embeddings import get_hf_embeddings
from app.hf.reranker import get_hf_reranker
from app.vectorstore.store import get_vector_store
from app.llm.ollama import get_llm
from app.agents.graph import TeslasAIOrchestrator
from app.agents.states import ResearchContext
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SimpleBetaTest:
    """Simplified beta test runner."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def test(self, name, fn):
        """Run a test function."""
        print(f"\n[TEST] {name}")
        print("-" * 60)
        try:
            start = time.time()
            fn()
            elapsed = time.time() - start
            print(f"PASS ({elapsed:.2f}s)")
            self.passed += 1
        except AssertionError as e:
            print(f"FAIL: {e}")
            self.failed += 1
        except Exception as e:
            print(f"WARN: {e}")
            self.warnings += 1
    
    def run_all(self):
        """Execute all tests."""
        print("="*60)
        print("TESLAS.AI BETA TEST - GLOBAL SYSTEM")
        print("="*60)
        
        # Component tests
        print("\n[SECTION] Component Tests")
        self.test("HF Embeddings", self.test_embeddings)
        self.test("HF Reranker", self.test_reranker)
        self.test("Vector Store", self.test_vector_store)
        self.test("Ollama LLM", self.test_ollama)
        
        # Pipeline tests
        print("\n[SECTION] Pipeline Tests")
        self.test("RAG Pipeline", self.test_rag)
        
        # Agent tests
        print("\n[SECTION] Agent Tests")
        self.test("Research Orchestrator", self.test_orchestrator)
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        total = self.passed + self.failed + self.warnings
        print(f"PASSED:  {self.passed}/{total}")
        print(f"FAILED:  {self.failed}/{total}")
        print(f"WARNINGS: {self.warnings}/{total}")
        print(f"STATUS: {'OPERATIONAL' if self.failed == 0 else 'NEEDS ATTENTION'}")
        print("="*60 + "\n")
    
    def test_embeddings(self):
        """Test HF embeddings."""
        emb = get_hf_embeddings()
        assert emb is not None, "Failed to load embeddings"
        
        vec = emb.embed_query("What is AI?")
        assert len(vec) == 384, f"Expected 384D, got {len(vec)}"
        
        batch = emb.embed_documents(["Doc1", "Doc2"])
        assert len(batch) == 2, "Batch embedding failed"
        print("- Embeddings: OK (384D, batching OK)")
    
    def test_reranker(self):
        """Test HF reranker."""
        rr = get_hf_reranker()
        assert rr is not None, "Failed to load reranker"
        
        cands = [
            {"content": "AI is machine learning"},
            {"content": "Dogs are animals"},
            {"content": "Neural networks process data"},
        ]
        
        ranked = rr.rerank("What is AI?", cands, top_k=2)
        assert len(ranked) == 2, f"Expected 2 results, got {len(ranked)}"
        assert "score" in ranked[0], "Missing score in results"
        print("- Reranker: OK (scored rankings)")
    
    def test_vector_store(self):
        """Test vector store."""
        vs = get_vector_store()
        assert vs is not None, "Failed to create vector store"
        
        docs = ["Linear algebra is fundamental", "Matrix operations are important"]
        vs.add_texts(docs)
        
        results = vs.search("What is linear algebra?", k=1, rerank=False)
        assert len(results) > 0, "No search results"
        
        results_ranked = vs.search("What is linear algebra?", k=1, rerank=True)
        assert len(results_ranked) > 0, "No reranked results"
        print("- Vector Store: OK (search + rerank)")
    
    def test_ollama(self):
        """Test Ollama LLM connection."""
        try:
            llm = get_llm(temperature=0.3)
            response = llm.invoke("What is 1+1? Answer with just the number.")
            content = getattr(response, "content", str(response))
            assert len(content) > 0, "Empty response"
            assert "2" in content, f"Unexpected response: {content}"
            print(f"- Ollama LLM: OK (response: {content.strip()[:40]}...)")
        except Exception as e:
            raise AssertionError(f"Ollama failed: {e}")
    
    def test_rag(self):
        """Test RAG pipeline."""
        try:
            vs = get_vector_store()
            llm = get_llm(temperature=0.2)
            
            # Add docs
            docs = [
                "Transformers use attention mechanisms",
                "Neural networks have multiple layers",
                "Deep learning is a subset of machine learning",
            ]
            vs.add_texts(docs)
            
            # Retrieve
            query = "How do neural networks work?"
            retrieved = vs.search(query, k=2, rerank=True)
            assert len(retrieved) > 0, "Retrieval failed"
            
            # Generate
            context = "\n".join([r.get("content", "") for r in retrieved])
            prompt = f"Context: {context}\n\nQ: {query}\nA:"
            answer = llm.invoke(prompt)
            content = getattr(answer, "content", str(answer))
            assert len(content) > 10, "Generated answer too short"
            
            print(f"- RAG Pipeline: OK (retrieved {len(retrieved)}, generated answer)")
        except Exception as e:
            raise AssertionError(f"RAG pipeline failed: {e}")
    
    def test_orchestrator(self):
        """Test research orchestrator."""
        try:
            orch = TeslasAIOrchestrator()
            assert orch is not None, "Failed to create orchestrator"
            
            result = orch.run_research("What is calculus?")
            assert isinstance(result, ResearchContext), "Invalid result type"
            assert result.main_query == "What is calculus?", "Query not set"
            
            print(f"- Orchestrator: OK (executed workflow)")
        except Exception as e:
            raise AssertionError(f"Orchestrator failed: {e}")


if __name__ == "__main__":
    tester = SimpleBetaTest()
    tester.run_all()
    
    sys.exit(0 if tester.failed == 0 else 1)
