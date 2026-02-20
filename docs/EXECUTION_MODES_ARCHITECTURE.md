# Execution Mode System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     TESLAS.AI ARCHITECTURE                      │
│                    With Execution Mode Support                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  API Layer (FastAPI)                                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  POST /research                                            │ │
│  │  Body: { query: str, mode: "fast" | "full", agents?: [] } │ │
│  │  → ResearchRequest (Pydantic Schema)                       │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Assistant Facade                                               │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  def research(query, agents, mode):                        │ │
│  │      → orchestrator.run_research(query, mode)              │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Orchestrator (LangGraph Principles)                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  def run_research(query, mode):                            │ │
│  │                                                            │ │
│  │    1. Get mode config:                                     │ │
│  │       agent_cfg = ModeConfig.get_agent_config(mode)        │ │
│  │       iter_cfg = ModeConfig.get_iteration_config(mode)     │ │
│  │                                                            │ │
│  │    2. Execute agents based on mode:                        │ │
│  │       if agent_cfg["planner"]: planner.plan()              │ │
│  │       if agent_cfg["mathematician"]: math.analyze()        │ │
│  │       ...                                                   │ │
│  │       if agent_cfg["reviewer"]: reviewer.review()  ✅/❌   │ │
│  │       if agent_cfg["memory"]: memory.curate()      ✅/❌   │ │
│  │                                                            │ │
│  │    3. Track agent calls vs max_agent_calls                 │ │
│  │                                                            │ │
│  │    4. Return ResearchContext with metadata                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────┬───────────────────────────────┬─────────────────┘
                │                               │
        ┌───────▼────────┐             ┌────────▼────────┐
        │  Agent Layer   │             │   RAG Layer     │
        └────────────────┘             └─────────────────┘
```

## Configuration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  app/config.py                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  class ExecutionMode(str, Enum):                           │ │
│  │      FAST = "fast"                                         │ │
│  │      FULL = "full"                                         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  class ModeConfig:                                         │ │
│  │                                                            │ │
│  │      AGENT_CONFIG: Dict[ExecutionMode, Dict[str, Any]]    │ │
│  │      ┌──────────────────────────────────────────────────┐ │ │
│  │      │  ExecutionMode.FAST:                             │ │ │
│  │      │    planner: "optional"                           │ │ │
│  │      │    mathematician: "optional"                     │ │ │
│  │      │    reviewer: False      ← DISABLED               │ │ │
│  │      │    memory: False        ← DISABLED               │ │ │
│  │      │    writer: True                                  │ │ │
│  │      └──────────────────────────────────────────────────┘ │ │
│  │      ┌──────────────────────────────────────────────────┐ │ │
│  │      │  ExecutionMode.FULL:                             │ │ │
│  │      │    ALL agents: True     ← ALL ENABLED            │ │ │
│  │      └──────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │      RAG_CONFIG: Dict[ExecutionMode, Dict[str, Any]]      │ │
│  │      ┌──────────────────────────────────────────────────┐ │ │
│  │      │  ExecutionMode.FAST:                             │ │ │
│  │      │    faiss_top_k: 15                               │ │ │
│  │      │    final_chunks: 3                               │ │ │
│  │      │    web_search_enabled: False                     │ │ │
│  │      └──────────────────────────────────────────────────┘ │ │
│  │      ┌──────────────────────────────────────────────────┐ │ │
│  │      │  ExecutionMode.FULL:                             │ │ │
│  │      │    faiss_top_k: 30                               │ │ │
│  │      │    final_chunks: 5                               │ │ │
│  │      │    web_search_enabled: True                      │ │ │
│  │      └──────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │      LLM_CONFIG: {...}                                     │ │
│  │      ITERATION_CONFIG: {...}                               │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Mode Enforcement Flow

```
┌──────────────────────────────────────────────────────────────────┐
│  Request with Mode                                               │
└────────────┬─────────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────────┐
│  ORCHESTRATOR LAYER                                              │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │  Get Agent Config                                            ││
│  │  agent_cfg = ModeConfig.get_agent_config(mode)               ││
│  │                                                              ││
│  │  FAST:                           FULL:                       ││
│  │  ┌─────────────────┐            ┌─────────────────┐         ││
│  │  │ planner: opt    │            │ planner: True   │         ││
│  │  │ math: opt       │            │ math: True      │         ││
│  │  │ numerical: opt  │            │ numerical: True │         ││
│  │  │ data_sci: False │ ← Skip     │ data_sci: True  │ ← Run   ││
│  │  │ literature: opt │            │ literature: True│         ││
│  │  │ reviewer: False │ ← Skip     │ reviewer: True  │ ← Run   ││
│  │  │ writer: True    │ ← Run      │ writer: True    │ ← Run   ││
│  │  │ memory: False   │ ← Skip     │ memory: True    │ ← Run   ││
│  │  └─────────────────┘            └─────────────────┘         ││
│  └──────────────────────────────────────────────────────────────┘│
└────────────┬─────────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────────┐
│  RAG LAYER                                                       │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │  Get RAG Config                                              ││
│  │  rag_cfg = ModeConfig.get_rag_config(mode)                   ││
│  │                                                              ││
│  │  FAST:                           FULL:                       ││
│  │  ┌─────────────────┐            ┌─────────────────┐         ││
│  │  │ top-k: 15       │            │ top-k: 30       │         ││
│  │  │ chunks: 3       │            │ chunks: 5       │         ││
│  │  │ web: False      │            │ web: True       │         ││
│  │  └─────────────────┘            └─────────────────┘         ││
│  │                                                              ││
│  │  retrieve_with_metadata(query, k=faiss_top_k)                ││
│  │  → Limit to final_chunks                                     ││
│  └──────────────────────────────────────────────────────────────┘│
└────────────┬─────────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────────┐
│  LLM LAYER (Future Enhancement)                                  │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │  llm_cfg = ModeConfig.get_llm_config(mode)                   ││
│  │  → temperature, max_tokens, timeout                          ││
│  └──────────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────┘
```

## Agent Execution Decision Tree

```
                         Start Research
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Check Mode         │
                    └──────────┬───────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                 │
              ▼                                 ▼
     ┌─────────────────┐              ┌─────────────────┐
     │  FAST Mode      │              │  FULL Mode      │
     └────────┬────────┘              └────────┬────────┘
              │                                 │
              ▼                                 ▼
     ┌─────────────────┐              ┌─────────────────┐
     │ Planner?        │              │ Planner         │
     │ - If optional   │              │ - Always run    │
     └────────┬────────┘              └────────┬────────┘
              │                                 │
              ▼                                 ▼
     ┌─────────────────┐              ┌─────────────────┐
     │ Mathematician?  │              │ Mathematician   │
     │ - If in plan    │              │ - If in plan    │
     └────────┬────────┘              └────────┬────────┘
              │                                 │
              ▼                                 ▼
     ┌─────────────────┐              ┌─────────────────┐
     │ Numerical?      │              │ Numerical       │
     │ - If in plan    │              │ - If in plan    │
     └────────┬────────┘              └────────┬────────┘
              │                                 │
              ▼                                 ▼
     ┌─────────────────┐              ┌─────────────────┐
     │ Data Scientist  │              │ Data Scientist  │
     │ ❌ SKIP         │              │ - If in plan    │
     └────────┬────────┘              └────────┬────────┘
              │                                 │
              ▼                                 ▼
     ┌─────────────────┐              ┌─────────────────┐
     │ Literature?     │              │ Literature      │
     │ - If in plan    │              │ - If in plan    │
     └────────┬────────┘              └────────┬────────┘
              │                                 │
              ▼                                 ▼
     ┌─────────────────┐              ┌─────────────────┐
     │ Reviewer        │              │ Reviewer        │
     │ ❌ SKIP         │              │ ✅ ALWAYS       │
     └────────┬────────┘              └────────┬────────┘
              │                                 │
              ▼                                 ▼
     ┌─────────────────┐              ┌─────────────────┐
     │ Writer          │              │ Writer          │
     │ ✅ ALWAYS       │              │ ✅ ALWAYS       │
     └────────┬────────┘              └────────┬────────┘
              │                                 │
              ▼                                 ▼
     ┌─────────────────┐              ┌─────────────────┐
     │ Memory          │              │ Memory          │
     │ ❌ SKIP         │              │ ✅ ALWAYS       │
     └────────┬────────┘              └────────┬────────┘
              │                                 │
              └────────────────┬────────────────┘
                               ▼
                    ┌──────────────────────┐
                    │   Return Context     │
                    │   with metadata      │
                    └──────────────────────┘
