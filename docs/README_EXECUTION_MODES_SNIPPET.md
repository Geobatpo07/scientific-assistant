# Execution Modes - Quick Start Guide

Add this section to your main README.md to document the new execution mode feature.

---

## ⚡ Execution Modes

Teslas.ai supports two execution modes to optimize the balance between speed and rigor:

### 🚀 FAST Mode (Default)
**Use for:** Quick answers, exploration, daily usage  
**Runtime:** 1-5 minutes  
**Agents:** Essential only (planner, mathematician, writer)  
**RAG:** Limited depth (15 docs → 3 chunks)

```python
from app.assistant import Assistant

assistant = Assistant()
result = assistant.research("What is the Taylor series of e^x?")
```

```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "Derive the heat equation", "mode": "fast"}'
```

### 🔬 FULL Mode
**Use for:** Deep research, publication, high rigor  
**Runtime:** 5-40 minutes  
**Agents:** ALL (including reviewer, memory, data scientist)  
**RAG:** Maximum depth (30 docs → 5 chunks)

```python
from app.config import ExecutionMode

result = assistant.research(
    "Analyze quantum entanglement mechanisms",
    mode=ExecutionMode.FULL
)
```

```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "Compare ML optimizers", "mode": "full"}'
```

### 📊 Mode Comparison

| Feature | FAST | FULL |
|---------|------|------|
| Runtime | 1-5 min | 5-40 min |
| Agents | 3-5 | 8+ |
| Review | ❌ | ✅ |
| Memory | ❌ | ✅ |
| RAG Depth | 3 chunks | 5 chunks |
| Best For | Quick Q&A | Research papers |

### 📚 Learn More
- **[Complete Documentation](docs/EXECUTION_MODES.md)** - Full mode definitions and usage
- **[Quick Reference](docs/EXECUTION_MODES_QUICK_REF.md)** - At-a-glance comparison
- **[Architecture](docs/EXECUTION_MODES_ARCHITECTURE.md)** - System design details
- **[Examples](examples/example_execution_modes.py)** - Code examples
- **[Tests](tests/test_execution_modes.py)** - Test suite

---

## 🎯 When to Use Each Mode

### Choose FAST Mode When:
- ✅ Need quick answer (< 5 minutes)
- ✅ Exploring new topics
- ✅ Straightforward question
- ✅ Interactive development
- ✅ Time is critical

### Choose FULL Mode When:
- ✅ Research for publication
- ✅ High-stakes decisions
- ✅ Need comprehensive review
- ✅ Complex multi-disciplinary query
- ✅ Want memory persistence
- ✅ Maximum rigor required

---

Add this section after the "Features" section in your main README.md
