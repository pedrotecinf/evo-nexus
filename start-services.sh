#!/bin/bash

# Self-discovering launcher for the EvoNexus dashboard, scheduler, and
# terminal-server. Resolves SCRIPT_DIR at runtime (instead of hard-coding
# an absolute path) so the same file works regardless of which user owns
# the install or where it lives.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ensure common user-local bin dirs are visible (openclaude/opencode may live there)
export PATH="/usr/local/bin:/usr/bin:/bin:$HOME/.local/bin:$HOME/.npm-global/bin:$HOME/.opencode/bin"

cd "$SCRIPT_DIR" || exit 1

# Load environment variables
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

# Ensure logs dir exists (fresh installs / reboots after manual cleanup)
mkdir -p "$SCRIPT_DIR/logs"

# Kill existing services (including scheduler)
pkill -f 'terminal-server/bin/server.js' 2>/dev/null || true
pkill -f 'dashboard/backend.*app.py' 2>/dev/null || true
pkill -f 'scheduler.py' 2>/dev/null || true
sleep 1

# Start terminal-server (must run FROM the project root for agent discovery)
nohup node dashboard/terminal-server/bin/server.js > "$SCRIPT_DIR/logs/terminal-server.log" 2>&1 &

# Start scheduler
nohup "$SCRIPT_DIR/.venv/bin/python" scheduler.py > "$SCRIPT_DIR/logs/scheduler.log" 2>&1 &

# Start Flask dashboard
cd dashboard/backend || exit 1
nohup "$SCRIPT_DIR/.venv/bin/python" app.py > "$SCRIPT_DIR/logs/dashboard.log" 2>&1 &
