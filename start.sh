#!/usr/bin/env bash
set -e

python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 &
API_PID=$!

trap 'kill "$API_PID" 2>/dev/null || true' EXIT

python3 -m streamlit run dashboard.py \
  --server.address 0.0.0.0 \
  --server.port "${PORT:-8501}" \
  --server.headless true \
  --server.enableCORS true \
  --server.enableXsrfProtection true
