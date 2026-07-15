#!/bin/bash
set -e

# Configure Hermes auth if credentials are provided
HERMES_ADMIN_USER="${EVONEXUS_HERMES_USERNAME:-}"
HERMES_ADMIN_PASS="${EVONEXUS_HERMES_PASSWORD:-}"

if [ -n "$HERMES_ADMIN_USER" ] && [ -n "$HERMES_ADMIN_PASS" ]; then
    echo "[gateway] Configuring Hermes Basic Auth..."

    # Generate bcrypt hash using uv venv
    _pw_hash=$(uv run python -c "
import bcrypt
print(bcrypt.hashpw('$HERMES_ADMIN_PASS'.encode(), bcrypt.gensalt()).decode())
")

    # Write config.yaml with auth credentials
    mkdir -p ~/.config/hermes
    cat > ~/.config/hermes/config.yaml << EOF
dashboard:
  basic_auth:
    username: "$HERMES_ADMIN_USER"
    password_hash: "$_pw_hash"
EOF
    chmod 600 ~/.config/hermes/config.yaml
    echo "[gateway] Basic Auth configured for user: $HERMES_ADMIN_USER"

    # Bind to 0.0.0.0 when auth is enabled
    export HERMES_DASHBOARD_HOST="0.0.0.0"
else
    echo "[gateway] No auth credentials provided, running without auth"
    export HERMES_DASHBOARD_HOST="127.0.0.1"
fi

echo "[gateway] Starting Hermes (Python/uvicorn) on internal port 9120 (bind: ${HERMES_DASHBOARD_HOST})..."
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
