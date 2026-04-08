# Roadmap -- OpenClaude

> Last updated: 2026-04-08
> Status: Active

---

## Vision

Transform the workspace into a complete AI-powered operating system where automated routines, specialized agents, and integrations work together to keep users informed, organized, and productive -- with minimal manual intervention.

---

## Current State

| Component | Qty | Status |
|---|---|---|
| Agents | 9 | Clawdia, Flux, Atlas, Kai, Pulse, Sage, Pixel, Nex, Mentor |
| Skills | 126 | Productivity, Google, Integrations, Finance, Marketing, Obsidian, Discord, Pulse, Sage, Social, Evo Method |
| Routines (ADWs) | 27 | 12 daily + 10 weekly + 4 monthly + scheduler |
| Integrations | 18 | Gmail, Calendar, Fathom, Todoist, Stripe, Omie, Linear, Discord, Telegram, GitHub, Canva, Notion, YouTube, Instagram, LinkedIn, WhatsApp, Licensing, Computer Use |
| Servers | 2 | Scheduler + Telegram Bot |
| HTML Templates | 17 | Full set covering all domains |

---

## Phase 1 -- Stabilization

Focus: ensure everything built works reliably.

- [x] **Test all routines** -- run each `make` target at least once and fix issues
- [x] **Persistent scheduler** -- `docker-compose.yml` + `Dockerfile` for background execution
- [x] **Fix ERP API** -- corrected endpoints and validated against official docs
- [ ] **Retry in runner** -- if Claude CLI fails by timeout/crash, retry once before giving up
- [ ] **Git auto-commit on EOD** -- end-of-day commits generated files (logs, reports, FAQ, summaries)
- [ ] **Calibrate timeouts** -- adjust timeout per routine based on real execution data

---

## Phase 2 -- Bidirectional Telegram (Done)

Resolved with `make telegram` -- Claude runs with `--channels plugin:telegram`, accepts messages, routes to the correct agent, and responds formatted via MCP.

---

## Phase 3 -- New Agents (Done)

All planned agents implemented.

- [x] **Pixel (@pixel)** -- Social media / multi-channel content (17 skills `social-*`)
- [x] **Nex (@nex)** -- Sales / pipeline management
- [x] **Sage (@sage)** -- Strategy, OKRs, scenarios (3 skills `sage-*`)
- [x] **Mentor (@mentor)** -- Courses and learning academy

---

## Phase 4 -- Unified Dashboard

Focus: HTML panels consolidating an overview of all domains.

- [x] **Daily dashboard** -- HTML template consolidating all areas: product, community, finance, routines, agenda, meetings. Skill `prod-dashboard`, ADW `make dashboard`, scheduler 21:30
- [ ] **Served locally** -- `make dashboard-serve` opens in browser with live reload
- [ ] **Auto-refresh** -- updates as routines run

---

## Phase 5 -- Intelligence and Advanced Automation

Focus: close loops and automate decisions.

- [x] **Trend analysis** -- compare metrics week-over-week (skill `prod-trends`, ADW `make trends`)
- [x] **Automated monthly close** -- full Stripe + ERP + P&L + checklist + pending items (skill `fin-monthly-close-kickoff`, ADW `make fin-close`, scheduler day 1 08:00)
- [x] **Financial routines** -- Financial Pulse daily (`make fin-pulse`, 19:00) + Financial Weekly (`make fin-weekly`, Friday 07:30)
- [ ] **Docs Gap to Issue** -- when FAQ Sync detects a recurring question without documentation: create GitHub issue + generate draft page and open PR
- [ ] **Proactive alerts** -- monitor balances (cloud providers, payment processors), service status, alert on Telegram
- [ ] **Weekly digest for the team** -- generate formatted weekly summary to send on Discord/WhatsApp
- [ ] **Automated changelog** -- generate changelog from merged commits/PRs of the week

---

## Phase 6 -- Scale and Observability

Focus: visibility and system reliability.

- [x] **Cost per routine** -- runner tracks tokens (input, output, cache) and USD cost per execution. Accumulated in `metrics.json`. Visible in terminal and via `make metrics`
- [ ] **Observability dashboard** -- HTML panel for routine health (success rate, avg time, failures, costs). Data already in `metrics.json`, template needed
- [ ] **Degradation alerts** -- if a routine starts failing more than 20%, alert on Telegram
- [ ] **Multi-workspace** -- prepare structure to replicate the workspace for other projects/users
- [ ] **Automatic backup** -- weekly routine that backs up the workspace (git push or cloud sync)

---

## Backlog (Future Ideas)

| Idea | Status | Notes |
|-------|--------|-------|
| AI Discord bot | Pending | Answer questions in #help using FAQ as knowledge base |
| Voice commands | Pending | Integrate with Whisper for voice commands via Telegram |
| Mobile dashboard | Pending | PWA version of the dashboard for mobile access |
| Notion integration | Done | MCP connected |
| Canva integration | Done | MCP connected |

---

## Principles

1. **Routine over heroics** -- reliable systems that run on their own beat heroic sprints
2. **Data before opinion** -- every decision based on evidence (metrics, logs, reports)
3. **Right agent for the job** -- each domain has its specialist, never overload one
4. **Human in the loop** -- AI suggests and executes, the user decides and approves
5. **Incremental** -- each phase delivers value independently, no dependency on the next
