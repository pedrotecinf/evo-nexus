#!/bin/bash
set -e

echo "[gateway] Starting Hermes (Python/uvicorn) on internal port 9120..."
HERMES_UI_PORT=9120 hermes serve &
HERMES_PID=$!

echo "[gateway] Starting Hermes WS proxy on port 9119..."
cd /app/Hermes && node server.js &

echo "[gateway] Waiting for Hermes to be ready..."
until curl -sf http://localhost:9120/ > /dev/null 2>&1; do
  sleep 1
done
echo "[gateway] Hermes ready (PID $HERMES_PID)."

echo "[gateway] Starting Next.js on port 8080..."
PORT=8080 exec node /app/.next/standalone/server.js
