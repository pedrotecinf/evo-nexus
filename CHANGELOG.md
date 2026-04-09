# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.0] - 2026-04-09

### Added
- **Scheduled Tasks** — new one-off task scheduling system. Schedule a skill, prompt, or script to run at a specific date/time without creating a full routine. Dashboard page at `/tasks` with create/edit/cancel/run-now/view-result. API CRUD at `/api/tasks`. Scheduler checks pending tasks every 30 seconds.
- **`schedule-task` skill** — conversational interface to create scheduled tasks ("agendar pra sexta 10h", "schedule this for tomorrow")
- **Dynamic routine discovery** — `ROUTINE_SCRIPTS` and `SCRIPT_AGENTS` are no longer hardcoded. Agent and script mappings are built dynamically by scanning `ADWs/routines/` scripts and extracting metadata from docstrings (`via AgentName` pattern). New scripts are auto-discovered.
- **`make run R=<id>`** — generic dynamic runner for any routine (core or custom)
- **`make list-routines`** — lists all discovered routines with agent, script, and name
- **Workspace file browser** — reports page replaced with a full file browser that navigates workspace folders

### Changed
- **Makefile cleaned** — custom routine targets (user-specific) removed from Makefile. Only core routine targets remain (`morning`, `eod`, `memory`, `memory-lint`, `weekly`). Custom routines run via `make run R=<id>`.
- **`ROUTINES.md`** — expanded with scheduled tasks docs, dynamic discovery, and updated manual execution section
- **Documentation** — new `docs/routines/scheduled-tasks.md`, updated makefile reference, dashboard overview, creating-routines guide, and skills overview

## [0.7.0] - 2026-04-09

### Added
- **Systematic routines** — new `run_script()` function in `ADWs/runner.py` for pure Python routines that run without Claude CLI, without AI, without tokens. Same logging/metrics infrastructure, but cost=$0 and duration in seconds instead of minutes.
- **`create-routine` skill updated** — now asks "AI or systematic?" and generates the correct script pattern. For systematic routines, Claude writes the Python logic once at creation time, then the script runs on its own forever.
- **Example routine** — `ADWs/routines/examples/log_cleanup.py` demonstrates the systematic pattern (deletes logs older than 30 days)
- **"systematic" badge** — dashboard Scheduler and Routines pages show a gray "systematic" badge for system routines instead of green `@agent`
- **Site docs CSS overhaul** — replaced fragile custom marked renderers with CSS-based styling on `.docs-content`. Tables, lists, code blocks, and all markdown elements now render correctly with the dark theme.
- **OAuth redirect URLs** — documented redirect URIs for YouTube, Instagram, and LinkedIn OAuth setup

### Changed
- **ROADMAP** — "Agent-less routines" marked as done

## [0.6.1] - 2026-04-09

### Added
- **Core routines documentation** (`docs/routines/core-routines.md`) — detailed explanation of all 5 core routines: what they do, why they matter, and how they form the daily loop
- **Memory Lint promoted to core** — moved from `ADWs/routines/custom/` to `ADWs/routines/`, hardcoded in `scheduler.py` (Sunday 09:00). Now 5 core routines instead of 4
- **Release skill** now syncs screenshots (`public/print-*.png` → `site/public/assets/`) on every release

### Changed
- **Dashboard pages redesigned** — 12 pages (Audit, Config, Costs, Files, Integrations, Memory, Reports, Roles, Routines, Scheduler, Skills, Systems, Templates, Users) with consistent dark theme and improved UX
- **Integration count** — 19 → 17 (removed internal-only Licensing and WhatsApp docs from public documentation)
- **Memory system** — LLM Wiki pattern: ingest propagation, weekly lint, centralized index, and operation log

### Removed
- **`docs/integrations/licensing.md`** — internal only, not public
- **`docs/integrations/whatsapp.md`** — internal only, not public

### Fixed
- **Dashboard build** — removed unused `totalTokens` variable in Costs page that blocked TypeScript compilation

## [0.6.0] - 2026-04-09

