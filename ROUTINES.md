# Automated Routines

Guide to all workspace routines, their schedules, and responsible agents.

---

## Daily Routines

| Time | Routine | Command | Agent | What It Does |
|:---:|--------|---------|--------|-----------|
| **06:50** | Review Todoist | `make review` | @clawdia | Categorizes, translates, and organizes tasks |
| **07:00** | Good Morning | `make morning` | @clawdia | Briefing: today's agenda + important emails + priority tasks |
| **07:15** | Email Triage | `make triage` | @clawdia | Classifies unread emails by urgency, proposes actions |
| **every 30min** | Sync Meetings | `make sync` | @clawdia | Pulls meetings from Fathom, saves summaries, creates tasks |
| **18:00** | Social Analytics | `make social` | @pixel | YouTube + Instagram + LinkedIn consolidated cross-platform HTML |
| **18:30** | Licensing Daily | `make licensing` | @atlas | Instances, geo, versions, activation funnel, alerts in HTML |
| **19:00** | Financial Pulse | `make fin-pulse` | @flux | Stripe (MRR, charges, churn) + ERP (accounts, invoices) snapshot HTML |
| **20:00** | Community Pulse | `make community` | @pulse | Discord 24h activity, sentiment, support, topics in HTML |
| **20:15** | FAQ Sync | `make faq` | @pulse | Updates FAQ with questions from Discord + GitHub |
| **21:00** | End of Day | `make eod` | @clawdia | Consolidates agent memory, ADW logs, tasks, learnings into daily log |
| **21:15** | Memory Sync | `make memory` | @clawdia | Extracts decisions/people/feedback from logs and meetings, updates persistent memory |
| **21:30** | Dashboard | `make dashboard` | @clawdia | Reads all routine outputs, generates 360 HTML dashboard with health badges |

## Weekly Routines

| Day/Time | Routine | Command | Agent | What It Does |
|:---:|--------|---------|--------|-----------|
| **Fri 08:00** | Weekly Review | `make weekly` | @clawdia | Full review: meetings, tasks, agenda, memory into weekly report |
| **Fri 08:30** | Trends | `make trends` | @clawdia | Trend analysis: community + GitHub + financial + operational scorecard |
| **Mon/Wed/Fri 09:00** | Linear Review | `make linear` | @atlas | Issues in review, blockers, stale items, sprint progress |
| **Mon/Wed/Fri 09:15** | GitHub Review | `make github` | @atlas | Open PRs, community issues, stars/forks, releases |
| **Mon 09:30** | Community Weekly | `make community-week` | @pulse | Weekly analysis: WAM, sentiment, topics, product insights, docs gaps in HTML |
| **Fri 09:00** | Strategy Digest | `make strategy` | @sage | Consolidates financial + product + community + market into strategic view |
| **Fri 07:30** | Financial Weekly | `make fin-weekly` | @flux | Week consolidation: revenue, expenses, cash flow, overdue accounts in HTML |
| **Fri 07:45** | Licensing Weekly | `make licensing-weekly` | @atlas | Weekly growth: instances, geo expansion, version adoption in HTML |
| **Fri 08:15** | Social Analytics Weekly | `make social` | @pixel | Weekly cross-platform report: YouTube + Instagram + LinkedIn |
| **Sun 10:00** | Health Check-in | `make health` | @kai | Health check-in: weight, nutrition, exercise, sleep, energy, medication |

## Monthly Routines

| Day/Time | Routine | Command | Agent | What It Does |
|:---:|--------|---------|--------|-----------|
| **Day 1 08:00** | Monthly Close Kickoff | `make fin-close` | @flux | P&L, close checklist, pending invoices, finance action items in HTML |
| **Day 1 08:00** | Community Monthly | `make community-month` | @pulse | Discord + WhatsApp 30d: MAM, sentiment, topics, product insights, docs gaps in HTML |
| **Day 1 08:00** | Licensing Monthly | `make licensing-month` | @atlas | Monthly growth: trajectory, markets, versions, projections in HTML |
| **Day 1 08:00** | Social Analytics Monthly | `make social` | @pixel | Monthly cross-platform report: YouTube + Instagram + LinkedIn |

---

## How It Works

Each routine is an ADW (AI Developer Workflow) in `ADWs/rotinas/` that:
1. Calls Claude Code CLI with the **correct agent** (`--agent`)
2. Executes the **corresponding skill** (structured prompt)
3. Shows **real-time output** in terminal (Rich)
4. Saves **structured logs** in `ADWs/logs/` (JSONL + detailed)

## Logs

