# Scheduled Tasks

Scheduled tasks are **one-off actions** that execute once at a specified date/time. Unlike routines (which repeat on a cron schedule), a scheduled task runs once and is done.

## Use Cases

- "Post no LinkedIn sexta 10h" -- schedule a skill to run at a specific time
- "Roda o financial pulse amanha 8h" -- run an existing script at a future time
- "Envia resumo pro Telegram as 14h" -- send a prompt to an agent later

## Task Types

| Type | Payload | What Happens |
|------|---------|--------------|
| **skill** | Skill name + args | Calls Claude CLI executing the skill via an agent |
| **prompt** | Free-form text | Sends a raw prompt to Claude CLI via an agent |
| **script** | Script path | Runs a Python script directly (no AI) |

## Creating Tasks

### Via CLI (skill)

Say "schedule this for" or use the `schedule-task` skill:

```
agendar post no LinkedIn pra sexta 10h sobre o Summit
```

Claude parses the intent, confirms the details, and creates the task via API.

### Via Dashboard

Go to `/tasks` in the dashboard:

1. Click **"+ New Task"**
2. Fill in: name, type, payload, agent, date/time
3. Click **Schedule**

The task appears in the list as "pending".

### Via API

```bash
POST /api/tasks
{
  "name": "Post LinkedIn -- Summit",
  "type": "skill",
  "payload": "social-post-writer LinkedIn post about Evolution Summit",
  "agent": "pixel-social-media",
  "scheduled_at": "2026-04-11T16:00:00Z"
}
```

## Task Lifecycle

```
pending --> running --> completed
                   --> failed (can retry)
pending --> cancelled
```

- **pending** -- waiting for scheduled time
- **running** -- currently executing
- **completed** -- finished successfully
- **failed** -- error occurred (can be retried with "Run Now")
- **cancelled** -- manually cancelled before execution

## How Execution Works

1. The scheduler loop (every 30 seconds) queries: `WHERE status='pending' AND scheduled_at <= NOW()`
2. Each matching task is executed in a background thread
3. For `skill` and `prompt` types, the task uses `ADWs/runner.py` (same infrastructure as routines)
4. For `script` type, the Python script runs as a subprocess
5. Results are saved in `result_summary`; errors in `error`
6. Status updates to `completed` or `failed`

## API Reference

| Method | Endpoint | Action | Permission |
|--------|----------|--------|------------|
| GET | `/api/tasks` | List tasks | `tasks:view` |
| POST | `/api/tasks` | Create task | `tasks:execute` |
| GET | `/api/tasks/<id>` | Get task detail | `tasks:view` |
| PUT | `/api/tasks/<id>` | Edit pending task | `tasks:execute` |
| DELETE | `/api/tasks/<id>` | Cancel/delete task | `tasks:execute` |
| POST | `/api/tasks/<id>/run` | Execute immediately | `tasks:execute` |

Query parameters for GET `/api/tasks`:
- `status` -- filter by status (pending, running, completed, failed, cancelled)
- `page` -- page number (default: 1)
- `per_page` -- items per page (default: 50)

## Dashboard Page

The `/tasks` page shows:

- **Filter tabs** -- All, Pending, Running, Completed, Failed
- **Task table** -- name, type badge, agent badge, scheduled time, status, actions
- **Create modal** -- form with name, description, type, payload, agent, datetime
- **View result modal** -- shows output/error for completed/failed tasks

### Actions by Status

| Status | Available Actions |
|--------|-------------------|
| pending | Edit, Run Now, Cancel |
| running | (none -- waiting) |
| completed | View Result, Delete |
| failed | View Result, Retry, Delete |
| cancelled | Delete |

## Agents

| Agent ID | Display |
|----------|---------|
| `clawdia-assistant` | @clawdia |
| `flux-financeiro` | @flux |
| `atlas-project` | @atlas |
| `pulse-community` | @pulse |
| `pixel-social-media` | @pixel |
| `sage-strategy` | @sage |
| `kai-personal-assistant` | @kai |
| `nex-comercial` | @nex |
| `mentor-courses` | @mentor |

## Tasks vs Routines

| | Scheduled Task | Routine |
|---|---|---|
| **Frequency** | Once | Recurring (daily/weekly/monthly) |
| **Defined in** | SQLite database | `config/routines.yaml` + script file |
| **Created via** | Dashboard UI, API, or `schedule-task` skill | `create-routine` skill |
| **Execution** | Scheduler checks every 30s | Scheduler runs on cron schedule |
| **Output** | Saved in DB (`result_summary`) | Saved to files + metrics.json |
