"""ARCHITECTURE DIAGRAM - TESLAS.AI WITH HUGGING FACE INTEGRATION

=====================================
RETRIEVAL PIPELINE (Step-by-Step)
=====================================

Step 1: USER QUERY
┌─────────────────┐
│   "What is AI?" │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  HF Embedding (CPU-Only)             │
│  - sentence-transformers/all-MiniLM  │
│  - Batch size: ≤ 32                  │
│  - Cached to avoid re-encoding       │
│  - Output: [384-dim vector]          │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  FAISS Index (Fast Candidate Fetch)  │
│  - Stores: embeddings + ids only     │
│  - Threads: 2 (CPU efficient)        │
│  - Returns: Top 30 candidate IDs     │
│  - Time: ~10-20ms                    │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  ChromaDB Metadata Retrieval         │
│  - Fetches documents + metadata      │
│  - Using candidate IDs from FAISS    │
│  - Persistent on /data/chroma        │
│  - Output: [30 docs with metadata]   │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  HF CrossEncoder Reranker            │
│  - cross-encoder/ms-marco-MiniLM     │
│  - Scores each query-doc pair        │
│  - Batch size: ≤ 32                  │
│  - Sorts by relevance score          │
│  - Output: Top 5 re-ranked results   │
│  - Time: ~50-100ms                   │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  Context Assembly                    │
│  - Format top-5 results              │
│  - Include metadata + sources        │
│  - Prepare for Ollama                │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  Ollama LLM (Reasoning)              │
│  - mistral / neural-chat / dolphin   │
│  - Synthesize response from context  │
│  - NO embeddings or reranking here   │
│  - Output: Final answer              │
└─────────────────────────────────────┘


=====================================
DATA FLOW DIAGRAM
=====================================

Ingestion Phase:
┌──────────────────────────────────────┐
│ Ingest Document                      │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ Text Chunking (pipeline.py)          │
│ - Chunk size: 1000                   │
│ - Overlap: 200                       │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ HF Embedding (CPU)                   │
│ - Embed all chunks                   │
│ - Batch size ≤ 32                    │
│ - [N × 384] embedding matrix         │
└────────┬─────────────────────────────┘
         │
    ┌────┴────┐
    │          │
    ▼          ▼
FAISS        ChromaDB
Index        Store
(IDs+        (Docs+
Embs)        Embs+
             Metadata)
    │          │
    └────┬─────┘
         │
    ┌────────────────┐
    │ Disk Cache     │
    │ /data/hf       │  ← Models cached here
    │ /data/chroma   │  ← ChromaDB persisted
    └────────────────┘

Search Phase:
┌──────────────────────────────────────┐
│ Query                                │
└────────┬─────────────────────────────┘
         │
         ▼
    HF Embedding ─→ [1 × 384] vector
         │
         ▼
    FAISS Search ─→ [Top 30 IDs]
         │
         ▼
    ChromaDB.get_by_ids ─→ [30 docs]
         │
         ▼
    HF Reranker ─→ [Top 5 ranked]
         │
         ▼
    Ollama Context ─→ [Final answer]


=====================================
COMPONENT INTERACTION DIAGRAM
=====================================

                    ┌─────────────────────┐
                    │ get_vector_store()  │
                    │ (singleton factory) │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────────┐
                    │ HybridVectorStore       │
                    │  - orchestrator         │
                    │  - manages all 3 layers │
                    └──────────┬──────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ HfEmbedding  │      │ ChromaDB     │      │ HfReranker   │
│ Service      │      │ VectorStore  │      │ (CrossEnc.)  │
├──────────────┤      ├──────────────┤      ├──────────────┤
│ - CPU only   │      │ - Persistent │      │ - CPU only   │
│ - Singleton  │      │ - Metadata   │      │ - Singleton  │
│ - Cached     │      │ - HNSW index │      │ - Batch ≤32  │
│ - Batch ≤32  │      │ - Fallback   │      │ - Scores     │
└──────────────┘      └──────────────┘      └──────────────┘
        │                      │                      │
        │                      └──────────┬───────────┘
        │                                 │
        └─────────────────┬───────────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ FAISS Index      │
                 ├──────────────────┤
                 │ - Fast search    │
                 │ - Embeddings+IDs │
                 │ - 2 threads      │
                 │ - Rebuilt on     │
                 │   startup        │
                 └──────────────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ /data/ Volume    │
                 ├──────────────────┤
                 │ /hf/ (models)    │
                 │ /chroma/ (db)    │
                 │ /processed/ (raw)│
                 └──────────────────┘


=====================================
MEMORY USAGE BREAKDOWN
=====================================

Component              Size        Notes
─────────────────────────────────────────────
HF Embeddings Model    ~22 MB      sentence-transformers
HF Embeddings Cache    ~128 MB     Batch of 32 texts
HF Reranker Model      ~28 MB      cross-encoder
HF Reranker Batch      ~64 MB      32 query-doc pairs
FAISS Index            ~2 MB       Per 1000 vectors
ChromaDB (memory)      ~50 MB      Open collection
Python Runtime         ~200 MB     Base interpreter
─────────────────────────────────────────────
Total HF + Indexes     ~494 MB     Fixed overhead
Ollama LLM             ~4-6 GB     Depends on model
─────────────────────────────────────────────
TOTAL (CPU-only)       ~5-7 GB     Conservative estimate


=====================================
LATENCY PROFILE
=====================================

Operation                Latency    Notes
────────────────────────────────────────────
HF Embedding (1 query)   ~5-10 ms   Cached after first use
FAISS search (30k vecs)  ~15-25 ms  2 threads, L2 distance
ChromaDB metadata fetch  ~10-20 ms  From disk/memory
HF Reranking (30 docs)   ~50-100 ms Batch scoring
Ollama LLM response      ~500-5000ms Depends on model
────────────────────────────────────────────
Total Retrieval          ~100-200ms Per query
Total RAG (with LLM)     ~1-7 sec   Per complete request


=====================================
THREAD SAFETY
=====================================

Component              Thread-Safe  Method
────────────────────────────────────────────
HfEmbeddingService     ✓ (lock)     Lock around cache + inference
HfCrossEncoderReranker ✓            No state mutations
ChromaDB (Chroma lib)  ✓            SQLite transaction
FAISS                  ✗ (2 threads) Manual thread limiting
────────────────────────────────────────────

For async usage:
  - Use asyncio.to_thread() for HF models
  - Run LLM in thread pool
  - Keep ChromaDB access serialized


=====================================
FALLBACK CHAIN
=====================================

Hybrid Search Fallback:
  ┌─────────────────────────────┐
  │ Try FAISS + Reranker        │
  └────────┬────────────────────┘
           │
     ✓ Success? Yes ─→ Return top-k reranked
           │ No
           ▼
  ┌─────────────────────────────┐
  │ Fall back to ChromaDB only  │
  │ (pure semantic search)      │
  └────────┬────────────────────┘
           │
     ✓ Success? Yes ─→ Return top-k by score
           │ No
           ▼
  ┌─────────────────────────────┐
  │ Return empty results        │
  │ Log warning                 │
  └─────────────────────────────┘

No HF model failures can block RAG pipeline.


=====================================
DOCKER DEPLOYMENT ARCHITECTURE
=====================================

┌─────────────────────────────────────────────────┐
│          Docker Container (python:3.11-slim)    │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌────────────────────────────────────────┐    │
│  │ FastAPI Server (port 8000)             │    │
│  │  - /research                           │    │
│  │  - /search                             │    │
│  │  - /kb/search                          │    │
│  │  - /ingest                             │    │
│  └──────────┬───────────────────────────┬─┘   │
│             │                           │      │
│  ┌──────────▼────────┐      ┌──────────▼──┐  │
│  │ RAGChain (Ollama) │      │ Vector Store │  │
│  │ - Orchestrator    │      │ - Hybrid     │  │
│  │ - Synthesis       │      │ - FAISS+     │  │
│  │                   │      │   ChromaDB   │  │
│  └───────────────────┘      └──────────────┘  │
│             │                       │          │
│             ▼                       ▼          │
│      ┌──────────────┐        ┌─────────────┐  │
│      │ Ollama       │        │ HF Embed +  │  │
│      │ (LLM)        │        │ Reranker    │  │
│      │ port:11434   │        │ (CPU-only)  │  │
│      └──────────────┘        └─────────────┘  │
│                                    │           │
└────────────────────────────────────┼───────────┘
                    ┌────────────────▼────────────┐
                    │   Volume Mount: /data       │
                    │   ├── /hf (models)          │
                    │   ├── /chroma (ChromaDB)    │
                    │   └── /processed (docs)     │
                    └─────────────────────────────┘


Network Flow:
  Client HTTP ──→ [FastAPI:8000] ──→ RAGChain
                                 ├──→ [Ollama:11434]
                                 └──→ [HF Embeddings+Reranker]


=====================================
"""
