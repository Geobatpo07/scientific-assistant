# Teslas.ai Execution Modes: FAST vs FULL

## Overview

Teslas.ai supports two distinct execution modes that control agent selection, RAG depth, and resource usage to optimize the balance between speed and rigor.

## Mode Definitions

### 🚀 FAST MODE

**Purpose:**
- Quick scientific answers
- Exploratory analysis
- Daily interactive usage
- Rapid prototyping

**Characteristics:**
- **Runtime:** Few minutes maximum
- **Latency:** Minimal
- **Rigor:** Moderate
- **Resource Usage:** Low

**Agent Configuration:**

| Agent | Status | Behavior |
|-------|--------|----------|
| Planner | Optional | Lightweight planning only |
| Mathematician | Optional | Only if clearly mathematical |
| Numerical | Optional | Only if clearly numerical |
| Data Scientist | ❌ Disabled | Skipped entirely |
| Literature | Optional | Quick search only |
| Reviewer | ❌ Disabled | No scientific review |
| Writer | ✅ Enabled | Concise output |
| Memory | ❌ Disabled | No memory curation |

**RAG Configuration:**
- FAISS top-k: **15** documents
- Final chunks: **3** (after reranking)
- Context compression: Enabled
- Web search: Disabled

**LLM Configuration:**
- Temperature: **0.1** (more deterministic)
- Max tokens: **2000** (shorter responses)
- Timeout: **120s** per call

**Iteration Limits:**
- Max iterations: **3**
- Max agent calls: **5**

**Best For:**
- Quick calculations
- Concept clarification
- Exploratory queries
- Interactive sessions
- Prototyping ideas

---

### 🔬 FULL MODE

**Purpose:**
- Deep scientific research
- Publication-grade analysis
- High-rigor investigations
- Comprehensive reviews

**Characteristics:**
- **Runtime:** Tens of minutes (acceptable)
- **Latency:** Higher (prioritizes correctness)
- **Rigor:** Maximum
- **Resource Usage:** High

**Agent Configuration:**

| Agent | Status | Behavior |
|-------|--------|----------|
| Planner | ✅ Enabled | Full strategic planning |
| Mathematician | ✅ Enabled | Complete mathematical analysis |
| Numerical | ✅ Enabled | Full numerical simulation |
| Data Scientist | ✅ Enabled | Complete data analysis |
| Literature | ✅ Enabled | Comprehensive literature search |
| Reviewer | ✅ Enabled | Critical scientific review |
| Writer | ✅ Enabled | Detailed structured output |
| Memory | ✅ Enabled | Memory curation and storage |

**RAG Configuration:**
- FAISS top-k: **30** documents
- Final chunks: **5** (after reranking)
- Context compression: Enabled (preserves detail)
- Web search: Enabled (if available)

**LLM Configuration:**
- Temperature: **0.3** (balanced)
- Max tokens: **4000** (detailed responses)
- Timeout: **300s** per call

**Iteration Limits:**
- Max iterations: **10**
- Max agent calls: **20**

**Best For:**
- Research papers
- Grant proposals
- Critical analysis
- Production models
- Publication preparation
- Comprehensive reviews

---

## Usage Examples

### Python API

```python
from app.assistant import Assistant
from app.config import ExecutionMode

assistant = Assistant()

# FAST mode - quick answer
result_fast = assistant.research(
    "What is the Taylor series expansion of e^x?",
    mode=ExecutionMode.FAST
)

# FULL mode - deep research
result_full = assistant.research(
    "Analyze the computational complexity of quantum algorithms for factorization",
    mode=ExecutionMode.FULL
)
```

### REST API

**FAST Mode Request:**
```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Derive the heat equation",
    "mode": "fast"
  }'
```

**FULL Mode Request:**
```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Compare gradient descent variants for deep learning optimization",
    "mode": "full"
  }'
```

### Selective Agent Mode

You can also specify agents explicitly (overrides mode defaults):

```python
# Use specific agents with FAST mode parameters
result = assistant.research(
    "Solve the differential equation dy/dx = x^2",
    agents=["planner", "mathematician", "writer"],
    mode=ExecutionMode.FAST
)
```

---

## Decision Guide

### Choose FAST Mode When:

✅ You need a quick answer  
✅ Exploring new topics  
✅ Time is critical  
✅ Question is straightforward  
✅ Interactive development  
✅ Prototyping phase  

### Choose FULL Mode When:

✅ Research for publication  
✅ High-stakes decisions  
✅ Need comprehensive review  
✅ Complex multi-disciplinary query  
✅ Want memory persistence  
✅ Require traceability  
✅ Maximum rigor needed  

