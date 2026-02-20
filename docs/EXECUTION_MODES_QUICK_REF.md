# Execution Modes Quick Reference

## 🎯 At a Glance

| Aspect | FAST Mode 🚀 | FULL Mode 🔬 |
|--------|-------------|-------------|
| **Runtime** | 1-5 minutes | 5-40 minutes |
| **Use Case** | Quick answers, exploration | Deep research, publication |
| **Agents** | 3-5 agents | 8+ agents |
| **RAG Depth** | 3 chunks from top-15 | 5 chunks from top-30 |
| **Review** | ❌ None | ✅ Scientific review |
| **Memory** | ❌ Disabled | ✅ Curated |
| **Cost** | Low | High |

## 📝 Quick Usage

### Python

```python
from app.assistant import Assistant
from app.config import ExecutionMode

assistant = Assistant()

# Fast mode (default)
result = assistant.research("What is e^iπ?")

# Full mode (explicit)
result = assistant.research(
    "Analyze quantum entanglement", 
    mode=ExecutionMode.FULL
)
```

### REST API

```bash
# Fast mode
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "Taylor series of sin(x)", "mode": "fast"}'

# Full mode
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "Compare ML optimizers", "mode": "full"}'
```

## 🎚️ Configuration Values

```python
# FAST Mode
faiss_top_k = 15
final_chunks = 3
temperature = 0.1
max_tokens = 2000
max_agent_calls = 5

# FULL Mode
faiss_top_k = 30
final_chunks = 5
temperature = 0.3
max_tokens = 4000
max_agent_calls = 20
```

## 🤖 Agent Execution

```
FAST Mode Flow:
Query → [Planner?] → [Math?] → Writer → Response

FULL Mode Flow:
Query → Planner → Math → Numerical → Data → Literature → Reviewer → Writer → Memory → Response
```

## 🔧 Customization

Edit [`app/config.py`](../app/config.py):

```python
class ModeConfig:
    RAG_CONFIG = {
        ExecutionMode.FAST: {
            "faiss_top_k": 20,  # Increase
            ...
        }
    }
```

## 📚 Full Documentation

See [EXECUTION_MODES.md](EXECUTION_MODES.md) for complete details.

## ✅ Testing

```bash
pytest tests/test_execution_modes.py -v
```
