# Teslas.ai API Dockerfile (FastAPI only)
# Base: slim Python 3.11 for smaller footprint
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_SYSTEM_PYTHON=1

# Install system deps required by faiss, chromadb, and scientific stack
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    wget \
    libgomp1 \
    libopenblas-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast, reproducible installs
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy project metadata first for better layer caching
COPY pyproject.toml /app/
COPY README.md /app/
COPY uv.lock /app/

# Sync dependencies
RUN uv sync --frozen --no-editable

# Copy source
COPY app /app/app
COPY scripts /app/scripts
COPY docker/entrypoint.sh /app/docker/entrypoint.sh

# Create data directories and make entrypoint executable
RUN mkdir -p /app/data /app/chroma && chmod +x /app/docker/entrypoint.sh

# Environment defaults (overridable via compose)
ENV API_HOST=0.0.0.0 \
    API_PORT=8000 \
    API_RELOAD=false \
    OLLAMA_BASE_URL=http://ollama:11434

EXPOSE 8000

# Run with single worker, no reload
ENTRYPOINT ["/app/docker/entrypoint.sh"]