```bash
make logs          # Latest JSONL entries
make logs-detail   # List detailed logs
make logs-tail     # Show latest full log
make clean-logs    # Remove logs older than 30 days
```

## Agents Used

| Agent | Routines |
|--------|---------|
| **@clawdia** | Morning, Sync, Triage, Review, Memory, EOD, Dashboard, Weekly, Trends |
| **@sage** | Strategy Digest |
| **@atlas** | Linear Review, GitHub Review, Licensing (daily, weekly, monthly) |
| **@pixel** | Social Analytics (daily, weekly, monthly) |
| **@pulse** | Community Pulse (daily), Community Weekly, Community Monthly, FAQ Sync |
| **@flux** | Financial Pulse (daily), Financial Weekly, Monthly Close |
| **@kai** | Health Check-in |

## Generated Files

| Routine | Format | Saves To |
|--------|---------|-----------|
| Good Morning | HTML | `workspace/daily-logs/[C] YYYY-MM-DD-morning.html` |
| Email Triage | HTML | `workspace/daily-logs/[C] YYYY-MM-DD-email-triage.html` |
| Review Todoist | MD | `workspace/daily-logs/[C] YYYY-MM-DD-todoist-review.md` |
| Sync Meetings | JSON + MD | `07 Meetings/fathom/` + `summaries/` |
| End of Day | MD | `workspace/daily-logs/[C] YYYY-MM-DD.md` |
| Memory Sync | MD | `memory/` (individual files) |
| Weekly Review | HTML + MD | `workspace/daily-logs/[C] YYYY-WXX-weekly-review.html` |
| Trends | HTML + MD | `workspace/daily-logs/[C] YYYY-WXX-trends.html` |
| Strategy Digest | HTML + MD | `09 Strategy/digests/[C] YYYY-WXX-strategy-digest.html` |
| Linear Review | HTML | `workspace/projects/linear-reviews/[C] YYYY-MM-DD-linear-review.html` |
| GitHub Review | HTML | `workspace/projects/github-reviews/[C] YYYY-MM-DD-github-review.html` |
| Community Pulse | HTML | `03 Community/reports/daily/[C] YYYY-MM-DD-community-pulse.html` |
| Community Weekly | HTML | `03 Community/reports/weekly/[C] YYYY-WXX-community-report.html` |
| FAQ Sync | MD | `03 Community/[C] FAQ.md` (updates) |
| Health Check-in | HTML + MD | `06 Personal/health-checkins/reports/[C] YYYY-MM-DD-health.html` |
| Dashboard | HTML | `workspace/daily-logs/[C] YYYY-MM-DD-dashboard.html` |
| Financial Pulse | HTML | `05 Finance/reports/daily/[C] YYYY-MM-DD-financial-pulse.html` |
| Financial Weekly | HTML | `05 Finance/reports/weekly/[C] YYYY-WXX-financial-weekly.html` |
| Monthly Close | HTML | `05 Finance/reports/monthly/[C] YYYY-MM-monthly-close.html` |
| Community Monthly | HTML | `03 Community/reports/monthly/[C] YYYY-MM-community-monthly.html` |
| Social Analytics | HTML | `04 Social/reports/consolidated/[C] YYYY-MM-DD-social-analytics.html` |
| Licensing Daily | HTML | `workspace/projects/licensing-reports/daily/[C] YYYY-MM-DD-licensing-daily.html` |
| Licensing Weekly | HTML | `workspace/projects/licensing-reports/weekly/[C] YYYY-WXX-licensing-weekly.html` |
| Licensing Monthly | HTML | `workspace/projects/licensing-reports/monthly/[C] YYYY-MM-licensing-monthly.html` |

### Available HTML Templates

All in `.claude/templates/html/`, dark theme (green `#00FFA7`, Inter font):

| Template | Used By |
|----------|-----------|
| `morning-briefing.html` | Good Morning |
| `email-triage.html` | Email Triage |
| `weekly-review.html` | Weekly Review |
| `trends-report.html` | Trends |
| `strategy-digest.html` | Strategy Digest |
| `linear-review.html` | Linear Review |
| `github-review.html` | GitHub Review |
| `community-daily-pulse.html` | Community Pulse |
| `community-weekly-report.html` | Community Weekly |
| `health-checkin.html` | Health Check-in |
| `dashboard-consolidation.html` | Dashboard |
| `financial-pulse.html` | Financial Pulse |
| `financial-weekly.html` | Financial Weekly |
| `monthly-close.html` | Monthly Close Kickoff |
| `community-monthly-report.html` | Community Monthly |
| `social-analytics-report.html` | Social Analytics (cross-platform) |
| `licensing-report.html` | Licensing Daily / Weekly / Monthly |
