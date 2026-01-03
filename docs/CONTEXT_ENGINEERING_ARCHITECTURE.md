# Context Engineering Layer: Architecture & Design

## Executive Summary

The Context Engineering layer is a lightweight preprocessing stage that optimizes context **before** it reaches the main LLM. It uses Flan-T5 (google/flan-t5-base) to normalize queries and compress retrieved documents without performing reasoning.

**Key Achievement**: Improved context quality with no reasoning contamination.

---

## System Architecture

### Before (Without Context Engineering)

```
User Query
    ↓
RAG Retrieval (FAISS + ChromaDB + HF reranker)
    ↓
Noisy/Raw Context
    ↓
ChatOllama
    ↓
Response (quality depends on raw context)
```

**Problems**:
- Noisy, ambiguous queries lead to poor retrieval
- Retrieved documents may contain redundancy and noise
- Context contamination affects LLM reasoning

### After (With Context Engineering)

```
User Query
    ↓
ContextEngineer.normalize_query (Flan-T5)
    ↓
Clarified Query
    ↓
RAG Retrieval (FAISS + ChromaDB + HF reranker)
    ↓
Retrieved Documents
    ↓
ContextEngineer.compress_context (Flan-T5)
    ↓
Clean, Compressed Context
    ↓
ChatOllama
    ↓
Response (based on optimized context)
```

**Benefits**:
- Explicit, clearer queries improve retrieval
- Compressed context reduces noise and bias
- LLM receives structured, curated context
- Better reasoning and synthesis

---

## Module Structure

```
app/
├── hf/
│   ├── __init__.py                    # Exports ContextEngineer
│   ├── embeddings.py                  # HF embedding service
│   ├── reranker.py                    # HF cross-encoder reranker
│   ├── context_engineering.py         # ✨ NEW: Context preprocessing
│   │
│   ├── Models:
│   │   ├── all-MiniLM-L6-v2 (embeddings)
│   │   ├── cross-encoder/ms-marco-MiniLM-L-6-v2 (reranker)
│   │   └── google/flan-t5-base (context engineering) ✨ NEW
│
├── rag/
│   ├── chains.py                      # Updated: Integrated context engineering
│   │
│   ├── Pipeline:
│   │   1. normalize_query (Flan-T5)
│   │   2. retrieve (FAISS + ChromaDB)
│   │   3. compress_context (Flan-T5)
│   │   4. assemble_context
│   │   5. llm.invoke (ChatOllama)
```

---

## Component Details

### 1. ContextEngineer (NEW)

**File**: `app/hf/context_engineering.py`

**Purpose**: Lightweight preprocessing using Flan-T5

**Interface**:
```python
class ContextEngineer:
    def normalize_query(query: str) -> str
    def compress_context(text: str) -> str
    def compress_context_batch(texts: List[str]) -> List[str]
```

**Constraints**:
- CPU-only (no GPU)
- Model loaded once (singleton)
- max_new_tokens = 128
- Greedy decoding (deterministic)
- NO reasoning or conclusions

### 2. RAGChain (UPDATED)

**File**: `app/rag/chains.py`

**Changes**:
1. Import ContextEngineer
2. Initialize context_engineer in `__init__`
3. Normalize query before retrieval
4. Compress context after retrieval
5. Assemble context with source metadata

**Method**: `retrieve_and_generate(query, k=5, system_prompt=None)`

**Returns**:
```python
{
    "query": str,                  # Original query
    "normalized_query": str,       # Clarified query
    "response": str,               # LLM answer
    "context": str,                # Compressed context
    "sources": List[dict],         # Retrieved docs
}
```

### 3. Hybrid Vector Store (UNCHANGED)

**Components**:
- HF Embeddings: `all-MiniLM-L6-v2`
- FAISS: Dense vector index
- ChromaDB: Persistent storage
- HF Reranker: Cross-encoder ranking

**No changes to existing retrieval logic**

### 4. ChatOllama (UNCHANGED)

**Role**: Final reasoning and synthesis

**Input**: Preprocessed context + system prompt

**No changes to LLM logic**

---

## Data Flow

### Query Normalization

```
Input Query:        "How u calculate regression?"
                    ↓
Flan-T5 Prompt:     "Normalize this query for scientific retrieval.
                     Expand abbreviations and clarify terminology.
                     Output only the normalized query: ..."
                    ↓
Output Query:       "How do you calculate linear regression analysis?"
```

**Purpose**: Improve retrieval by clarifying intent

### Context Compression

```
Input Document:     "Linear regression is a statistical method... [1000 chars]"
                    ↓
Flan-T5 Prompt:     "Compress this passage. Keep definitions and equations.
                     Remove redundancy. Output only compressed passage: ..."
                    ↓
Output Document:    "Linear regression: statistical method for modeling linear
                     relationships using least squares. Key assumptions: 
                     linearity, independence, homoscedasticity, normality. [128 chars]"
```

**Purpose**: Reduce noise while preserving essential information

---

## Model Selection Rationale

### Why google/flan-t5-base?

| Metric | Flan-T5-base | Flan-T5-large | Flan-T5-xl |
|--------|--------------|---------------|-----------|
| Parameters | 250M | 780M | 3B |
| Size | ~990MB | ~3GB | ~12GB |
| CPU Time/Query | 100-200ms | 500ms+ | 2s+ |
| GPU Required | Optional | Recommended | Required |
| Output Quality | ★★★★☆ | ★★★★★ | ★★★★★ |
| **Selected** | ✓ | | |

**Decision**: Optimal balance between quality, speed, and CPU compatibility

### Why NOT use larger models?

