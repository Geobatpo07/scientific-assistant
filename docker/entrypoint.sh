#!/usr/bin/env bash
set -euo pipefail

# Simple entrypoint to run the API with a single worker, no reload

HOST="${API_HOST:-0.0.0.0}"
PORT="${API_PORT:-8000}"

echo "Starting Teslas.ai API on ${HOST}:${PORT} (1 worker, no reload)"
exec /app/.venv/bin/uvicorn app.main:app \
  --host "${HOST}" \
  --port "${PORT}" \
  --workers 1
