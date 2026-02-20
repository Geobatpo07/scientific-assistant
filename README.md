# 🧪 Scientific Assistant - Multi-Agent Research System

> **Local-first multi-agent scientific assistant for rigorous research in mathematics, numerical methods, and data science.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![LangChain](https://img.shields.io/badge/LangChain-Powered-orange.svg)](https://www.langchain.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-purple.svg)](https://ollama.ai)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Quick Installation](#-quick-installation)
- [Usage](#-usage)
- [Architecture](#-architecture)
- [Documentation](#-documentation)
- [Development](#-development)

---

## 🎯 Overview

**Scientific Assistant** is a **local-first** multi-agent system designed for rigorous scientific research. It combines 8 specialized agents with RAG (Retrieval-Augmented Generation) to deliver precise, reproducible, and citation-backed analyses.

### ✨ Why Scientific Assistant?

- 🔒 **100% Local** - Your data stays private (Ollama + ChromaDB)
- 🎯 **Specialized** - Built for rigorous scientific workflows
- 🤖 **Multi-agent** - 8 expert agents collaborate in synergy
- 📚 **Advanced RAG** - Hybrid vector + keyword retrieval
- 🔬 **Reproducible** - Generates executable Python code
- 📝 **Documentation-ready** - Automatic LaTeX and APA/BibTeX citations

### 🤖 The 8 Specialized Agents

| Agent | Role | Expertise |
|-------|------|-----------|
| **Planner** | Orchestration | Research task decomposition |
| **Mathematician** | Symbolic analysis | Mathematical proofs, theorems |
| **Numerical** | Simulation | Numerical methods, convergence |
| **Data Scientist** | Statistics | ML, data analysis, uncertainty |
| **Literature** | Retrieval | RAG + web search, citations |
| **Reviewer** | Quality | Verification, error detection |
| **Writer** | Writing | Academic writing, LaTeX |
| **Memory** | Knowledge | Knowledge base management |

---

## 🚀 Features

### 💡 Core Capabilities

- ✅ **Symbolic mathematical analysis** (SymPy)
- ✅ **Numerical simulations** (NumPy, SciPy, scikit-learn)
- ✅ **Document ingestion** (PDF, TXT, Markdown)
- ✅ **Semantic retrieval** with embeddings
- ✅ **Executable Python code generation**
- ✅ **Automatic citations** (APA, BibTeX)
- ✅ **LaTeX export** for publications

### 🏗️ Technical Stack

- **LLM**: Ollama (mistral, llama2, neural-chat...)
- **Orchestration**: LangChain + LangGraph
- **Vector DB**: ChromaDB + FAISS (hybrid)
- **Embeddings**: sentence-transformers
- **API**: FastAPI
- **UI**: Streamlit
- **Logging**: Loguru

---

## ⚡ Quick Installation

### Prerequisites

- **Python 3.11+**
- **[Ollama](https://ollama.ai)** installed and running
- **[uv](https://github.com/astral-sh/uv)** (fast Python package manager)

### Install in 3 Steps

#### 1️⃣ Install uv and clone the project

```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone https://github.com/Geobatpo07/scientific-assistant.git
cd scientific-assistant
```

#### 2️⃣ Install dependencies

```bash
# Sync environment (very fast with uv)
uv sync

# Download an Ollama model
ollama pull mistral
```

#### 3️⃣ Launch the application

```bash
# Method 1: All-in-one script (recommended)
uv run python scripts/run_local.py

# Method 2: PowerShell
.\Makefile.ps1 run

# Method 3: Docker
docker compose up -d --build
```

**Access:**
- 🌐 Web UI: http://localhost:8501
- 📡 API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs

### 🎛️ Configuration (Optional)

```bash
# Copy sample environment file
cp .env.example .env

# Customize if needed (defaults are usable)
# - LLM model
# - Chunk size
# - Log level
# etc.
```

---

## 💻 Usage

### Web Interface (Streamlit)

1. Open http://localhost:8501
2. Enter your research question
3. Select the agents you want to use
4. Click **Run Research**
5. Explore outputs in the result tabs

### REST API

```bash
# Run a research workflow
curl -X POST "http://localhost:8000/api/research" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze stability of explicit Euler method",
    "agents": ["planner", "mathematician", "numerical", "reviewer"]
  }'

# Search the knowledge base
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "finite difference methods",
    "search_type": "scientific",
    "max_results": 5
  }'

# Check system health
curl http://localhost:8000/api/health
```

### Python API

```python
from app.agents.graph import create_orchestrator

orchestrator = create_orchestrator()
context = orchestrator.run_research(
    "What are the stability conditions for the Euler method?"
)

print(context.final_summary)
print(context.mathematical_insights)
print(context.numerical_results)
```

---

## 📚 Knowledge Base Management

### Document Ingestion

```bash
# Ingest a PDF
uv run python scripts/ingest_docs.py data/papers/my_article.pdf

# Ingest a full folder
uv run python scripts/ingest_docs.py data/papers/

# Reset the database (warning!)
uv run python scripts/reset_db.py --confirm
```

**Supported formats**: PDF, TXT, Markdown

**Pipeline:**
1. Document loading
2. Chunking (with overlap)
3. Embedding generation
4. ChromaDB storage
5. FAISS indexing for fast retrieval

---

## 🐳 Docker (Recommended)

```bash
# Build and start
docker compose up -d --build

# View logs
docker compose logs -f

# Stop services
docker compose down
```

---

## 📐 Architecture

### Project Structure

```text
scientific-assistant/
├── 📁 app/                     # Main source code
│   ├── agents/                 # 🤖 Multi-agent system
│   ├── vectorstore/            # 🗄️ ChromaDB + FAISS + LangChain-Chroma
│   ├── llm/                    # 🧠 Ollama + Embeddings integration
│   ├── rag/                    # 📚 RAG chains + citations
│   ├── tools/                  # 🔧 Scientific tools
│   ├── ingestion/              # 📥 Document processing
│   ├── api/                    # 🌐 FastAPI REST
│   ├── ui/                     # 🎨 Streamlit interface
│   └── utils/                  # 📝 Logging (Loguru), helpers
├── 📁 docs/                    # 📖 Full documentation
├── 📁 examples/                # 💡 Code examples
├── 📁 scripts/                 # 🛠️ Utility scripts
├── 📁 tests/                   # 🧪 Unit tests
├── 📁 data/                    # 💾 Ingested documents
├── 📁 chroma/                  # 🗃️ ChromaDB persistence
├── 📄 pyproject.toml           # 📦 Dependencies (uv)
├── 🐳 docker-compose.yml       # Docker orchestration
└── 📄 README.md
```

### Processing Flow

```text
Question → PlannerAgent → Specialized routing
                ↓
    ┌───────────┼───────────┐
    ↓           ↓           ↓
MathAgent  NumericalAgent  DataScientist
    ↓           ↓           ↓
    └───────────┼───────────┘
                ↓
         ReviewerAgent
                ↓
          WriterAgent
                ↓
          MemoryAgent
                ↓
           Final result
```

### Hybrid RAG Stack

- **ChromaDB**: Persistent storage + rich metadata
- **FAISS**: Fast top-K retrieval (ID-level)
- **LangChain-Chroma**: Integration with LangChain ecosystem
- **Reranking**: Cosine similarity + keyword boost
- **Fallback**: If FAISS is empty, use ChromaDB only

---

## 📚 Documentation

📖 **Full documentation is available in [docs/](docs/)**

### Main Guides

- 🚀 **[Getting Started](docs/GETTING_STARTED.md)** - Installation and first steps
- 🔗 **[LangChain-Chroma](docs/GUIDE_LANGCHAIN_CHROMA.md)** - Vector store integration
- 📝 **[Loguru Logging](docs/LOGURU_SUMMARY.md)** - Logging system
- 🎨 **[Design Guide](docs/DESIGN_GUIDE.md)** - UI and design references
- 📑 **[Documentation Index](docs/README.md)** - Full navigation

### Code Examples

- `examples/example_5_langchain_chroma.py` - ChromaDB usage
- `examples/example_6_scientific_rag.py` - Scientific RAG workflow
- `examples/example_7_loguru_features.py` - Advanced logging

---

## 🛠️ Development

### Tests

```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest --cov=app tests/

# Run a specific test file
uv run pytest tests/test_agents.py -v
```

### Code Quality

```bash
# Formatter (Black)
black app/ tests/

# Sort imports
isort app/ tests/

# Type checking
mypy app/

# Linter
ruff check app/
```

### Contributing

1. Fork the project
2. Create a branch (`git checkout -b feature/amazing`)
3. Commit (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 🐛 Troubleshooting

### Common Issues

**Ollama not found**
```bash
# Install from https://ollama.ai
ollama serve  # Run in a separate terminal
```

**ChromaDB errors**
```bash
# Reset the database
uv run python scripts/reset_db.py --confirm
```

**Memory issues**
- Reduce `CHUNK_SIZE` in `.env`
- Use a smaller model (`phi`, `mistral` instead of `llama2-70b`)
- Lower `TOP_K_RETRIEVAL`

**Debug logs**
```bash
# Logs are stored in logs/
tail -f logs/scientific_assistant_*.log
```

### ⚙️ Performance Optimization

- **Models**: Prefer `mistral` or `phi` for fast iteration
- **Temperature**: Keep low (`0.3`) for reproducibility
- **Retrieval**: Tune `TOP_K_RETRIEVAL` (quality vs speed)
- **Chunking**: Optimize `CHUNK_SIZE` and `CHUNK_OVERLAP`
- **Docker**: One worker by default; scale carefully

---

## 📜 License

MIT License - see [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

Built with:
- **[LangChain](https://www.langchain.com/)** - Multi-agent orchestration
- **[Ollama](https://ollama.ai)** - Local LLM inference
- **[ChromaDB](https://www.trychroma.com/)** - Vector database
- **[Loguru](https://github.com/Delgan/loguru)** - Modern logging
- **[Streamlit](https://streamlit.io/)** - Rapid UI
- **[FastAPI](https://fastapi.tiangolo.com/)** - High-performance API

Inspired by LangChain and LlamaIndex.

---

<div align="center">

**Made with ⚡ for rigorous scientific research**

[Documentation](docs/) • [Examples](examples/) • [Issues](https://github.com/Geobatpo07/scientific-assistant/issues)

</div>