### Added
- **Evolution API skill** (`int-evolution-api`) — 33 commands: instances, messages (text, media, location, contact, buttons, lists, polls), chats, groups, webhooks
- **Evolution Go skill** (`int-evolution-go`) — 24 commands: instances, messages, reactions, presence
- **Evo CRM skill** (`int-evo-crm`) — 48 commands: contacts, conversations, messages, inboxes, pipelines, labels
- **Integration docs** — 3 new guides: `docs/integrations/evolution-api.md`, `evolution-go.md`, `evo-crm.md`
- **Dashboard integrations** — Evolution API, Evolution Go, and Evo CRM cards on Integrations page
- **`.env.example`** — added `EVOLUTION_API_URL/KEY`, `EVOLUTION_GO_URL/KEY`, `EVO_CRM_URL/TOKEN`

### Changed
- **Integration count** — 16 → 17 across README, site, and docs (removed internal-only Licensing and WhatsApp docs)
- **Community members** — 7,000+ → 17,000+ on site
- **v0.4 roadmap complete** — all 13 items done, Evolution product skills was the last one

## [0.5.1] - 2026-04-09

### Changed
- **Docs markdown rendering** — replaced regex parser with `marked` library. Code blocks, ASCII art, and nested formatting now render correctly on the site.
- **README and site** — `npx @evoapi/open-claude` is now the primary install method. Git clone shown as alternative.
- **Release skill** — `make docs-build` and frontend rebuild are now mandatory on every release (not conditional).

### Fixed
- **Site /docs navigation** — nested doc pages (e.g., `/docs/guides/creating-routines`) no longer 404. Switched from `useRoute` wildcard to direct URL parsing.
- **Site route matching** — changed from `/docs/:slug+` to `/docs/*` for reliable wouter matching.
- **CLI default directory** — `npx @evoapi/open-claude` without args now clones into current directory (`.`), not a subfolder.
- **Site CI build** — added missing `print-agents.png` to site assets.
- **Docs sync** — site now serves updated docs matching the repo (was stale).

## [0.5.0] - 2026-04-09

### Added
- **Active agent visualization** — Claude Code hooks (`PreToolUse`, `Stop`) track agent launches in `agent-status.json`. Dashboard polls `/api/agents/active` and shows animated "RUNNING" badges on agent cards and overview.
- **Agents page redesign** — unique icons and accent colors per agent, slash command badges, memory count pills, status dots, hover glow effects.
- **Overview page redesign** — stat cards with icons and trend indicators, active agents bar, quick actions row (Morning Briefing, Chat, Costs, GitHub), improved reports and routines tables with relative timestamps.
- **Claude Code hooks** — `agent-tracker.sh` hook registered in `settings.json` for real-time agent activity tracking.
- **Project settings.json** — permissions (allow/deny rules), hooks configuration.
- **Inner-loop commands** — `/status` (workspace status) and `/review` (recent changes + next actions).
- **Default system: Claude Status** — `seed_systems()` creates Anthropic status page as default external system on first boot.
- **Public roadmap** — `ROADMAP.md` with community input via GitHub discussions.

### Changed
- **CLAUDE.md split** — reduced from 263 to 128 lines. Detailed config moved to `.claude/rules/` (agents, integrations, routines, skills) — auto-loaded by Claude Code.
- **All 9 agent prompts generalized** — removed hardcoded personal references (Omie, Linear, Discord Evolution, Brazilian formats, etc.). User-specific context preserved in `_improvements.md` per agent memory folder.
- **Rules and commands translated** — all `.claude/rules/` and `.claude/commands/` files translated from Portuguese to English.

## [0.4.1] - 2026-04-09

### Added
- **Docker Compose for dashboard** — `Dockerfile.dashboard` (multi-stage: node + python) + `docker-compose.yml` with dashboard, telegram, and runner services. `make docker-dashboard` to start.
- **Dashboard CI** — GitHub Actions workflow builds and pushes dashboard image to `ghcr.io/evolutionapi/open-claude/dashboard` on push/release
- **npm CI** — GitHub Actions workflow publishes CLI to npm on release (requires `NPM_TOKEN` secret)

