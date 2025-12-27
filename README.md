# Teslas.ai - Multi-Agent Scientific Assistant 🚀🤖

A **local-first, multi-agent AI system** for rigorous scientific research in mathematics, numerical methods, and data science. Designed for researchers who demand accuracy and reproducibility.

## 🤖 Features

### Multi-Agent Orchestration
Teslas.ai leverages **8 specialized agents** working in concert:

1. **PlannerAgent** - Decompose research questions into structured tasks
2. **MathematicalAnalystAgent** - Rigorous symbolic mathematics & proofs
3. **NumericalSimulationAgent** - Numerical methods, discretization, convergence analysis
4. **DataScientistAgent** - Statistical analysis, ML, uncertainty quantification
5. **LiteratureResearchAgent** - Hybrid RAG + web search with proper citations
6. **ReviewerAgent** - Quality control, error detection, rigor verification
7. **ScientificWriterAgent** - Academic writing, LaTeX generation
8. **MemoryAgent** - Knowledge management and persistent learning

### 💾 Local-First Design
- **Ollama** for local LLMs (mistral, neural-chat, etc.)
- **ChromaDB** for semantic search without external APIs
- **DuckDuckGo** for privacy-preserving web search
- All computation runs on your machine

### 📊 Comprehensive Analysis
- Symbolic & numerical computation (SymPy, NumPy, SciPy)
- Scientific document ingestion (PDF, TXT, Markdown)
- Semantic search with embeddings (sentence-transformers)
- Automated citation management (APA, BibTeX)
- LaTeX equation generation
- Reproducible code execution

### 🎯 Production-Ready
- FastAPI REST API
- Streamlit web UI
- Structured logging
- Error handling & recovery
- Extensible architecture