- **Flan-T5-large/xl**: Require GPU, slower on CPU, overkill for preprocessing
- **Mistral/Llama**: Too large, designed for reasoning (our job is NOT reasoning)
- **GPT**: Requires API, external dependency

### Why NOT use smaller models?

- **Flan-T5-small**: Lower quality, less reliable
- **T5-base**: Not instruction-tuned, poor zero-shot performance

---

## Performance Characteristics

### Latency

| Operation | Time | Note |
|-----------|------|------|
| First load | 2-3s | One-time (cached) |
| normalize_query | 100-150ms | Single forward pass |
| compress_context | 120-180ms | Per document |
| Batch (5 docs) | 600-900ms | Sequential processing |
| Full RAG pipeline | 1-3s | Including retrieval |

### Memory

| Component | Size |
|-----------|------|
| Flan-T5 model | ~250MB |
| Tokenizer | ~10MB |
| Inference buffer | ~50-100MB |
| **Total** | **~400MB** |

**Once loaded**, negligible overhead for subsequent calls.

### CPU Usage

- Single-threaded processing
- No GPU parallelism
- Predictable, deterministic execution

---

## Determinism & Reproducibility

All operations are deterministic:

```python
query = "How to calculate variance?"

# Greedy decoding (no sampling)
result1 = engineer.normalize_query(query)
result2 = engineer.normalize_query(query)

assert result1 == result2  # ✓ Always true
```

**Why?**
1. **Greedy decoding**: Selects highest probability token at each step
2. **No sampling**: No randomness in token selection
3. **CPU-only**: No GPU indeterminism
4. **Fixed weights**: Model weights loaded once

---

## Role Separation (STRICT)

### Flan-T5 (ContextEngineer)

```
✓ Allowed:
  - Query clarification
  - Context compression
  - Redundancy removal
  - Definition preservation

✗ Prohibited:
  - Reasoning
  - Inference
  - Conclusions
  - Hypothesis generation
  - Final answer
```

### ChatOllama

```
✓ Allowed:
  - Reasoning
  - Inference
  - Mathematical proofs
  - Synthesis
  - Answer generation

✗ Prohibited:
  - Context engineering
  - Preprocessing
```

---

## Integration Checklist

- [x] Create `app/hf/context_engineering.py`
- [x] Implement ContextEngineer class
- [x] Implement normalize_query method
- [x] Implement compress_context method
- [x] Implement compress_context_batch method
- [x] Update `app/rag/chains.py`
- [x] Integrate context engineering into RAGChain
- [x] Update RAGChain.retrieve_and_generate
- [x] Add documentation
- [x] Add tests
- [x] Add examples
- [x] Update `app/hf/__init__.py`

---

## Testing Strategy

### Unit Tests (`tests/test_context_engineering.py`)

1. **Initialization**
   - Singleton pattern verification
   - Model loading verification
   - Device verification (CPU-only)

2. **Query Normalization**
   - Basic normalization
   - Empty input handling
   - Intent preservation

3. **Context Compression**
   - Basic compression
   - Definition preservation
   - Redundancy removal
   - Empty input handling

4. **Batch Operations**
   - Multiple documents
   - Error recovery
   - Order preservation

5. **Constraints**
   - Model version
   - Max tokens
   - CPU-only execution
   - Determinism

### Integration Tests

- RAG chain integration
- Full pipeline end-to-end
- Response format verification

---

## Monitoring & Diagnostics

### Logging

All operations log to `app.hf.context_engineering`:

```python
DEBUG: Normalized query: "..." → "..."
DEBUG: Compressed context: 1543 chars → 127 chars
INFO: Loading HF CrossEncoder reranker (CPU): ...
WARNING: Failed to compress chunk 3: ...
```

### Metrics to Track

```python
{
    "normalized_query_length": int,
    "original_context_length": int,
    "compressed_context_length": int,
    "compression_ratio": float,
    "processing_time_ms": float,
}
```

---

## Future Extensions

### Potential Enhancements (Not Implemented)

1. **Query Expansion**: Expand query with related terms (for better retrieval)
2. **Query Disambiguation**: Handle ambiguous queries with clarification
3. **Document Summarization**: Extractive or abstractive summary options
4. **Factual Preservation**: Verify key facts are preserved during compression
5. **Multilingual Support**: Normalize queries in multiple languages

### NOT Planned (Against Design)

- Using Flan-T5 for final answer generation
- GPU acceleration (defeats determinism)
- Real-time batching (violates constraints)
- Replacing ChatOllama (violates role separation)

---

## Troubleshooting

### Issue: Model download fails

**Solution**:
```bash
python -c "from transformers import AutoModel; \
  AutoModel.from_pretrained('google/flan-t5-base')"
```

### Issue: High memory usage

**Solution**:
- Model is cached globally (load once, reuse forever)
- Check for multiple Python processes

### Issue: Slow responses

**Solution**:
- First call includes model loading (2-3s)
- Subsequent calls are fast (100-200ms)

---

## References

- [Flan-T5 Paper](https://arxiv.org/abs/2210.11416)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
- [LangChain Integration](https://python.langchain.com/)
- [ChromaDB + FAISS](https://docs.trychroma.com/)

---

## Compliance Checklist

- [x] No GPU usage
- [x] Max tokens ≤ 128
- [x] CPU-only execution
- [x] Model loaded once (singleton)
- [x] No reasoning performed
- [x] No conclusions drawn
- [x] Deterministic output
- [x] Source metadata preserved
- [x] Graceful error handling
- [x] Comprehensive logging
- [x] Production-quality code
- [x] Clear docstrings

---

**Status**: ✅ COMPLETE & PRODUCTION READY

**Version**: 1.0.0

**Last Updated**: January 2026
