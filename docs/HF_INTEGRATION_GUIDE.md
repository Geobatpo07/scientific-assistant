"""
HUGGING FACE INTEGRATION FOR TESLAS.AI
=====================================

Production-Ready, CPU-Optimized Scientific AI System

OBJECTIVE
---------
Integrate Hugging Face models for:
- High-quality embeddings (semantic search)
- Scientific reranking (relevance scoring)

WITHOUT:
- Replacing Ollama (main LLM reasoning engine)
- Excessive RAM/CPU consumption
- Duplicating existing functionality

=====================================
ARCHITECTURE OVERVIEW
=====================================

PIPELINE:
  User Query
    ↓
  HF Embedding (sentence-transformers/all-MiniLM-L6-v2)
    ↓
  FAISS Index (Top 30 candidates - speed)
    ↓
  ChromaDB (Metadata retrieval + persistence)
    ↓
  HF Reranker (cross-encoder/ms-marco-MiniLM-L-6-v2)
    ↓
  Top-5 Results
    ↓
  Ollama (Reasoning & synthesis)

COMPONENTS:

1. HF Embeddings (app/hf/embeddings.py)
   - Model: sentence-transformers/all-MiniLM-L6-v2
   - Device: CPU only (explicit `device="cpu"`)
   - Singleton: Loaded once, reused across all requests
   - Cache: De-duplication cache to avoid re-encoding
   - Batch Size: Capped at 32 for RAM efficiency
   - LangChain Compatible: Implements Embeddings interface

2. HF Reranker (app/hf/reranker.py)
   - Model: cross-encoder/ms-marco-MiniLM-L-6-v2
   - Device: CPU only
   - Singleton: Loaded once
   - Batch Size: Capped at 32
   - Input: Query + list of candidates with content/metadata
   - Output: Scored and sorted results by relevance

3. FAISS Index (app/vectorstore/faiss_index.py)
   - Stores: Embeddings + IDs only (lightweight)
   - NOT: Documents or metadata (ChromaDB handles this)
   - Thread Limit: 2 threads (CPU efficiency)
   - Rebuild: Can be rebuilt from ChromaDB exports
   - Dimension: Inferred from HF embeddings (384 for all-MiniLM-L6-v2)

4. ChromaDB Vector Store (app/vectorstore/chroma.py)
   - Stores: Documents + embeddings + metadata
   - Embeddings: Use HF embeddings (CPU-only)
   - Persistence: /data/chroma/scientific_db
   - Fallback: Pure semantic search if FAISS unavailable

5. Hybrid Vector Store (app/vectorstore/hybrid_store.py)
   - Orchestrates: FAISS + ChromaDB + HF Reranker
   - Lazy Init: FAISS rebuilt from ChromaDB on startup
   - Search: Query → FAISS candidates → ChromaDB metadata → HF Reranker

6. Retriever (app/vectorstore/retriever.py)
   - Interface: Compatible with RAG chains
   - Reranking: Always enabled for scientific queries

7. RAG Chain (app/rag/chains.py)
   - Uses: get_vector_store() → HybridVectorStore
   - Input: Query
   - Output: Retrieved context + Ollama synthesis

=====================================
MODELS (CPU-FRIENDLY)
=====================================

EMBEDDINGS MODEL:
  Name: sentence-transformers/all-MiniLM-L6-v2
  Size: ~22 MB
  Dimension: 384
  Speed: ~1000 sentences/sec on CPU
  Quality: Excellent for scientific domain (trained on MNLI)
  RAM: ~40 MB (model) + ~128 MB (batch of 32)
  URL: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

RERANKER MODEL:
  Name: cross-encoder/ms-marco-MiniLM-L-6-v2
  Size: ~28 MB
  Quality: Specialized for query-document ranking
  Speed: ~500 query-doc pairs/sec on CPU
  RAM: ~50 MB (model) + ~64 MB (batch of 32)
  URL: https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2

TOTAL MEMORY (Conservative):
  HF Embeddings: ~170 MB
  HF Reranker: ~115 MB
  FAISS (1000 docs): ~2 MB
  ChromaDB: Persistent on disk
  Ollama: ~4-6 GB (LLM)
  ────────────────────────
  TOTAL: ~6-7 GB (including Ollama)

CPU THREADS:
  FAISS threads: 2 (configurable)
  Batch sizes: 32 (configurable)
  Ollama threads: Managed by Ollama

=====================================
DOCKER SETUP
=====================================

ENVIRONMENT VARIABLES:
  HF_HOME=/data/hf
    - Hugging Face model cache location
    - Persisted on volume mount

  CUDA_VISIBLE_DEVICES=""
    - Disables GPU (CPU-only)

  TOKENIZERS_PARALLELISM=false
    - Prevents tokenizer warnings

VOLUME MOUNT:
  /data
    ├── /hf              (Hugging Face model cache)
    ├── /chroma/         (ChromaDB persistence)
    └── /processed/      (Ingested documents)

DOCKERFILE:
  - Base: python:3.11-slim
  - No CUDA or GPU support
  - HF models auto-download to /data/hf
  - Models cached after first run

=====================================
USAGE IN CODE
=====================================

BASIC USAGE:

from app.vectorstore.store import get_vector_store

# Get singleton hybrid store
vs = get_vector_store()

# Add documents (auto-embeds via HF + stores in ChromaDB + FAISS)
ids = vs.add_texts(
    texts=["Document 1", "Document 2"],
    metadatas=[{"source": "source1"}, {"source": "source2"}],
)

# Hybrid search (FAISS → ChromaDB → HF Reranker)
results = vs.search(
    query="What is machine learning?",
    k=5,              # Return top-5
    faiss_k=30,       # FAISS retrieves 30 candidates
    rerank=True,      # Apply HF CrossEncoder reranking
)

for result in results:
    print(result["content"])      # Document text
    print(result["metadata"])     # Metadata
    print(result["score"])        # HF Reranker score

RAG CHAIN:

from app.rag.chains import RAGChain

rag = RAGChain()
output = rag.retrieve_and_generate(
    query="Explain quantum entanglement",
    k=5,
)

# output = {
#     "query": "Explain quantum entanglement",
#     "response": "<Ollama-generated synthesis>",
#     "context": "<Retrieved + formatted context>",
#     "sources": [<reranked documents with metadata>],
# }

DIRECT HF USAGE (if needed):

from app.hf.embeddings import get_hf_embeddings
from app.hf.reranker import get_hf_reranker

embeddings = get_hf_embeddings()
query_vec = embeddings.embed_query("What is AI?")

reranker = get_hf_reranker()
reranked = reranker.rerank(
    query="What is AI?",
    candidates=[
        {"content": "AI is..."},
        {"content": "Artificial intelligence is..."},
    ],
    top_k=1,
)

=====================================
CPU OPTIMIZATION TECHNIQUES
=====================================

1. SINGLETON PATTERN
   ✓ Each HF model loaded once
   ✓ Shared across all requests
   ✓ No re-initialization overhead

2. BATCH SIZING
   ✓ Max batch size: 32
   ✓ Prevents memory spikes
   ✓ Configurable via _BATCH_LIMIT

3. EMBEDDING CACHE
   ✓ De-duplicate identical texts
   ✓ Avoid re-encoding
   ✓ In-memory cache (thread-safe)

4. FAISS OPTIMIZATION
   ✓ CPU threads limited to 2
   ✓ Stores embeddings + IDs only (~2 MB per 1000 docs)
   ✓ IndexFlatL2 (simple, no GPU)
   ✓ Can be rebuilt from ChromaDB

5. NO GPU USAGE
   ✓ CUDA_VISIBLE_DEVICES=""
   ✓ device="cpu" everywhere
   ✓ No GPU dependencies in requirements

6. LAZY INITIALIZATION
   ✓ HF models loaded on first use
   ✓ FAISS rebuilt from persisted ChromaDB
   ✓ No blocking startup

=====================================
DISK PERSISTENCE
=====================================

DIRECTORY STRUCTURE:
  /data/
  ├── /hf/
  │   ├── models/sentence-transformers/...
  │   └── models/cross-encoder/...
  ├── /chroma/
  │   └── /scientific_db/
  │       ├── chroma.sqlite3
  │       └── data/
  └── /processed/

CHROMA PERSISTENCE:
  ✓ Automatic on add_texts/add_documents
  ✓ Survives container restart
  ✓ Safe for concurrent access

FAISS PERSISTENCE:
  ✗ Not persisted (rebuilt on startup)
  ✓ Rebuilt from ChromaDB embeddings automatically
  ✓ ~5-10 seconds to rebuild 1000 docs

=====================================
CONFIGURATION
=====================================

app/config.py:

    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHROMA_COLLECTION_NAME: str = "scientific_documents"
    CHROMA_PERSIST_DIR: Path = CHROMA_DIR / "scientific_db"
    TOP_K_RETRIEVAL: int = 5
    RERANK_TOP_K: int = 3

Optional overrides (environment variables):
    HF_HOME: Set HF model cache location
    CUDA_VISIBLE_DEVICES: Leave empty (CPU-only)

=====================================
TESTING
=====================================

UNIT TESTS:

from app.vectorstore.store import get_vector_store
from app.hf.embeddings import get_hf_embeddings

def test_hybrid_search():
    vs = get_vector_store()
    ids = vs.add_texts([
        "Python is a programming language",
        "Machine learning is a subset of AI",
    ])
    assert len(ids) == 2
    
    results = vs.search("What is machine learning?", k=1)
    assert len(results) == 1
    assert "machine learning" in results[0]["content"].lower()

INTEGRATION:

def test_rag_chain():
    from app.rag.chains import RAGChain
    rag = RAGChain()
    output = rag.retrieve_and_generate("What is AI?")
    assert output["response"]
    assert len(output["sources"]) > 0

=====================================
TROUBLESHOOTING
=====================================

ISSUE: OOM (Out of Memory)
SOLUTION:
  1. Reduce batch size: _BATCH_LIMIT = 16
  2. Reduce FAISS candidates: faiss_k = 20
  3. Clear embedding cache periodically

ISSUE: Slow embeddings
SOLUTION:
  1. Check TOKENIZERS_PARALLELISM=false (no fork)
  2. Profile: logger.info("Embedding time: X ms")
  3. Use cache hits

ISSUE: FAISS search returns no results
SOLUTION:
  1. Check ChromaDB has documents: vs.count()
  2. Rebuild FAISS: vs._rebuild_faiss_from_chroma()
  3. Verify embeddings saved: vs.chroma.export_embeddings()

ISSUE: Wrong reranking scores
SOLUTION:
  1. Verify reranker loaded: from app.hf.reranker import get_hf_reranker
  2. Check candidate format: {"content": "..."}
  3. Validate top_k: rerank(query, candidates, top_k=5)

=====================================
MONITORING
=====================================

LOGS:
  Level: INFO
  Format: JSON
  Location: logs/

KEY METRICS:
  - HF model load time
  - Embedding time per batch
  - FAISS search time
  - Reranker time
  - Total retrieval time
  - Cache hit rate

EXAMPLE LOG:
  {
    "timestamp": "2026-01-01T12:00:00",
    "level": "INFO",
    "message": "Hybrid search",
    "query": "What is AI?",
    "faiss_candidates": 30,
    "chroma_results": 30,
    "rerank_results": 5,
    "time_ms": 145,
  }

=====================================
MIGRATION FROM OLD SYSTEM
=====================================

OLD: app/llm/embeddings.py + DocumentReranker
NEW: app/hf/embeddings.py + app/hf/reranker.py

COMPATIBILITY:
  ✓ ChromaVectorStore still works (uses HF embeddings internally)
  ✓ HybridVectorStore is the main interface
  ✓ get_vector_store() returns HybridVectorStore
  ✓ RAGChain uses get_vector_store()

MIGRATION STEPS:
  1. Update imports: from app.hf.embeddings import get_hf_embeddings
  2. Delete old: app/llm/embeddings.py (or keep for backwards compatibility)
  3. Update RAG chains to use HybridVectorStore
  4. Re-embed documents (ChromaDB auto-handles via HF embeddings)

=====================================
DEPLOYMENT CHECKLIST
=====================================

□ HF_HOME=/data/hf (volume mounted)
□ CUDA_VISIBLE_DEVICES="" (CPU-only)
□ TOKENIZERS_PARALLELISM=false
□ faiss.omp_set_num_threads(2)
□ Batch size ≤ 32
□ ChromaDB persisted to /data/chroma
□ Models auto-download on first run
□ Memory: < 7 GB on CPU
□ Logging: JSON format enabled
□ Docker: python:3.11-slim base image
□ Docker: No GPU/CUDA dependencies

=====================================
FUTURE OPTIMIZATIONS
=====================================

1. QUANTIZATION
   - Quantize embeddings to int8 (75% memory reduction)
   - Quantize reranker to int8
   
2. DISTILLATION
   - Smaller embedding model (TinyBERT)
   - Faster inference, lower memory

3. CACHING
   - Redis for embedding cache (distributed)
   - Persistent embedding cache across restarts

4. ASYNC
   - Async embedding generation
   - Async reranking (if needed)

5. SPARSE RETRIEVAL
   - Hybrid BM25 + dense search
   - Better recall for rare terms

=====================================
REFERENCES
=====================================

Hugging Face Embeddings:
  https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

Hugging Face Reranker:
  https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2

FAISS Documentation:
  https://github.com/facebookresearch/faiss

Chroma Documentation:
  https://docs.trychroma.com/

LangChain Embeddings:
  https://python.langchain.com/docs/concepts/embedding_models/

=====================================
"""
