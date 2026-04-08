# Architecture

## Overview

OpenClaude is a file-based, git-friendly framework. Everything is markdown, YAML, and Python scripts. No database required for the core framework (SQLite is used only by the dashboard).

```
┌─────────────────────────────────────────────────┐
│                    User (human)                  │
│                        │                         │
│                  Claude Code CLI                 │
│                        │                         │
│   ┌────────┬───────┬───────┬────────┬────────┐  │
│   │  Ops   │Finance│Project│Community│ Social │  │
│   │ Agent  │ Agent │ Agent │  Agent  │ Agent  │  │
│   └───┬────┴───┬───┴───┬───┴────┬───┴────┬───┘  │
│       │        │       │        │        │       │
│   ┌───┴────────┴───────┴────────┴────────┴───┐   │
│   │              Skills (126)                 │   │
│   │   fin- / social- / int- / prod- / mkt-   │   │
│   └──────────────────────────────────────────┘   │
│                        │                         │
│   ┌──────────────────────────────────────────┐   │
│   │     Integrations (APIs + MCPs)           │   │
│   │  Gmail / Calendar / Discord / Stripe     │   │
│   └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘

        ┌───────────────────────┐
        │   Scheduler (cron)    │ ─── routines.yaml
        │   ADW Runner          │ ─── 27 Python scripts
        │   JSONL Logs          │ ─── metrics + costs
        └───────────────────────┘

        ┌───────────────────────┐
        │   Dashboard (web)     │
        │   Flask + React       │
        │   SQLite (auth only)  │
        └───────────────────────┘
```

## Components

### Agents (`.claude/agents/`)

Each agent is a markdown file with a system prompt that defines its domain, responsibilities, and behavioral rules. Agents are invoked via slash commands (`/ops`, `/finance`, etc.) or automatically by Claude based on the user's request.

### Skills (`.claude/skills/`)

Skills are domain-specific instructions that teach Claude how to perform specific tasks. Organized by prefix:

| Prefix | Domain | Count |
|--------|--------|-------|
| `evo-` | Development framework | 45 |
| `social-` | Social media | 17 |
| `int-` | Integrations | 13 |
| `fin-` | Financial | 11 |
| `prod-` | Productivity | 9 |
| `mkt-` | Marketing | 8 |
| `gog-` | Google | 6 |
| `obs-` | Obsidian | 5 |
| `discord-` | Discord | 5 |
| `pulse-` | Community | 4 |
| `sage-` | Strategy | 3 |

### Routines (`ADWs/rotinas/`)

Automated workflows that run on a schedule. Each routine is a Python script that invokes Claude Code CLI with a specific agent and skill.

**Runner** (`ADWs/runner.py`) — The execution engine that:
- Invokes Claude Code CLI with `--output-format json`
- Captures token usage and cost
- Logs to JSONL files
- Sends Telegram notifications
- Tracks metrics per routine

**Scheduler** (`scheduler.py`) — Reads `config/routines.yaml` and runs routines at configured times using the `schedule` library.

### Memory

Two-tier persistent memory:

1. **CLAUDE.md** — Hot cache loaded at every session start. Contains key context about the user, company, active projects, and preferences.
2. **memory/** — Global memory directory with typed files (people, projects, glossary, trends). Agents read these as needed.
3. **agent-memory/** — Per-agent memory that persists between sessions.

### Dashboard (`dashboard/`)

Web UI built with:
- **Backend**: Flask + SQLAlchemy + Flask-Login + WebSocket
- **Frontend**: React + TypeScript + Tailwind + Recharts + xterm.js
- **Auth**: SQLite with roles (admin/operator/viewer), customizable permissions, audit log
- **Terminal**: Real browser-based Claude Code terminal via WebSocket PTY

### Integrations

API clients in `.claude/skills/int-*/scripts/` that connect to external services. Each integration has a SKILL.md describing usage and a Python client script.
