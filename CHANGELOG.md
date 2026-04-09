# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
