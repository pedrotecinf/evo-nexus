# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-04-08

### Added
- Initial open source release
- **9 Specialized Agents** — Ops, Finance, Projects, Community, Social, Strategy, Sales, Courses, Personal
- **126 Skills** organized by domain prefix (evo-, social-, fin-, int-, prod-, mkt-, gog-, obs-, discord-, pulse-, sage-)
- **27 Automated Routines** — daily, weekly, monthly ADWs with scheduler
- **17 HTML Report Templates** — dark-themed dashboards for every domain
- **Web Dashboard (OpenClaude)** — React + Flask app with:
  - Overview, Reports, Agents, Skills, Routines pages
  - Web terminal (xterm.js + WebSocket PTY)
  - Service management (start/stop scheduler, Telegram, Docker containers)
  - Auth system with roles, permissions, and audit log
  - Setup wizard (web + CLI)
- **Social Auth** — OAuth multi-account app for YouTube, Instagram, LinkedIn, Twitter, TikTok, Twitch
- **Integration Clients** — Stripe, Omie ERP, YouTube, Instagram, LinkedIn, Discord
- **Evo Method** — Complete dev framework (analysis, planning, architecture, implementation, QA)
- **ADW Runner** — Execution engine with token/cost tracking, JSONL logs, Telegram notifications
- **Persistent Memory** — Two-tier system (CLAUDE.md + memory/) with per-agent memory
- **Setup Wizard** — Interactive CLI (`make setup`) and web-based first-run configuration
- **Docker Support** — Dockerfile + docker-compose for VPS deployment
- **Config-driven Routines** — `config/routines.yaml` for declarative schedule definition
