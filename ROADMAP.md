# OpenClaude Roadmap

> Unofficial toolkit for Claude Code — AI-powered business operating system.
>
> This roadmap is updated regularly. Want to vote or suggest? [Open a discussion](https://github.com/EvolutionAPI/open-claude/discussions) or [create an issue](https://github.com/EvolutionAPI/open-claude/issues).

---

## Legend

| Symbol | Meaning |
|--------|---------|
| `[ ]` | Not started |
| `[x]` | Done |
| `⚠️` | Breaking change |
| `🔥` | High priority |
| `💡` | Needs design discussion first |

---

## v0.4 — Foundation & Stability

> Fix, secure, and improve what already exists before growing.

### Skills

- [x] 🔥 **Evolution product skills** — `int-evolution-api` (33 commands), `int-evolution-go` (24 commands), `int-evo-crm` (48 commands) for managing instances, messages, contacts, conversations, pipelines via REST API.
- [x] **Version indicator & update alerts** — show current version in dashboard sidebar, alert when new GitHub releases are available.

### Developer Experience

- [x] 🔥 **CLI installer** — `npx @evoapi/open-claude` — clones repo, installs deps, runs interactive setup wizard.
- [x] **Full Docker install** — `docker compose up dashboard` with multi-stage Dockerfile + GitHub Actions CI pushing to GHCR.
- [x] **Update checker** — dashboard checks GitHub releases and shows upgrade notification.
- [x] **settings.json** — project-level permissions (allow/deny), hooks configuration, thinking mode enabled.
- [x] **CLAUDE.md split** — reduced from 263 to 128 lines. Detailed config moved to `.claude/rules/` (agents, integrations, routines, skills).
- [x] **Inner-loop commands** — `/status` (workspace status) and `/review` (recent changes + next actions).

### Dashboard UX

- [x] **Sidebar reorganization** — 5 collapsible groups (Main, Operations, Data, System, Admin) with localStorage persistence.
- [x] **Active agent visualization** — Claude Code hooks track agent launches via `PreToolUse` events, writing to `agent-status.json`. Dashboard polls `/api/agents/active` and shows "RUNNING" badges with pulse animation on agent cards and overview.
- [x] **Agents page redesign** — unique icons and accent colors per agent, status dots, slash command badges, memory count pills, hover glow effects.
- [x] **Overview page redesign** — stat cards with icons and trend indicators, active agents bar, quick actions row, improved reports and routines tables.

### Agent Generalization

- [x] **Agent prompts generalized** — all 9 agent prompts cleaned of hardcoded personal references. User-specific context preserved in `_improvements.md` per agent memory folder.

---

## v0.5 — Extensibility & Ecosystem

> Make OpenClaude composable and self-extending.

### Agent System

- [x] 🔥 **Generalize existing agents** — all 9 agent prompts generalized. User-specific context preserved in `_improvements.md` per agent memory folder. Adapter patterns documented as future work.
- [ ] 🔥 **New business agents** — expand functional coverage:
  - [ ] **Marketing Agent** — orchestrate existing `mkt-*` skills, attribution, budget, full funnel
  - [ ] **HR / People Agent** — onboarding, 1:1s, performance reviews, hiring pipeline
  - [ ] **Customer Success Agent** — health score, churn prediction, NPS/CSAT, client onboarding
  - [ ] **Legal / Compliance Agent** — contracts, renewals, GDPR/LGPD, compliance checklists
  - [ ] **Product Agent** — discovery, feature prioritization (RICE/ICE), PLG metrics, feedback loop
  - [ ] **Data / BI Agent** — cross-area consolidated dashboard, unified KPIs, alerts, trend analysis
- [ ] 💡 **Custom agents** — define spec and UX for user-created agents: naming, memory isolation, skill scope, onboarding
- [ ] 💡 **Help agent** — agent that answers questions about the workspace using its own documentation (RAG)

### Routines & Scheduling

- [ ] 🔥 **Trigger registry** — define and manage named triggers (webhook, cron, event-based) that invoke skills or routines
- [x] **Non-recurrent scheduled actions** — one-off scheduled tasks (e.g., "post this on LinkedIn Friday at 10am") without creating a full routine
- [x] **Systematic routines** — pure Python routines via `run_script()` — no AI, no tokens, no cost. `create-routine` skill generates the code

### Integrations

- [ ] **Complete Obsidian integration** — finish `obs-*` skills: bidirectional sync, canvas, bases, CLI

### Import / Export

- [ ] **Backup system** — export workspace state as ZIP (agents, skills, routines, memory, config); import to restore. Support local, git, and cloud bucket targets.
- [ ] **Install via ZIP** — install skills, routines, and agents through the dashboard UI by uploading a ZIP. Includes malware and prompt injection scanning.

---

## v1.0 — Community & Growth

> Community adoption, discoverability, and self-sustaining ecosystem.

### Community & Docs

- [x] 🔥 **Public roadmap** — this file. Community input welcome via [discussions](https://github.com/EvolutionAPI/open-claude/discussions).
- [ ] **Telegram & Discord channels** — activate community channels, document in README and docs site.
- [ ] **In-app tutorials** — contextual tutorials surfaced inside the dashboard, not just external docs.
- [ ] **Resume Claude sessions in chat** — list active/resumable Claude sessions in dashboard chat with `--resume` support.

### Development

- [ ] **Testing framework** — define and implement test strategy for skills, routines, and agent behaviors; prevent regressions.

---

## Contributing

Want to help? Pick any `[ ]` item and:

1. Check [open issues](https://github.com/EvolutionAPI/open-claude/issues)
2. Read [CONTRIBUTING.md](CONTRIBUTING.md)
3. For `💡` items, open a [discussion](https://github.com/EvolutionAPI/open-claude/discussions) first — design is still open

---

*Last updated: 2026-04-09 — [Evolution Foundation](https://evolutionfoundation.com.br)*