### Changed
- **Sidebar reorganized** — 5 collapsible groups (Main, Operations, Data, System, Admin) with collapse state persisted in localStorage
- **Scheduler removed from docker-compose** — runs embedded in dashboard, not as separate service
- **`make docker-up` → `make docker-telegram`** — reflects that only Telegram is a separate Docker service
- **Public roadmap updated** — removed internal Future/Research section, marked completed items

## [0.4.0] - 2026-04-09

### Added
- **CLI installer** — `npx @evoapi/open-claude` clones repo, checks prerequisites, installs deps, runs setup wizard, and builds dashboard
- **Version indicator in dashboard** — sidebar footer shows current version; `/api/version/check` compares against latest GitHub release with 1h cache
- **Public roadmap** — `ROADMAP.md` with 4 phases (v0.4 → Future), community input via GitHub discussions
- **Update guide** — `docs/guides/updating.md` with git pull, Docker, and custom content preservation instructions

### Changed
- **Privacy-first licensing** — removed heartbeat thread, deactivate endpoint, and shutdown hook. Only initial registration remains (who installed). No monitoring, no kill switch, no telemetry.
- **Licensing version** — now reads from `pyproject.toml` dynamically instead of hardcoded constant

### Fixed
- **nginx 403 on `/docs/`** — removed `$uri/` from `try_files` so directory paths fall through to SPA instead of returning Forbidden
- **`.gitignore` formatting** — `site/lib/` and `mempalace.yaml` were concatenated on one line
- **User-specific files removed from git** — `mempalace.yaml` and `entities.json` no longer tracked

## [0.3.2] - 2026-04-08

### Added
- **Docs page on site** (`/docs`) — full documentation viewer with sidebar, search, and markdown rendering
- **Auto-version system** — `pyproject.toml` is single source of truth, injected into site (Vite `__APP_VERSION__`), dashboard (`/api/version`), and CI (Docker build-arg)
- **Pre-build docs index** — `scripts/build-docs-index.mjs` generates `docs-index.json` at build time
- **`/api/version` endpoint** — dashboard serves current version from `pyproject.toml`

### Changed
- **`make docs-build`** — now also syncs `docs/` to `site/public/docs/`
- **Docs links** in landing page point to `/docs` (internal route, not dashboard)
- **Site version badge** — reads from `pyproject.toml` dynamically instead of hardcoded

## [0.3.1] - 2026-04-08

### Added
- **Landing page** (`site/`) — standalone React + Vite static site, extracted from Replit monorepo
- **Docker support for site** — multi-stage Dockerfile (node build → nginx serve) + docker-compose
- **GitHub Actions CI** — workflow builds site image and pushes to `ghcr.io/evolutionapi/open-claude/site` on push/release
- **Docs bundled in site image** — `docs/` copied into site build context automatically

### Changed
- **`.gitignore` updated** — site tracked in repo (Replit artifacts, node_modules, dist excluded)
- **Site assets renamed** — clean filenames (`logo.png`, `print-overview.png`, etc.) instead of Replit hashes

## [0.3.0] - 2026-04-08

### Added
- **Public Documentation** (`/docs`) — full docs site inside the dashboard, accessible without auth
- **MemPalace** — semantic knowledge base with ChromaDB for code/doc search (optional)
- **Content search** — docs search now matches inside file content, not just titles
- **llms-full.txt** — pre-generated plain text with all docs for LLM consumption (`/docs/llms-full.txt`)
- **23 routine examples** and **21 template examples** shipped with repo
- **14 documentation screenshots** in `docs/imgs/`
- **Comprehensive docs** — 28 markdown files across 9 sections (guides, dashboard, agents, skills, routines, integrations, real-world, reference)
- **Practical usage guides** — how to run routines, invoke agents, create custom skills

### Changed
- **Unofficial disclaimer** — README, docs, and landing page clearly state "unofficial, not affiliated with Anthropic"
- **Positioning** — "compatible with Claude Code and other LLM tooling" (not "purpose-built for")
- **Enterprise-safe language** — "integrates with" instead of "leverages", opens door for multi-provider future
- **Docs sidebar** — logical section ordering, section icons, content preview in search
- **llms-full.txt** — served as static pre-generated file (instant load, no on-the-fly concatenation)
- **i18n** — final cleanup, 18 files translated from Portuguese to English

