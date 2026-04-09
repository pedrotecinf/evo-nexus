# ============================================================
# OpenClaude — Makefile
# ============================================================
# Usage: make <command>
# Docs: ROUTINES.md
#
# Core routines have dedicated targets below.
# Custom routines (ADWs/routines/custom/) are user-specific —
# run them with: make run R=<id>  (e.g. make run R=fin-pulse)
# List all available: make list-routines

# Auto-detect: uv if available, fallback to python3
PYTHON := $(shell command -v uv >/dev/null 2>&1 && echo "uv run python" || echo "python3")
ADW_DIR := ADWs/routines

# Load .env if it exists
ifneq (,$(wildcard .env))
include .env
export
endif

# ── Setup ──────────────────────────────────

docs-build:         ## 📄 Regenerate docs/llms-full.txt and sync to site
	@$(PYTHON) -c "from pathlib import Path; docs=Path('docs'); parts=['# OpenClaude Documentation\n\nComplete reference.\n']; [parts.append(f.read_text()) for f in sorted(docs.rglob('*.md'))]; Path('docs/llms-full.txt').write_text('\n\n---\n\n'.join(parts)); print(f'Generated docs/llms-full.txt ({len(parts)-1} docs)')"
	@rm -rf site/public/docs && cp -r docs/ site/public/docs/ && echo "Synced docs → site/public/docs/"

setup:              ## 🔧 Interactive setup wizard (prerequisites, config, folders)
	$(PYTHON) setup.py

# ── Core Routines (shipped with repo) ─────

morning:            ## ☀️  Morning briefing — agenda, emails, tasks (@clawdia)
	$(PYTHON) $(ADW_DIR)/good_morning.py

eod:                ## 🌙 End of day consolidation — memory, logs, learnings (@clawdia)
	$(PYTHON) $(ADW_DIR)/end_of_day.py

memory:             ## 🧠 Consolidate memory (@clawdia)
	$(PYTHON) $(ADW_DIR)/memory_sync.py

memory-lint:        ## 🔍 Memory health check — contradictions, gaps, stale data (@clawdia)
	$(PYTHON) $(ADW_DIR)/memory_lint.py

weekly:             ## 📊 Full weekly review (@clawdia)
	$(PYTHON) $(ADW_DIR)/weekly_review.py

# ── Dynamic Routine Runner ────────────────
# Run any routine (core or custom) by its ID.
# IDs are derived from script names. Use `make list-routines` to see all.
# Examples:
#   make run R=morning
#   make run R=fin-pulse
#   make run R=community-week

run:                ## ▶️  Run any routine: make run R=<id>  (e.g. make run R=fin-pulse)
	@$(PYTHON) -c "\
	import sys; sys.path.insert(0, 'dashboard/backend'); \
	from routes._helpers import get_routine_scripts; \
	scripts = get_routine_scripts(); \
	r = '$(R)'; \
	s = scripts.get(r) or next((v for k,v in scripts.items() if r.replace('-','_') in v), None); \
	print(f'Running: {s}') if s else (print(f'Unknown routine: {r}. Available: {\" \".join(sorted(scripts.keys()))}'), exit(1)); \
	" && $(PYTHON) $(ADW_DIR)/$$($(PYTHON) -c "\
	import sys; sys.path.insert(0, 'dashboard/backend'); \
	from routes._helpers import get_routine_scripts; \
	scripts = get_routine_scripts(); \
	r = '$(R)'; \
	s = scripts.get(r) or next((v for k,v in scripts.items() if r.replace('-','_') in v), ''); \
	print(s); \
	")

list-routines:      ## 📋 List all available routines (dynamic from scripts)
	@$(PYTHON) -c "\
	import sys; sys.path.insert(0, 'dashboard/backend'); \
	from routes._helpers import discover_routines; \
	routines = discover_routines(); \
	[print(f'  \033[36m{k:20s}\033[0m {v[\"name\"]:30s} @{v[\"agent\"]:<10s} {v[\"script\"]}') for k,v in sorted(routines.items())]; \
	print(f'\n  {len(routines)} routines available — run with: make run R=<id>'); \
	"

# ── Combos ────────────────────────────────

daily:              ## ☀️  Combo: sync meetings + review todoist
	@$(PYTHON) $(ADW_DIR)/custom/sync_meetings.py 2>/dev/null; $(PYTHON) $(ADW_DIR)/custom/review_todoist.py 2>/dev/null; echo "Daily combo done"

# ── Servers ───────────────────────────────

