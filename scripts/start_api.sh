#!/usr/bin/env bash

set -euo pipefail

# Start FastAPI (Uvicorn) for the project
# Usage: ./scripts/start_api.sh [port]

PORT="${1:-8000}"

# Prefer a known project venv if present (workspace temp venv), else local venv, else system python
if [ -x "/tmp/cv-ai-venv/bin/python" ]; then
  PY="/tmp/cv-ai-venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  PY=python
fi

echo "Starting FastAPI on port ${PORT} using ${PY}..."
echo "Docs:       http://localhost:${PORT}/api/docs"
echo "Health:     http://localhost:${PORT}/api/v1/health"

exec "${PY}" -m uvicorn src.api.main:app --host 0.0.0.0 --port "${PORT}" --reload