```

## Key Design Principles

### 1. **Explicit Configuration**
- All mode parameters centralized in `ModeConfig`
- No hidden globals or magic values
- Clear mapping: mode → parameters

### 2. **Type Safety**
- `ExecutionMode` enum enforces valid values
- Pydantic schemas validate API requests
- Type hints throughout stack

### 3. **Separation of Concerns**
- **Configuration Layer**: `app/config.py`
- **Orchestration Layer**: `app/agents/graph.py`
- **RAG Layer**: `app/rag/chains.py`
- **API Layer**: `app/api/routes.py` + `schemas.py`

### 4. **Testability**
- Mockable agent methods
- Configuration queries are pure functions
- No side effects in config access

### 5. **Extensibility**
- New modes: add to enum + config dicts
- New parameters: add to config classes
- No orchestrator changes needed

### 6. **Traceability**
- Mode stored in `context.metadata`
- Agent execution path tracked
- Full audit trail in response

## File Structure

```
app/
├── config.py                    ← ExecutionMode + ModeConfig
├── assistant.py                 ← Mode passthrough
├── agents/
│   ├── graph.py                 ← Mode-aware orchestration
│   └── states.py                ← Context with metadata
├── rag/
│   └── chains.py                ← Mode-aware RAG
└── api/
    ├── routes.py                ← Mode parameter handling
    └── schemas.py               ← Mode in request/response

docs/
├── EXECUTION_MODES.md           ← Full documentation
└── EXECUTION_MODES_QUICK_REF.md ← Quick reference

examples/
└── example_execution_modes.py   ← Usage examples

tests/
└── test_execution_modes.py      ← Comprehensive tests
```

## Future Enhancements

1. **Dynamic Mode Selection**
   - Auto-detect query complexity
   - Suggest optimal mode to user

2. **Hybrid Modes**
   - BALANCED mode (between FAST/FULL)
   - CUSTOM mode (user-defined parameters)

3. **Performance Monitoring**
   - Track mode runtime statistics
   - Optimize mode configurations

4. **LLM Parameter Control**
   - Pass temperature/max_tokens to LLM
   - Mode-specific system prompts

5. **Streaming Support**
   - Stream mode-aware updates
   - Progressive result disclosure

---

**Status:** ✅ Production Ready  
**Version:** 1.0  
**Last Updated:** 2026-01-02
