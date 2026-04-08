# Contributing to OpenClaude

Thank you for your interest in contributing to OpenClaude! This document provides guidelines for contributing.

## How to Contribute

### Reporting Issues

- Use [GitHub Issues](https://github.com/EvolutionAPI/open-claude/issues) to report bugs or request features
- Include steps to reproduce, expected behavior, and actual behavior
- Include your OS, Python version, and Node.js version

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Test locally (`make setup` + `make dashboard-app`)
5. Commit with a clear message
6. Push and open a PR

### What to Contribute

**High impact areas:**
- New agents for business domains (HR, Legal, Customer Success, Product)
- New integration clients (Slack, Outlook, HubSpot, QuickBooks)
- New skills for existing agents
- Dashboard improvements (new pages, charts, features)
- Documentation and guides
- Bug fixes
- Test coverage

### Creating a New Agent

1. Create `.claude/agents/my-agent.md` — follow the pattern in existing agents
2. Create `.claude/commands/my-agent.md` — slash command to invoke it
3. Add skills in `.claude/skills/prefix-*/SKILL.md`
4. Add routines in `ADWs/rotinas/my_routine.py`
5. Add HTML template in `.claude/templates/html/`
6. Update `config/routines.yaml.example` with the new routine

### Creating a New Skill

1. Create `.claude/skills/prefix-name/SKILL.md`
2. Follow the YAML frontmatter format (name, description)
3. Keep SKILL.md under 500 lines
4. Add examples if helpful

### Creating a New Integration

1. Create script in `.claude/skills/int-name/scripts/client.py`
2. Create `.claude/skills/int-name/SKILL.md`
3. Add required env vars to `.env.example`
4. Document in the skill's SKILL.md

## Code Style

- **Python**: Follow PEP 8, use type hints where helpful
- **TypeScript/React**: Follow existing patterns in `dashboard/frontend/`
- **Markdown**: Use clear headers, keep skills concise
- **Commits**: Use conventional commits (`feat:`, `fix:`, `docs:`)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