### Fixed
- `/docs/llms-full.txt` redirect (was showing docs sidebar with "Loading..." instead of plain text)
- Screenshots with personal data removed and replaced
- 10 doc files corrected after full audit

## [0.2.0] - 2026-04-09

### Added
- **Core vs Custom split** — routines, templates, and skills separated into core (tracked) and custom (gitignored)
- **Create Routine skill** (`create-routine`) — guides users through creating custom routines step by step
- **Scheduler embedded in dashboard** — runs automatically with `make dashboard-app`, no separate process
- **Core/Custom badges** — scheduled routines and templates show green "core" or gray "custom" labels
- **Custom routines from YAML** — scheduler loads custom routines dynamically from `config/routines.yaml`
- **.env editor** — edit environment variables directly from the Config page in the dashboard
- **Auto-discover reports** — Reports page scans entire `workspace/` recursively, no hardcoded paths

### Changed
- **Routines reorganized** — 4 core routines in `ADWs/routines/`, custom in `ADWs/routines/custom/` (gitignored)
- **Templates reorganized** — 2 core HTML + 4 core MD templates, custom in `custom/` subfolders (gitignored)
- **`ADWs/rotinas/` renamed to `ADWs/routines/`** — full English naming
- **Agent files renamed** — `flux-financeiro` → `flux-finance`, `nex-comercial` → `nex-sales`
- **59 evo-* skills removed** — Evo Method is a separate project, skills gitignored
- **Docker removed from Services** — use Systems CRUD for Docker container management
- **ROUTINES.md rewritten** — generic, documents core vs custom split and YAML config format
- **scheduler.py rewritten** — only 4 core routines hardcoded, custom loaded from YAML
- **README updated** — correct agent names (`/clawdia`, `/flux`, `/atlas`, etc.), 4 core routines, ~67 skills

### Removed
- **ROADMAP.md** from Config page (file no longer exists)
- **Docker section** from Services page
- **Specific routine schedules** from scheduler.py (moved to user's `config/routines.yaml`)
- **Custom routines from git** — 23 scripts moved to gitignored `custom/` directory
- **Custom templates from git** — 15 HTML + 6 MD templates moved to gitignored `custom/` directories

### Fixed
- Custom routine scripts `sys.path` adjusted for `custom/` subdirectory (3 levels up for runner)
- Scheduler parser strips `custom/` prefix for agent mapping
- `SCRIPT_AGENTS` moved to module level (was inaccessible from `_load_yaml_routines`)
- Telegram `screen` command removed unsupported `-Logfile` flag
- Remaining Portuguese translated in skill bodies

## [0.1.1] - 2026-04-08

### Added
- **Silent Licensing** — automatic registration via Evolution Foundation licensing server
- **Systems CRUD** — register and manage apps/services from the dashboard
- **Roles & Permissions** — custom roles with granular permission matrix
- **Onboarding Skill** (`initial-setup`) — guides new users through the workspace
- **Screenshots** in README (overview, chat, integrations, costs)

### Changed
- **English-first codebase** — translated agents, skills, templates, routines, and config
- **Workspace folders** renamed from PT to EN (`workspace/daily-logs`, etc.)
- **Setup wizard** simplified — all agents enabled by default
- **HTML templates** standardized with Evolution Foundation branding
- **Makefile** auto-detects `uv` or falls back to `python3`
- All Python dependencies consolidated in `pyproject.toml`

### Removed
- **Evo Method** (`_evo/`) — separate project
- **Proprietary skills** — licensing and whatsapp excluded
- **Portuguese folder names** (01-09) — replaced with `workspace/`

### Fixed
- 16 bug fixes (scheduler logs, SQLite WAL, auth permissions, dates, etc.)

## [0.1.0] - 2026-04-08

### Added
- Initial open source release
- 9 Specialized Agents, ~67 Skills, 4 core routines
- Web Dashboard with auth, roles, web terminal, service management
- Integration clients (Stripe, Omie, YouTube, Instagram, LinkedIn, Discord)
- ADW Runner with token/cost tracking
- Persistent memory system
- Setup wizard (CLI + web)
