# ============================================================
# Teslas.ai API – FastAPI (CPU ONLY, PRODUCTION-GRADE)
# ============================================================

FROM python:3.11-slim

# ------------------------------------------------------------
# Global environment (Python + uv)
# ------------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_HTTP_TIMEOUT=1200 \
    PIP_NO_CACHE_DIR=1 \
    UV_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cpu

# ------------------------------------------------------------
# HARD BLOCK CUDA / GPU (CRITICAL)
# ------------------------------------------------------------
ENV CUDA_VISIBLE_DEVICES="" \
    TORCH_CUDA_ARCH_LIST="" \
    FORCE_CUDA=0 \
    NVIDIA_VISIBLE_DEVICES=none

# ------------------------------------------------------------
# Block transformers GPU backends (CRITICAL)
# ------------------------------------------------------------
ENV TRANSFORMERS_NO_TORCHVISION=1 \
    TRANSFORMERS_NO_TF=1 \
    TRANSFORMERS_NO_FLAX=1

# ------------------------------------------------------------
# System dependencies (CPU-only scientific stack)
# ------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    libgomp1 \
    libopenblas0 \
    libgl1 \
    libglib2.0-0 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Install uv
# ------------------------------------------------------------
RUN pip install --no-cache-dir uv

WORKDIR /app

# ------------------------------------------------------------
# Copy dependency metadata first (Docker cache friendly)
# ------------------------------------------------------------
COPY pyproject.toml uv.lock README.md /app/

# ------------------------------------------------------------
# Install Python dependencies (CPU-only, locked)
# ------------------------------------------------------------
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen \
    && uv pip install "numpy<2" \
    && uv pip install --no-deps "torch==2.2.2+cpu" --index-url https://download.pytorch.org/whl/cpu

# ------------------------------------------------------------
# Copy application code
# ------------------------------------------------------------
COPY app /app/app
COPY scripts /app/scripts
COPY docker/entrypoint.sh /app/docker/entrypoint.sh

# ------------------------------------------------------------
# Prepare runtime directories
# ------------------------------------------------------------
RUN mkdir -p /app/data /app/chroma \
    && chmod +x /app/docker/entrypoint.sh

# ------------------------------------------------------------
# Runtime environment defaults
# ------------------------------------------------------------
ENV API_HOST=0.0.0.0 \
    API_PORT=8000 \
    API_RELOAD=false \
    OLLAMA_BASE_URL=http://ollama:11434

EXPOSE 8000

ENTRYPOINT ["/app/docker/entrypoint.sh"]
