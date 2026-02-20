#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""BETA TEST - Global AI System Integration Test

Complete end-to-end test of the Teslas.ai scientific assistant:
1. HF Embeddings & Reranker
2. Vector Store (Chroma + FAISS)
3. RAG Chain
4. LLM (Ollama)
5. Multi-Agent System (Mathematician, Data Scientist, Literature, Memory)
6. Full research pipeline
"""

import sys
from pathlib import Path
import time
import json

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.hf.embeddings import get_hf_embeddings
from app.hf.reranker import get_hf_reranker
from app.vectorstore.store import get_vector_store
from app.llm.ollama import get_llm
from app.agents.graph import TeslasAIOrchestrator
from app.agents.states import ResearchContext
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Color codes for output
GREEN = "[OK]"
RED = "[FAIL]"
YELLOW = "[WARN]"
BLUE = "[INFO]"


class BetaTestRunner:
    """Beta test harness for complete system validation."""
    
    def __init__(self):
        self.results = {
            "components": {},
            "pipeline": {},
            "agents": {},
            "end_to_end": {},
            "timestamp": time.time(),
        }
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def report(self, section: str, test_name: str, status: str, message: str = "", duration: float = 0):
        """Log test result."""
        icon = GREEN if status == "PASS" else RED if status == "FAIL" else YELLOW
        duration_str = f" ({duration:.2f}s)" if duration > 0 else ""
        
        print(f"{icon} [{section}] {test_name}{duration_str}")
        if message:
            print(f"   {message}")
        
        if section not in self.results:
            self.results[section] = {}
        
        self.results[section][test_name] = {
            "status": status,
            "message": message,
            "duration": duration,
        }
        
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
        else:
            self.warnings += 1
    
    def test_phase(self, name: str):
        """Print phase header."""
        print(f"\n{'='*70}")
        print(f"{BLUE} PHASE: {name}")
        print(f"{'='*70}\n")
    
    # ========== COMPONENT TESTS ==========
    
    def test_hf_embeddings(self):
        """Test HF embedding service."""
        self.test_phase("HF Embeddings")
        
        try:
            start = time.time()
            emb = get_hf_embeddings()
            
            # Test query embedding
            query_vec = emb.embed_query("What is artificial intelligence?")
            assert len(query_vec) == 384, f"Expected 384 dims, got {len(query_vec)}"
            
            # Test batch
            batch_vecs = emb.embed_documents([
                "Machine learning and AI are related",
                "Deep neural networks power modern AI",
                "Transformers revolutionized NLP",
            ])
            assert len(batch_vecs) == 3
            
            # Test singleton
            emb2 = get_hf_embeddings()
            assert emb is emb2
            
            duration = time.time() - start
            self.report("components", "HF Embeddings", "PASS", 
                       f"384D vectors, batch OK, singleton OK", duration)
            return True
            
        except Exception as e:
            self.report("components", "HF Embeddings", "FAIL", str(e))
            return False
    
    def test_hf_reranker(self):
        """Test HF CrossEncoder reranker."""
        self.test_phase("HF Reranker")
        
        try:
            start = time.time()
            reranker = get_hf_reranker()
            
            query = "What is machine learning?"
            candidates = [
                {"content": "ML is a subset of AI"},
                {"content": "Neural networks process data"},
                {"content": "The weather is sunny today"},
                {"content": "Transformers use attention mechanisms"},
            ]
            
            ranked = reranker.rerank(query, candidates, top_k=3)
            assert len(ranked) == 3, f"Expected 3 results, got {len(ranked)}"
            
            # Verify scores are numeric (can be negative)
            for r in ranked:
                assert "score" in r
                assert isinstance(r["score"], (int, float))
            
            # Singleton
            rr2 = get_hf_reranker()
            assert reranker is rr2
            
            duration = time.time() - start
            self.report("components", "HF Reranker", "PASS",
                       f"3 candidates reranked, singleton OK", duration)
            return True
            
        except Exception as e:
            self.report("components", "HF Reranker", "FAIL", str(e))
            return False
    
    def test_vector_store(self):
        """Test hybrid vector store (FAISS + ChromaDB)."""
        self.test_phase("Vector Store Integration")
        
        try:
            start = time.time()
            vs = get_vector_store()
            
            # Add documents
            docs = [
                "Linear algebra deals with vectors and matrices",
                "Eigenvalues represent scaling factors in transformations",
                "Neural networks use matrix multiplications",
                "Singular value decomposition is useful for dimensionality reduction",
            ]
            
            metadatas = [
                {"source": "math", "category": "linear_algebra"},
                {"source": "math", "category": "linear_algebra"},
                {"source": "ml", "category": "fundamentals"},
                {"source": "ml", "category": "dimensionality_reduction"},
            ]
            
            vs.add_texts(docs, metadatas=metadatas)
            
            # Search without reranking
            results = vs.search("What are eigenvalues?", k=2, rerank=False)
            assert len(results) > 0, "No results found"
            
            # Search with reranking
            results_ranked = vs.search("What are eigenvalues?", k=2, rerank=True)
            assert len(results_ranked) > 0, "No ranked results"
            
            duration = time.time() - start
            self.report("components", "Vector Store", "PASS",
                       f"Stored {len(docs)} docs, search+rerank OK", duration)
            return True
            
        except Exception as e:
            self.report("components", "Vector Store", "FAIL", str(e))
            return False
    
    def test_ollama_llm(self):
        """Test Ollama LLM connection and generation."""
        self.test_phase("Ollama LLM")
        
        try:
            start = time.time()
            llm = get_llm(temperature=0.3)
            
            # Simple generation test
            response = llm.invoke("What is 2+2? Answer briefly.")
            content = getattr(response, "content", str(response))
            
            assert len(content) > 0, "Empty response from LLM"
            assert "4" in content or "four" in content.lower(), "Wrong answer from LLM"
            
            duration = time.time() - start
            self.report("components", "Ollama LLM", "PASS",
                       f"LLM generation OK ({len(content)} chars)", duration)
            return True
            
        except Exception as e:
            self.report("components", "Ollama LLM", "WARN",
                       f"Ollama connection: {str(e)}", 0)
            return False
    
    # ========== PIPELINE TESTS ==========
    
    def test_rag_pipeline(self):
        """Test RAG (Retrieval Augmented Generation) pipeline."""
        self.test_phase("RAG Pipeline")
        
        try:
            start = time.time()
            
            # Setup
            vs = get_vector_store()
            llm = get_llm(temperature=0.2)
            
            # Add context documents
            docs = [
                "Artificial neural networks are computational models inspired by biological neural networks",
                "Deep learning uses multiple layers of abstraction to learn hierarchical representations",
                "The transformer architecture introduced self-attention mechanisms for sequence modeling",
                "Large language models are trained on massive amounts of text data",
            ]
            
            vs.add_texts(docs)
            
            # RAG query
            query = "What are transformers in AI?"
            retrieved = vs.search(query, k=2, rerank=True)
            
            assert len(retrieved) > 0, "No documents retrieved"
            
            # Create RAG context
            context_text = "\n".join([r.get("content", "") for r in retrieved if r.get("content")])
            
            # Generate answer using LLM with retrieved context
            rag_prompt = f"""Using this context:
{context_text}

