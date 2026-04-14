# Heartbeats

![Heartbeats — proactive agents with schedule, status, cost](imgs/doc-heartbeats.webp)

**Heartbeats are proactive agents.** A heartbeat is a configuration that wakes an agent on a schedule so it can triage work without being asked. Instead of you remembering to ask Atlas "any stale PRs?" every morning, Atlas wakes up every 4 hours, checks, and acts only if there's something to do.

## The Mental Model

A routine is **systematic** — the same script runs every day at 7am. A heartbeat is **proactive** — the agent wakes, looks, and decides whether to act. Every heartbeat run answers a single question:

> Given the current state of my domain, should I work now or skip?

The agent returns a JSON verdict. If `action: work`, the dispatcher lets the agent run its turns. If `action: skip`, the run ends immediately at near-zero cost.

## Anatomy of a Heartbeat

Heartbeats live in `config/heartbeats.yaml` (source of truth) and are mirrored to the dashboard DB. Each entry has:

| Field | What it does |
|---|---|
| `id` | Unique slug, kebab-case (e.g. `atlas-4h`) |
| `agent` | Which agent to wake (`atlas-project`, `zara-cs`, …) |
| `interval_seconds` | How often the interval trigger fires. Minimum 60 |
| `max_turns` | Hard cap on Claude turns per run (default 10) |
| `timeout_seconds` | Hard kill timeout for the subprocess (default 300) |
| `lock_timeout_seconds` | Stale lock sweep threshold (default 1800) |
| `wake_triggers` | Subset of `[interval, new_task, mention, manual, approval_decision]` |
| `decision_prompt` | The question the agent answers — must force a JSON verdict |
| `goal_id` | Optional goal slug for context injection |
| `required_secrets` | `.env` keys the agent needs |
| `enabled` | Master switch. Always starts `false` |

## Quick Start

### 1. Create a heartbeat

From Claude Code, use the `create-heartbeat` skill:

> "Create a 4-hour heartbeat for atlas-project that triages stale PRs and issues."

The skill walks you through the fields, defaults `enabled: false`, and calls `POST /api/heartbeats`. The entry appears in the dashboard **Heartbeats** page as disabled.

Alternatively, edit `config/heartbeats.yaml` directly and call `POST /api/heartbeats/reindex` to mirror it into the DB.

### 3. Dry-run before enabling

From the dashboard, click **Run now** on the card (or call `POST /api/heartbeats/{id}/run`). This fires a one-off manual run regardless of the interval clock. Inspect the result:

- Did the agent return valid JSON?
- Was the decision reasonable?
- Did it stay within `max_turns` and `timeout_seconds`?

If yes, flip the enable toggle. The dispatcher will pick up the next interval tick.

### 4. Monitor runs

Every run records `started_at`, `finished_at`, `status`, `tokens_input`, `tokens_output`, `cost_usd`, and the parsed `decision_json`. The **Heartbeats** page in the dashboard shows the last 10 runs per card and aggregate 7-day cost.

## Wake Triggers

A heartbeat wakes on any of the triggers listed in `wake_triggers`:

- **interval** — the scheduler fires every `interval_seconds`. Almost always included.
- **manual** — someone clicks "Run now" or calls the API. Enables operators to debug.
- **mention** — a `@agent-slug` in a ticket comment fires a mention trigger (if the agent has an enabled heartbeat with `mention` in its wake_triggers). Max 3 mentions per comment.
- **new_task** — a goal task created with this agent as `assignee_agent` wakes the heartbeat.
- **approval_decision** — an approval request decided (future feature).

Multiple triggers = more responsiveness. Fewer triggers = more predictable cost.

## Cost Control

Because heartbeats burn tokens on every run, put guardrails on them:

1. **Start `enabled: false`**. Always. Review the first manual run before enabling.
2. **Use a crisp `decision_prompt`**. If the agent writes a paragraph when it should write JSON, you waste tokens.
3. **Bias toward `skip`**. Train the prompt to skip unless there's genuine urgency. A 4-hour heartbeat that skips 4 out of 6 runs per day is doing its job.
4. **Cap `max_turns` low** for pure triage heartbeats (5–10). Only raise it for agents that may need to act on multiple items.
5. **Watch `cost_7d`** on the dashboard card. If a heartbeat trends up, the prompt is probably too soft — tighten the skip criteria.

## Debugging

### A heartbeat isn't firing

1. Check the heartbeat's `enabled` — is this one individually on?
2. Check the dispatcher log (`journalctl -u evo-nexus -f` or the dashboard service logs) for interval registration.
3. Call `POST /api/heartbeats/{id}/run` — does a manual run work? If yes, it's a scheduler issue; if no, it's an agent or prompt issue.

### A run failed

Look at the run's `stderr_tail` and `stdout_tail`. Common causes:

- Missing `required_secrets` in `.env`
- `decision_prompt` didn't force JSON — the parser couldn't extract the verdict
- Agent hit `max_turns` before returning (raise the cap or tighten the prompt)
- Agent hit `timeout_seconds` (integration call was slow — raise timeout or add a retry inside the agent)

### YAML and DB drift

If you edited `config/heartbeats.yaml` by hand and the dashboard still shows the old state, run:

```bash
curl -X POST http://localhost:8080/api/heartbeats/reindex
```

This rebuilds the DB rows from the YAML. Safe to run anytime.

## CLI Skills

| Skill | What it does |
|---|---|
| `create-heartbeat` | Interactive wizard to add a new heartbeat |
| `manage-heartbeats` | List, enable/disable, trigger manual runs, inspect history |

## Related

- `docs/goals.md` — link a heartbeat to a goal for context injection
- `docs/tickets.md` — `@mentions` in tickets wake heartbeats
- Source: `dashboard/backend/heartbeat_dispatcher.py`, `dashboard/backend/routes/heartbeats.py`, `dashboard/backend/heartbeat_schema.py`
