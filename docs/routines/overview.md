# Routines Overview

Routines are automated workflows (ADWs -- AI Developer Workflows) that run on a schedule. There are two types:

- **AI routines** -- invoke Claude Code CLI with an agent to perform reasoning tasks (reports, analysis, decisions). Cost tokens per run.
- **Systematic routines** -- pure Python scripts that perform deterministic operations (API calls, file ops, data transforms). No AI, no tokens, no cost, runs in seconds.

## Core vs Custom

```
ADWs/routines/
  good_morning.py       # Core (ships with the repo, hardcoded in scheduler.py)
  end_of_day.py         # Core
  memory_sync.py        # Core
  memory_lint.py        # Core
  weekly_review.py      # Core
  examples/             # Example routines (tracked with the repo)
    community_daily.py
    financial_pulse.py
    ...
  custom/               # User-created (gitignored), scheduled via routines.yaml
    my_routine.py
    ...
```

**Core routines** ship with the repo and cover the essential daily loop: good_morning, end_of_day, memory_sync, memory_lint, and weekly_review. Their schedules are hardcoded in `scheduler.py` — they do NOT come from `config/routines.yaml`. See [Core Routines](core-routines.md) for a detailed explanation of each one and why they matter.

> **Dynamic Discovery:** Routines are discovered dynamically by scanning script files. The agent is extracted from each script's docstring (`via AgentName` pattern). No hardcoded mappings needed — add a new script and it's automatically available in the dashboard, API, and `make run`.

> **Note:** Memory maintenance follows the LLM Wiki pattern. The `memory_sync` routine (daily) handles ingest with cross-reference propagation (updating related memory files when one changes). The `memory_lint` routine (weekly) performs health checks: detecting contradictions, stale data, orphan files, and coverage gaps. Both routines update `memory/index.md` (catalog) and `memory/log.md` (operation log).

**Example routines** live in `ADWs/routines/examples/` and are tracked with the repo. These are reference implementations for common integrations (Discord, Stripe, YouTube, etc).

**Custom routines** live in `ADWs/routines/custom/` and are gitignored. Copy from examples or create your own. Only custom routines go in `config/routines.yaml`. The `create-routine` skill helps generate them.

## ADW Runner

All routines use `ADWs/runner.py`, which provides:

- **`run_skill(skill, log_name, timeout, agent)`** -- executes a skill via Claude Code CLI (AI routine)
- **`run_claude(prompt, log_name, timeout, agent)`** -- executes a raw prompt (AI routine)
- **`run_script(func, log_name, timeout)`** -- executes a pure Python function (systematic routine, no AI)
- **`banner(title, subtitle)`** -- prints a styled header
- **`summary(results, title)`** -- prints execution summary with cost/token stats

The runner handles:
- Invoking `claude --print --dangerously-skip-permissions --output-format json` (AI routines)
- Executing Python functions directly with timeout protection (systematic routines)
- Logging to JSONL files (`ADWs/logs/YYYY-MM-DD.jsonl`)
- Saving detailed logs (`ADWs/logs/detail/`)
- Accumulating metrics per routine (`ADWs/logs/metrics.json`)
- Rich terminal output with progress indicators

## How a Routine Script Works

Every routine follows the same pattern:

```python
#!/usr/bin/env python3
"""ADW: Financial Pulse -- Daily financial snapshot via Flux"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
from runner import run_skill, banner, summary

def main():
    banner("Financial Pulse", "Stripe - Omie - MRR - Churn | @flux")
    results = []
    results.append(run_skill(
        "fin-daily-pulse",
        log_name="financial-pulse",
        timeout=600,
        agent="flux-finance"
    ))
    summary(results, "Financial Pulse")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
```

Key elements:
1. Import the runner from `ADWs/runner.py`
2. Print a banner with the routine name
3. Call `run_skill()` with the skill name, log name, timeout, and agent
4. Print a summary

For multi-step routines, append multiple results to the list.

## config/routines.yaml

This file defines the schedule for **custom routines only**. Core routines (good_morning, end_of_day, memory_sync, weekly_review) are hardcoded in `scheduler.py` and do not need entries here.

```yaml
daily:
  - name: "Community Pulse"
    script: community_daily.py
    time: "20:00"
    enabled: true

  - name: "Sync Meetings"
    script: sync_meetings.py
    interval: 30          # Every 30 minutes instead of fixed time
    enabled: true

weekly:
  - name: "Financial Weekly"
    script: financial_weekly.py
    day: friday
    time: "07:30"
    enabled: true

  - name: "Linear Review"
    script: linear_review.py
    days: [monday, wednesday, friday]   # Multiple days
    time: "09:00"
    enabled: true

monthly:
  - name: "Monthly Close"
    script: monthly_close.py
    day: 1                # Day of month
    time: "08:00"
    enabled: true
```

Fields:
- `name`: Display name
- `script`: Python file in `ADWs/routines/custom/` (or `ADWs/routines/examples/`)
- `time`: Execution time (24h format, local timezone)
- `interval`: Run every N minutes (instead of fixed time)
- `day`: Day of week (weekly) or day of month (monthly)
- `days`: Array for multi-day weekly schedules
- `enabled`: Toggle on/off without deleting

## Scheduler

Start the scheduler with:

```bash
make scheduler
```

This runs `scheduler.py`, which has core routines hardcoded and also reads `config/routines.yaml` for custom routines. The scheduler runs in the foreground and shows real-time progress.

The dashboard also starts/stops the scheduler from the **Services** page.

## Creating Custom Routines

### Using the skill

```
/create-routine
```

The `create-routine` skill walks you through:
1. What the routine does
2. Which agent runs it
3. Which skill it invokes
4. The schedule (daily/weekly/monthly)

It generates the Python script and updates `config/routines.yaml`. No Makefile changes needed — routines are discovered dynamically.

### Manually

1. Create `ADWs/routines/custom/my_routine.py` following the pattern above
2. Add an entry to `config/routines.yaml`

## Manual Execution

Core routines have dedicated make targets. All routines (core and custom) can be run with the dynamic runner:

```bash
# Core targets
make morning         # Morning briefing
make eod             # End of day
make memory          # Memory sync
make memory-lint     # Memory lint
make weekly          # Weekly review

# Dynamic runner (any routine by ID)
make run R=fin-pulse        # Financial pulse
make run R=community        # Community pulse
make run R=licensing-month  # Licensing monthly

# List all available routines
make list-routines
```

Or run the Python script directly:

```bash
python3 ADWs/routines/custom/community_daily.py
```

## Scheduled Tasks (One-Off)

For actions that should run **once** at a specific time (not recurring), use **Scheduled Tasks** instead of routines. See [Scheduled Tasks](scheduled-tasks.md) for details.

```
"Post no LinkedIn sexta 10h" → scheduled task (one-off)
"Check community every day at 20h" → routine (recurring)
```

## Logs and Metrics

### Log files

```
ADWs/logs/
  2026-04-08.jsonl           # Daily JSONL log (one line per run)
  metrics.json               # Accumulated metrics per routine
  detail/                    # Full stdout/stderr per run
    20260408-200000-community-daily.log
```

### Viewing logs

```bash
make logs            # Latest JSONL entries
make logs-detail     # List detailed log files
make logs-tail       # Show the latest full log
make metrics         # Per-routine metrics table
make clean-logs      # Remove logs older than 30 days
```

### Metrics format

`metrics.json` tracks per routine:
- Total runs, successes, failures, success rate
- Average duration
- Total and average cost (USD)
- Total input/output tokens
- Last run timestamp