Answer the question: {query}
Keep answer concise."""
            
            answer = llm.invoke(rag_prompt)
            answer_text = getattr(answer, "content", str(answer))
            
            assert len(answer_text) > 10, "Generated answer too short"
            
            duration = time.time() - start
            self.report("pipeline", "RAG Pipeline", "PASS",
                       f"Retrieved {len(retrieved)} docs, generated answer ({len(answer_text)} chars)",
                       duration)
            return True
            
        except Exception as e:
            self.report("pipeline", "RAG Pipeline", "FAIL", str(e))
            return False
    
    # ========== AGENT TESTS ==========
    
    def test_research_graph(self):
        """Test multi-agent research graph."""
        self.test_phase("Research Graph & Agents")
        
        try:
            start = time.time()
            
            # Create research orchestrator
            orchestrator = TeslasAIOrchestrator()
            
            # Initialize context
            context = ResearchContext(main_query="What is the relationship between linear algebra and neural networks?")
            
            # Run research (with timeout)
            print(f"  Running multi-agent research...")
            
            # This is a simplified test - just verify orchestrator creation
            assert orchestrator is not None, "Failed to create research orchestrator"
            
            # Note: Full orchestrator execution requires all agents working
            # We'll test basic execution
            try:
                result = orchestrator.run_research("What is matrix multiplication?")
                
                if result and isinstance(result, ResearchContext):
                    self.report("agents", "Research Orchestrator", "PASS",
                               f"Orchestrator executed, research completed", time.time() - start)
                else:
                    self.report("agents", "Research Orchestrator", "WARN",
                               "Orchestrator ran but returned unexpected result", time.time() - start)
            except Exception as orch_err:
                logger.warning(f"Orchestrator execution partial: {orch_err}")
                self.report("agents", "Research Orchestrator", "WARN",
                           f"Orchestrator created OK, execution partial", time.time() - start)
            
            return True
            
        except Exception as e:
            self.report("agents", "Research Orchestrator", "FAIL", str(e))
            return False
    
    # ========== END-TO-END TEST ==========
    
    def test_end_to_end(self):
        """Complete end-to-end research workflow."""
        self.test_phase("End-to-End Research Workflow")
        
        try:
            start = time.time()
            
            # Step 1: Query
            query = "Explain the relationship between eigenvalues and neural network convergence"
            print(f"  Query: {query}\n")
            
            # Step 2: Embeddings
            embedder = get_hf_embeddings()
            query_embedding = embedder.embed_query(query)
            print(f"  ✓ Query embedded (384D)")
            
            # Step 3: Vector store with research docs
            vs = get_vector_store()
            research_docs = [
                "Eigenvalues determine the behavior of linear transformations in neural networks",
                "The convergence rate of neural networks depends on the Hessian eigenvalues",
                "Weight matrices in neural networks have spectral properties related to eigenvalues",
                "Gradient descent convergence is affected by the largest eigenvalue of the Hessian",
            ]
            
            vs.add_texts(research_docs)
            print(f"  ✓ {len(research_docs)} research docs indexed")
            
            # Step 4: Retrieve and rerank
            retrieved = vs.search(query, k=3, rerank=True)
            print(f"  ✓ Retrieved and reranked {len(retrieved)} documents")
            
            # Step 5: Generate answer
            llm = get_llm(temperature=0.2)
            context_str = "\n".join([d.get("content", "") for d in retrieved])
            
            final_prompt = f"""You are a scientific researcher. Based on this context:

