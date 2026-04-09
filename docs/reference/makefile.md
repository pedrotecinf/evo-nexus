# Makefile Reference

All available `make` commands. Run `make help` to see this list in your terminal.

## Setup

```bash
make setup           # Interactive setup wizard (runs setup.py)
                     # Checks prerequisites (Claude Code, uv, Node.js)
                     # Installs Python deps via `uv sync`
                     # Creates config files, .env, CLAUDE.md, workspace folders
```

## Dashboard

```bash
make dashboard-app   # Start the web dashboard (React + Flask) on localhost:8080
                     # Builds frontend, then starts the Flask backend
```

## Core Routines

These ship with the repo and run the essential daily loop:

```bash
make morning         # Morning briefing -- agenda, emails, tasks (@clawdia)
make eod             # End of day -- memory, logs, learnings (@clawdia)
make memory          # Memory sync -- consolidate agent memory (@clawdia)
make memory-lint     # Memory health check -- contradictions, gaps, stale data (@clawdia)
make weekly          # Full weekly review (@clawdia)
```

## Dynamic Routine Runner

Custom routines (user-specific, in `ADWs/routines/custom/`) are run via the dynamic runner. No hardcoded Makefile targets needed -- routines are discovered automatically from script files.

```bash
make run R=fin-pulse        # Financial pulse (@flux)
make run R=community        # Daily community pulse (@pulse)
make run R=licensing-month  # Monthly licensing report (@atlas)
make run R=social           # Social analytics (@pixel)
make run R=strategy         # Strategy digest (@sage)

make list-routines          # List all available routines (core + custom)
```

Any script in `ADWs/routines/` or `ADWs/routines/custom/` is automatically discoverable. The routine ID is derived from the script name (e.g., `financial_pulse.py` becomes `fin-pulse`).

## Combos

```bash
make daily           # Runs: sync + review (sync meetings then organize tasks)
```

## Servers

```bash
make scheduler       # Start the routine scheduler (runs in foreground)
make telegram        # Start Telegram bot in background (screen session)
make telegram-stop   # Stop the Telegram bot
make telegram-attach # Attach to Telegram terminal (Ctrl+A D to detach)
```

## Observability

```bash
make logs            # Show latest JSONL log entries
make logs-detail     # List detailed log files
make logs-tail       # Show the latest full detailed log
make metrics         # Per-routine metrics table (runs, cost, tokens, success rate)
make clean-logs      # Remove logs older than 30 days
```

## Docker (VPS Deployment)

```bash
make docker-dashboard  # Start dashboard in Docker (port 8080)
make docker-telegram   # Start Telegram bot in Docker
make docker-down       # Stop all containers
make docker-logs       # Show container logs (follow mode)
make docker-run ADW=good_morning.py  # Run a specific routine in Docker
make docker-build      # Build the Docker image
```

## Help

```bash
make help            # Show all available commands with descriptions
```
