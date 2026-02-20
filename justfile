# Teslas.ai - Justfile (modern task runner)
# Install just: https://github.com/casey/just
# Usage: just <command>

# Default recipe
default:
    @just --list

# Install dependencies with uv
install:
    @echo "📦 Installing dependencies with uv..."
    uv pip install -e .

# Run full application (API + UI)
run:
    @echo "🚀 Starting Teslas.ai..."
    uv run python scripts/run_local.py

# Run API server only
api:
    @echo "🔵 Starting API server..."
    uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Run Streamlit UI only
ui:
    @echo "🟢 Starting UI..."
    uv run streamlit run app/ui/streamlit_app.py --theme.base dark

# Run tests
test:
    @echo "🧪 Running tests..."
    uv run pytest tests/ -v

# Run tests with coverage
test-cov:
    @echo "🧪 Running tests with coverage..."
    uv run pytest tests/ --cov=app --cov-report=html --cov-report=term

# Ingest documents (provide path as argument)
ingest path:
    @echo "📥 Ingesting documents from {{path}}..."
    uv run python scripts/ingest_docs.py {{path}}

# Reset knowledge base
reset:
    @echo "🗑️ Resetting knowledge base..."
    uv run python scripts/reset_db.py

# Format code
format:
    @echo "🎨 Formatting code..."
    uv run black app/ tests/ scripts/
    uv run isort app/ tests/ scripts/

# Lint code
lint:
    @echo "🔍 Linting code..."
    uv run ruff check app/ tests/ scripts/

# Type check
typecheck:
    @echo "📝 Type checking..."
    uv run mypy app/

# Clean project
clean:
    @echo "🧹 Cleaning project..."
    rm -rf .venv __pycache__ .pytest_cache chroma logs/
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    @echo "✨ Project cleaned!"

# Development setup (install + check Ollama)
dev-setup:
    @echo "🛠️ Setting up development environment..."
    uv pip install -e ".[dev]"
    @echo "✅ Checking Ollama..."
    @ollama pull mistral || echo "⚠️ Please install Ollama and run: ollama pull mistral"
    @echo "✨ Dev setup complete!"

# Pull required models
models:
    @echo "📥 Pulling required models..."
    ollama pull mistral
    ollama pull neural-chat
    @echo "✅ Models ready!"

# Show logs
logs:
    @tail -f logs/teslas_ai.log

# Open API docs
docs-api:
    @echo "📖 Opening API docs..."
    @open http://localhost:8000/docs || start http://localhost:8000/docs

# Open UI
open-ui:
    @echo "🌐 Opening UI..."
    @open http://localhost:8501 || start http://localhost:8501