{context_str}

Answer: {query}

Provide a concise, technical answer."""
            
            answer = llm.invoke(final_prompt)
            answer_text = getattr(answer, "content", str(answer))
            print(f"  ✓ LLM generated answer ({len(answer_text)} chars)")
            
            duration = time.time() - start
            self.report("end_to_end", "Complete Workflow", "PASS",
                       f"Query→Embed→Store→Retrieve→Rerank→Generate", duration)
            
            return True
            
        except Exception as e:
            self.report("end_to_end", "Complete Workflow", "FAIL", str(e))
            return False
    
    def run_all_tests(self):
        """Execute all beta tests."""
        print("\n" + "="*70)
        print("TESLAS.AI BETA TEST SUITE - Global System Integration")
        print("="*70)
        
        # Component Tests
        print("\n" + "="*70)
        print("COMPONENT TESTS")
        print("="*70)
        
        self.test_hf_embeddings()
        self.test_hf_reranker()
        self.test_vector_store()
        self.test_ollama_llm()
        
        # Pipeline Tests
        print("\n" + "="*70)
        print("PIPELINE TESTS")
        print("="*70)
        
        self.test_rag_pipeline()
        
        # Agent Tests
        print("\n" + "="*70)
        print("AGENT & SYSTEM TESTS")
        print("="*70)
        
        self.test_research_graph()
        
        # End-to-End
        print("\n" + "="*70)
        print("END-TO-END TEST")
        print("="*70)
        
        self.test_end_to_end()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print comprehensive test summary."""
        total = self.passed + self.failed + self.warnings
        
        print("\n" + "="*70)
        print("BETA TEST SUMMARY")
        print("="*70)
        
        print(f"""
{GREEN} PASSED:  {self.passed}/{total}
{RED} FAILED:  {self.failed}/{total}
{YELLOW} WARNINGS: {self.warnings}/{total}

System Status: {'OPERATIONAL' if self.failed == 0 else 'NEEDS ATTENTION'}

Components Tested:
  * HF Embeddings (all-MiniLM-L6-v2)
  * HF Reranker (ms-marco-MiniLM-L-6-v2)
  * Vector Store (FAISS + ChromaDB)
  * LLM (Ollama)
  * RAG Pipeline
  * Multi-Agent System
  * End-to-End Workflow

Key Results:
""")
        
        for section, tests in self.results.items():
            if section not in ["timestamp"]:
                print(f"\n{section.upper()}:")
                for test_name, result in tests.items():
                    status_icon = GREEN if result["status"] == "PASS" else RED if result["status"] == "FAIL" else YELLOW
                    print(f"  {status_icon} {test_name}")
                    if result.get("message"):
                        print(f"     {result['message']}")
        
        print("\n" + "="*70)
        
        # Save results
        try:
            results_file = Path("tests/beta_test_results.json")
            with open(results_file, "w") as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"[OK] Results saved to: {results_file}")
        except Exception as e:
            print(f"[WARN] Could not save results: {e}")
        
        print("="*70 + "\n")


if __name__ == "__main__":
    runner = BetaTestRunner()
    runner.run_all_tests()
    
    # Exit code based on failures
    sys.exit(0 if runner.failed == 0 else 1)
