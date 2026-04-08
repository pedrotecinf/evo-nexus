# Getting Started with OpenClaude

## Prerequisites

- **Claude Code CLI** — [Install Claude Code](https://claude.ai/claude-code)
- **Python 3.11+** with [uv](https://docs.astral.sh/uv/)
- **Node.js 18+** (for the dashboard)
- **API keys** for integrations you want to use

## Installation

### 1. Clone and Setup

```bash
git clone https://github.com/EvolutionAPI/open-claude.git
cd open-claude

# Interactive setup wizard
make setup
# Or: python setup.py
```

The wizard asks for:
- Your name and company
- Timezone and language
- Which agents to enable
- Which integrations to configure

It generates:
- `config/workspace.yaml` — central config
- `config/routines.yaml` — routine schedules
- `.env` — API keys (fill in after setup)
- `CLAUDE.md` — context file for Claude

### 2. Configure API Keys

Edit `.env` with your keys:

```bash
nano .env
```

At minimum, you need:
- No keys required for basic operation (agents, skills work without integrations)
- `DISCORD_BOT_TOKEN` — for community monitoring
- `STRIPE_SECRET_KEY` — for financial routines
- Social OAuth keys — via `make social-auth` or the dashboard

### 3. Start the Dashboard

```bash
make dashboard-app
```

Open http://localhost:8080 — the first run shows a setup wizard where you create your admin account and configure the workspace.

### 4. Start Automated Routines

```bash
make scheduler
```

This starts the scheduler that runs routines at their configured times (see `config/routines.yaml`).

### 5. Use Claude Code

Just open Claude Code in this directory. It reads `CLAUDE.md` automatically and has access to all agents and skills.

```bash
# Invoke agents directly
/ops           # Operations hub
/finance       # Financial analysis
/projects      # Project management
/community     # Community pulse
/social        # Social media

# Or let Claude route automatically based on your request
```

## Next Steps

- Read [Architecture](architecture.md) to understand how agents, skills, and routines work together
- Browse `.claude/skills/CLAUDE.md` for the full skill index
- Check `ROTINAS.md` for routine documentation
- Customize `config/routines.yaml` to adjust schedules
