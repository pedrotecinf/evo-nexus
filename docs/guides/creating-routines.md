# Creating Routines

Routines are automated tasks that run on a schedule — daily financial snapshots, community pulses, email triage, and more. Use the `create-routine` skill to generate everything you need.

## Quick Start

Just say:

```
create a routine
```

or describe what you want:

```
I want to automate a daily competitor check
```

Claude walks you through the setup.

## What the Skill Asks

The `create-routine` skill collects four things:

1. **What** — What should the routine do? (e.g., "Check competitor pricing pages and summarize changes")
2. **Which agent** — Who runs it? (e.g., Sage for strategy, Pulse for community)
3. **When** — Schedule in cron format or natural language (e.g., "every weekday at 9am", "Mondays and Fridays at 8:30")
4. **Output** — Where does the result go? (e.g., HTML report, markdown log, Telegram notification)

## What Gets Generated

After you answer, the skill creates:

### 1. Python Script

Located at `ADWs/routines/custom/<name>.py`:

```python
"""Daily Competitor Check — monitors competitor pricing and features."""
# Auto-generated routine script
# Agent: sage
# Schedule: 0 9 * * 1-5

import subprocess
import sys

def run():
    prompt = """..."""
    subprocess.run([sys.executable, "-m", "claude", ...])

if __name__ == "__main__":
    run()
```

### 2. YAML Entry

Added to `config/routines.yaml`:

```yaml
- name: competitor-check
  description: Daily competitor pricing and feature check
  agent: sage
  schedule: "0 9 * * 1-5"
  script: ADWs/routines/custom/competitor-check.py
  make_target: competitor-check
```

## Example: Daily Competitor Check

Here's the full walkthrough:

**You:** "I want to automate a daily competitor check"

**Claude:** "What exactly should this routine check?"

**You:** "Monitor competitor websites for pricing changes, new features, and blog posts. Compare against our positioning."

**Claude:** "Which agent should run it? I'd suggest Sage since this is strategic intelligence."

**You:** "Yes, Sage."

**Claude:** "When should it run?"

**You:** "Every weekday at 9am"

**Claude:** "Where should the output go?"

**You:** "HTML report in the strategy folder, plus a Telegram summary"

Claude then generates the script and YAML entry. Routines are discovered dynamically — no Makefile changes needed. Test it immediately:

```bash
make run R=competitor-check
```

## Where Files Live

| File | Location |
|---|---|
| Custom routine scripts | `ADWs/routines/custom/` |
| Core routine scripts | `ADWs/routines/` |
| Routine config | `config/routines.yaml` |
| Generated reports | Varies by agent (e.g., `09 Estrategia/`, `05 Financeiro/`) |

## Testing

After creation, test your routine:

```bash
# Run by ID (dynamic discovery)
make run R=competitor-check

# List all available routines
make list-routines

# Check logs
make logs
```

## Managing Routines

- **Edit schedule**: Update the entry in `config/routines.yaml`
- **Disable**: Set `enabled: false` or remove the YAML entry
- **View metrics**: `make metrics` shows token usage and cost per routine
- **Scheduler**: `make scheduler` runs all routines on their configured schedules

## One-Off Actions

If you need to run something **once** at a specific time (not recurring), use [Scheduled Tasks](../routines/scheduled-tasks.md) instead. Say "schedule this for Friday at 10am" or use the `schedule-task` skill.