---

## Architecture Details

### Configuration Location

All mode configurations are defined in [`app/config.py`](../app/config.py):

```python
class ExecutionMode(str, Enum):
    FAST = "fast"
    FULL = "full"

class ModeConfig:
    AGENT_CONFIG: Dict[str, Dict[str, Any]] = {...}
    RAG_CONFIG: Dict[str, Dict[str, Any]] = {...}
    LLM_CONFIG: Dict[str, Dict[str, Any]] = {...}
    ITERATION_CONFIG: Dict[str, Dict[str, int]] = {...}
```

### Flow Through Stack

```
API Request (mode parameter)
    ↓
Assistant.research(query, mode)
    ↓
Orchestrator.run_research(query, mode)
    ↓
ModeConfig.get_agent_config(mode)
    ↓
Agent Execution (mode-aware)
    ↓
RAG Chain (mode-specific parameters)
    ↓
Response (with mode metadata)
```

### Mode Enforcement

Mode parameters are enforced at multiple levels:

1. **Orchestrator Level** ([`app/agents/graph.py`](../app/agents/graph.py))
   - Agent selection
   - Iteration limits
   - Agent call counting

2. **RAG Level** ([`app/rag/chains.py`](../app/rag/chains.py))
   - Retrieval depth (top-k)
   - Chunk limits
   - Context compression

3. **LLM Level** (future enhancement)
   - Temperature control
   - Token limits
   - Timeout configuration

---

## Extending the System

### Adding a New Mode

To add a new mode (e.g., `RESEARCH`, `INTERACTIVE`):

1. **Add to Enum** ([`app/config.py`](../app/config.py)):
```python
class ExecutionMode(str, Enum):
    FAST = "fast"
    FULL = "full"
    RESEARCH = "research"  # New mode
```

2. **Define Configuration** ([`app/config.py`](../app/config.py)):
```python
AGENT_CONFIG: Dict[str, Dict[str, Any]] = {
    ExecutionMode.RESEARCH: {
        "planner": True,
        "mathematician": True,
        "reviewer": True,
        "writer": True,
        "memory": "optional",
        ...
    }
}
```

3. **Update Documentation** (this file)

### Customizing Parameters

Modify [`app/config.py`](../app/config.py) → `ModeConfig` class:

```python
RAG_CONFIG: Dict[str, Dict[str, Any]] = {
    ExecutionMode.FAST: {
        "faiss_top_k": 20,  # Increase from 15
        "final_chunks": 4,  # Increase from 3
        ...
    }
}
```

---

## Performance Benchmarks

### Typical Runtimes (Approximate)

| Query Type | FAST Mode | FULL Mode |
|------------|-----------|-----------|
| Simple calculation | 30s - 1m | 2m - 5m |
| Equation derivation | 1m - 2m | 5m - 10m |
| Literature review | 2m - 3m | 10m - 20m |
| Complex analysis | 3m - 5m | 20m - 40m |

*Note: Times depend on hardware, LLM model, and query complexity*

### Resource Usage

| Resource | FAST Mode | FULL Mode |
|----------|-----------|-----------|
| Agent calls | ~5 | ~15-20 |
| RAG queries | ~3 chunks | ~5 chunks |
| Memory usage | Low | Moderate |
| LLM tokens | ~2k | ~4k |

---

## Testing

Run mode-specific tests:

```bash
# Test FAST mode
pytest tests/test_execution_modes.py::test_fast_mode -v

# Test FULL mode
pytest tests/test_execution_modes.py::test_full_mode -v

# Test mode switching
pytest tests/test_execution_modes.py::test_mode_switching -v
```

---

## Troubleshooting

### Issue: FAST mode too slow
**Solution:** Check agent logs. Optional agents may be running unnecessarily. Ensure plan complexity detection works correctly.

### Issue: FULL mode runs out of memory
**Solution:** Reduce `faiss_top_k` or `final_chunks` in config. Monitor ChromaDB size.

### Issue: Results differ between modes
**Expected behavior.** FAST mode trades depth for speed. Use FULL mode when correctness is critical.

---

## References

- [Configuration Source](../app/config.py)
- [Orchestrator Implementation](../app/agents/graph.py)
- [RAG Chain Implementation](../app/rag/chains.py)
- [API Schemas](../app/api/schemas.py)
- [API Routes](../app/api/routes.py)

---

**Version:** 1.0  
**Last Updated:** 2026-01-02  
**Status:** Production Ready ✅