scheduler:          ## ⏰ Start routine scheduler (runs in background)
	$(PYTHON) scheduler.py

dashboard-app:      ## 🖥️  Start Dashboard App (React + Flask, localhost:8080)
	cd dashboard/frontend && npm run build && cd ../backend && $(PYTHON) app.py

telegram:           ## 📨 Start Telegram bot in background (screen)
	@if screen -list | grep -q '\.telegram'; then \
		echo "⚠ Telegram bot is already running. Use 'make telegram-stop' first or 'make telegram-attach' to connect."; \
	else \
		screen -dmS telegram claude --channels plugin:telegram@claude-plugins-official --dangerously-skip-permissions; \
		echo "✅ Telegram bot running in background (screen: telegram)"; \
		echo "📺 Ver: screen -r telegram"; \
		echo "🛑 Parar: make telegram-stop"; \
	fi

telegram-stop:      ## 🛑 Stop the Telegram bot
	@screen -S telegram -X quit 2>/dev/null && echo "✅ Telegram bot stopped" || echo "⚠ Was not running"

telegram-attach:    ## 📺 Connect to Telegram terminal (Ctrl+A D to detach)
	@screen -r telegram

# ── Utilities ─────────────────────────────

logs:               ## 📝 Show latest logs (JSONL)
	@tail -20 ADWs/logs/$$(ls -t ADWs/logs/*.jsonl 2>/dev/null | head -1) 2>/dev/null || echo "No logs yet."

logs-detail:        ## 📝 List detailed logs
	@ls -lt ADWs/logs/detail/ 2>/dev/null | head -11 || echo "No logs yet."

logs-tail:          ## 📝 Show latest full log
	@cat ADWs/logs/detail/$$(ls -t ADWs/logs/detail/ 2>/dev/null | head -1) 2>/dev/null || echo "No logs yet."

metrics:            ## 📈 Show accumulated metrics per routine (tokens + cost)
	@python3 -c "\
	import json; d=json.load(open('ADWs/logs/metrics.json'));\
	total_runs=0; total_cost=0; total_tok=0;\
	[(\
	  print(f'  {k:22s} runs:{v[\"runs\"]:3d}  ok:{v[\"success_rate\"]:5.1f}%  avg:{v[\"avg_seconds\"]:5.0f}s  cost:\$${v.get(\"total_cost_usd\",0):7.2f}  avg:\$${v.get(\"avg_cost_usd\",0):.2f}  tok:{v.get(\"total_input_tokens\",0)+v.get(\"total_output_tokens\",0):>9,}  last:{v[\"last_run\"][:16]}'),\
	  total_runs:=total_runs+v['runs'],\
	  total_cost:=total_cost+v.get('total_cost_usd',0),\
	  total_tok:=total_tok+v.get('total_input_tokens',0)+v.get('total_output_tokens',0)\
	) for k,v in sorted(d.items())];\
	print(f'\n  {\"TOTAL\":22s} runs:{total_runs:3d}  {\" \":18s}  cost:\$${total_cost:7.2f}  {\" \":10s}  tok:{total_tok:>9,}')\
	" 2>/dev/null || echo "No metrics yet."

clean-logs:         ## 🗑️  Remove logs older than 30 days
	@find ADWs/logs/ -name "*.log" -mtime +30 -delete 2>/dev/null; find ADWs/logs/ -name "*.jsonl" -mtime +30 -delete 2>/dev/null; echo "Old logs removed."

# ── Docker (VPS) ──────────────────────────

docker-dashboard:   ## 🐳 Start dashboard in Docker (port 8080)
	docker compose up -d dashboard

docker-telegram:    ## 🐳 Start Telegram bot in Docker
	docker compose up -d telegram

docker-down:        ## 🐳 Stop all containers
	docker compose down

docker-logs:        ## 🐳 Container logs
	docker compose logs -f --tail=50

docker-run:         ## 🐳 Run routine manually (ex: make docker-run ADW=good_morning.py)
	docker compose run --rm runner ADWs/routines/$(ADW)

docker-build:       ## 🐳 Build the image
	docker compose build

help:               ## 📖 Show this help
	@grep -E '^[a-zA-Z_-]+:.*##' Makefile | sort | awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

.PHONY: morning eod memory memory-lint weekly run list-routines daily scheduler dashboard-app telegram telegram-stop telegram-attach logs logs-detail logs-tail metrics clean-logs docker-dashboard docker-telegram docker-down docker-logs docker-run docker-build help docs-build setup
.DEFAULT_GOAL := help