## 🚀 Installation

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.ai) running locally
- [uv](https://github.com/astral-sh/uv) package manager (fast pip replacement)

### Quick Start

```bash
# Install uv (if not already installed)
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone https://github.com/Geobatpo07/scientific-assistant.git
cd scientific-assistant

# Install dependencies with uv (fast!)
uv pip install -e .

# Pull an Ollama model
ollama pull mistral  # or neural-chat, dolphin-mixtral, etc.

# Start Ollama server (in separate terminal)
ollama serve

# Launch Teslas.ai
uv run python scripts/run_local.py
# Or use the PowerShell helper:
.\Makefile.ps1 run
```

### Environment Setup

```bash
# Copy and customize environment file
cp .env.example .env

# Edit .env if needed (defaults work for local setup)
```

### Running Teslas.ai

**Option 1: Using uv (recommended)**
```bash
# Full application (API + UI)
uv run python scripts/run_local.py

# Or with PowerShell helper
.\Makefile.ps1 run
```

**Option 2: Individual components**

Terminal 1 - Start Ollama:
```bash
ollama serve
```

Terminal 2 - Start API:
```bash
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
# Or: .\Makefile.ps1 api
```

Terminal 3 - Start UI:
```bash
uv run streamlit run app/ui/streamlit_app.py --theme.base dark
# Or: .\Makefile.ps1 ui
```

Then open:
- **API Documentation**: http://localhost:8000/docs
- **UI**: http://localhost:8501

### 🐳 Run with Docker (recommended for reproducibility)

This runs Teslas.ai API and Ollama in separate containers with persistent volumes:

```bash
# Build and start
docker compose up -d --build

# Tail logs
docker compose logs -f api

# Stop
docker compose down
```

Endpoints:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

Notes:
- The API container talks to Ollama at `http://ollama:11434` over the Docker network.
- ChromaDB data persists in the `chroma_data` volume.
- Embeddings and other project data persist in the `data_volume`.
- FAISS is rebuilt at startup from embeddings, ensuring consistency without duplicating storage.

### Available Commands (PowerShell)

```powershell
.\Makefile.ps1 install    # Install dependencies
.\Makefile.ps1 run        # Start full application
.\Makefile.ps1 api        # Start API only
.\Makefile.ps1 ui         # Start UI only
.\Makefile.ps1 test       # Run tests
.\Makefile.ps1 ingest     # Ingest documents
.\Makefile.ps1 reset      # Reset knowledge base
.\Makefile.ps1 clean      # Clean project
```

## 📖 Usage Examples

### Via Python API

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

### Via REST API

```bash
curl -X POST "http://localhost:8000/api/research" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Solve the heat equation using finite differences",
    "agents": ["planner", "mathematician", "numerical", "reviewer"]
  }'
```

### Via Web UI (Streamlit)
1. Open http://localhost:8501
2. Enter your research question
3. Select desired agents
4. Click "Run Research"
5. Explore results in tabs

## 📥 Document Ingestion

Build your personal knowledge base:

```bash
# Ingest a single PDF
python scripts/ingest_docs.py data/papers/important_paper.pdf

# Ingest entire directory
python scripts/ingest_docs.py data/papers/

# Reset knowledge base (careful!)
python scripts/reset_db.py --confirm
```

## 🏗️ Project Structure

```
scientific-assistant/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── llm/                 # LLM integration
│   ├── agents/              # Multi-agent system
│   ├── ingestion/           # Document processing
│   ├── vectorstore/         # ChromaDB + FAISS hybrid store
│   ├── rag/                 # RAG chains
│   ├── tools/               # Scientific tools
│   ├── api/                 # REST API
│   ├── ui/                  # Streamlit UI
│   └── utils/               # Logging, helpers
├── data/                    # Document storage
├── chroma/                  # Vector DB persistence
└── docker/
  └── entrypoint.sh        # API entrypoint
├── scripts/                 # Utility scripts
├── tests/                   # Unit tests
├── notebooks/               # Experiments
├── pyproject.toml          # Dependencies
├── .env.example            # Configuration template
└── README.md
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Specific test
pytest tests/test_agents.py -v
```

## 🛠️ Development

### Code Style
- Black formatting
- isort imports
- mypy type checking
- ruff linting

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Type checking
mypy app/

# Lint
ruff check app/
```

## 🐛 Troubleshooting

### Ollama not found
```bash
# Install Ollama from https://ollama.ai
ollama serve  # Run in separate terminal
```

### ChromaDB errors
```bash
# Reset database
python scripts/reset_db.py --confirm
```

### Memory issues
- Reduce `CHUNK_SIZE` in `.env`
- Use smaller LLM model (phi, mistral vs llama2-70b)
- Limit `TOP_K_RETRIEVAL`

## 📜 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

- Inspired by LangChain and LLamaIndex
- Built with Ollama for local inference
- ChromaDB for vector operations
- Streamlit for rapid UI development

---

**Made with ⚡ for rigorous scientific research**

Questions? Open an issue on GitHub!

---

## 📐 Architecture Overview

- **FastAPI**: Serves the REST API for research requests and tools.
- **LangChain + (LangGraph-inspired)**: Orchestrates agents with shared state and deterministic prompts.
- **ChatOllama (LangChain)**: Single cached LLM client shared across agents. No direct HTTP calls.
- **Hybrid Vector Store**:
  - FAISS: Fast top-K candidate retrieval using embeddings (IDs only).
  - ChromaDB: Persistent storage of documents + metadata.
  - Rerank: Cosine similarity via sentence-transformers, optional keyword boost.
  - Fallback: If FAISS is empty/unavailable, revert to pure Chroma search.

Rationale: ChromaDB excels at persistence and metadata-rich retrieval. FAISS accelerates candidate selection. Combining both yields speed and quality without duplicate storage.

---

## 🔌 Example Requests (Postman/curl)

Research:
```bash
curl -X POST "http://localhost:8000/api/research" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze stability of explicit Euler for dy/dt = -ky",
    "agents": ["planner", "mathematician", "numerical", "reviewer", "writer", "memory"]
  }'
```

Search:
```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "finite difference heat equation stability", "search_type": "scientific", "max_results": 5}'
```

Health:
```bash
curl http://localhost:8000/api/health
```

---

## ⚙️ Performance Considerations

- Use smaller Ollama models for faster iteration (e.g., `mistral`, `phi`).
- Keep temperature low (default 0.3) for deterministic results.
- Adjust `TOP_K_RETRIEVAL` and rerank thresholds for throughput vs quality.
- Chunking: Tune `CHUNK_SIZE` and `CHUNK_OVERLAP` in settings.
- Docker: API runs with a single worker; scale cautiously to avoid memory contention.