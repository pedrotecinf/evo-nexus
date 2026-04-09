# OpenClaude — Routines & Scheduled Tasks

Routines are automated workflows that run on a schedule via the ADW Runner.

## Core vs Custom

| Type | Location | Tracked | Description |
|------|----------|---------|-------------|
| **Core** | `ADWs/routines/` | Yes | Essential system routines shipped with the repo |
| **Custom** | `ADWs/routines/custom/` | No (gitignored) | User-created, workspace-specific routines |

## Core Routines

| Routine | Script | Agent | Schedule |
|---------|--------|-------|----------|
| Good Morning | `good_morning.py` | @clawdia | Daily 07:00 |
| End of Day | `end_of_day.py` | @clawdia | Daily 21:00 |
| Memory Sync | `memory_sync.py` | @clawdia | Daily 21:15 |
| Weekly Review | `weekly_review.py` | @clawdia | Friday 08:00 |
| Memory Lint | `memory_lint.py` | @clawdia | Sunday 09:00 |

> **Memory Sync** follows the LLM Wiki pattern: extracts knowledge from daily logs, meetings, and git changes, then **propagates updates** across related memory files (e.g., a role change updates people/, glossary.md, and CLAUDE.md). Updates `memory/index.md` (catalog) and `memory/log.md` (operation log) after each run.

## Custom Routines

Custom routines live in `ADWs/routines/custom/` (gitignored) and are scheduled via `config/routines.yaml` (also gitignored).

To create a custom routine, say **"create a routine"** and the `create-routine` skill will guide you.

### config/routines.yaml

```yaml
daily:
  - name: "My Routine"
    script: my_routine.py
    time: "19:00"
    enabled: true

weekly:
  - name: "Weekly Report"
    script: weekly_report.py
    day: friday
    time: "09:00"
    enabled: true

monthly:
  - name: "Monthly Close"
    script: monthly_close.py
    day: 1
    time: "08:00"
    enabled: true
```

## Scheduled Tasks (One-Off)

Scheduled tasks are **non-recurrent actions** that execute once at a specified date/time. Unlike routines (which repeat on cron), a scheduled task runs once and is done.

Use cases:
- "Post no LinkedIn sexta 10h"
- "Roda o financial pulse amanha 8h"
- "Envia resumo pro Telegram as 14h"

### Creating Scheduled Tasks

**Via CLI:** Say "schedule this for" or use the `schedule-task` skill.

**Via Dashboard:** Go to `/tasks` → click "New Task" → fill the form.

**Via API:**
```bash
POST /api/tasks
{
  "name": "Post LinkedIn — Summit",
  "type": "skill",           # skill | prompt | script
  "payload": "social-post-writer LinkedIn post about Summit",
  "agent": "pixel-social-media",
  "scheduled_at": "2026-04-11T16:00:00Z"
}
```

### Task Lifecycle

```
pending → running → completed
                  → failed (can retry)
pending → cancelled
```

The scheduler checks for pending tasks every 30 seconds and executes them in background threads.

### Dashboard

Tasks are managed at `/tasks` in the dashboard with:
- Filter by status (pending, running, completed, failed)
- Create/edit/cancel/delete actions
- "Run Now" for immediate execution
- View result/error output

## Dynamic Routine Discovery

Routines are discovered dynamically from script files. The system:

1. Scans `ADWs/routines/*.py` (core) and `ADWs/routines/custom/*.py` (custom)
2. Extracts agent from docstring (`via AgentName` pattern)
3. Builds make-IDs automatically (e.g. `financial_pulse.py` → `fin-pulse`)

No hardcoded mappings needed — add a new script and it's automatically available.

## How It Works

1. Scheduler runs embedded in the dashboard (`make dashboard-app`)
2. Core routines are hardcoded in `scheduler.py`
3. Custom routines are loaded from `config/routines.yaml`
4. Scheduled tasks are stored in SQLite and checked every 30 seconds
5. Each routine/task invokes Claude Code CLI via the ADW Runner (`ADWs/runner.py`)
6. Runner logs to `ADWs/logs/` (JSONL + metrics)
7. Reports saved to workspace folders

## Manual Execution

```bash
# Core routines (dedicated targets)
make morning      # Good Morning
make eod          # End of Day
make memory       # Memory Sync
make memory-lint  # Memory Lint
make weekly       # Weekly Review

# Any routine (core or custom) via dynamic runner
make run R=fin-pulse        # Financial Pulse
make run R=community-week   # Community Weekly
make run R=licensing        # Licensing Daily

# List all available routines
make list-routines

# All commands
make help
```
