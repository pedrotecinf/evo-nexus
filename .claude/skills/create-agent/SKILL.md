---
name: create-agent
description: "Create a new custom agent for the workspace. Guides the user through defining agent name, domain, personality, skills, model, and memory folder. Use when the user says 'create an agent', 'new agent', 'add an agent', 'I need a custom agent', or wants to create a specialized agent for a specific domain."
---

# Create Custom Agent

Guide the user through creating a new custom agent that extends the workspace with a specialized domain.

## What You're Building

A custom agent is a `.md` file in `.claude/agents/` with the `custom-` prefix. It has:
- A system prompt defining personality, domain, and behavior
- A slash command in `.claude/commands/`
- A persistent memory folder in `.claude/agent-memory/`
- Optional skills it can use

Custom agents are gitignored (the `custom-` prefix triggers this) — they're personal to your workspace.

## Step 1: Understand the Agent

Ask the user:
1. **What domain should this agent cover?** (e.g., "DevOps monitoring", "customer support", "legal review")
2. **What name?** Suggest a short, memorable name. The final file will be `custom-{name}.md`
3. **What should it do?** Key responsibilities and tasks
4. **What personality/tone?** (technical, friendly, formal, concise)
5. **Which model?** Default: `sonnet`. Use `opus` for complex reasoning tasks
6. **What color?** For the dashboard card. Suggest a hex color that fits the domain (e.g., `#FF6B6B` for alerts, `#4ECDC4` for monitoring)

## Step 2: Generate the Agent File

Create `.claude/agents/custom-{name}.md`:

```markdown
---
name: custom-{name}
description: "{one-line description of the agent's domain}"
model: sonnet
color: "{hex color}"
---

# {Agent Display Name}

You are {Agent Display Name}, a specialized agent for {domain description}.

## Your Domain

{Detailed description of what this agent handles. Be specific about:}
- What tasks fall under this domain
- What data sources it accesses
- What outputs it produces

## Personality

- {personality trait 1}
- {personality trait 2}
- {personality trait 3}

## How You Work

1. Always read your memory folder first: `.claude/agent-memory/custom-{name}/`
2. {workflow step}
3. {workflow step}
4. Save learnings to your memory folder

## Skills You Can Use

{List relevant existing skills or note that custom skills can be created}

## Anti-patterns

- Do NOT {thing to avoid}
- Do NOT {thing to avoid}
- Do NOT mix with other agent domains
```

## Step 3: Generate the Slash Command

Create `.claude/commands/custom-{name}.md`:

```markdown
---
description: "{short description} — custom agent"
allowed-tools: ["Agent"]
---

Launch the custom-{name} agent.

Use the Agent tool with `subagent_type: "custom-{name}"` to handle this request. The agent has its own memory in `.claude/agent-memory/custom-{name}/` and its system prompt in `.claude/agents/custom-{name}.md`.
```

## Step 4: Register in Dashboard (core agents only)

If the agent does NOT have the `custom-` prefix (i.e., it's a core agent that will be committed to the repo), add it to `AGENT_META` in `dashboard/frontend/src/pages/Agents.tsx`:

1. Add the icon import from `lucide-react` at the top of the file
2. Add an entry to the `AGENT_META` object:

```typescript
'{agent-name}': {
  icon: {IconName},
  color: '{hex color from frontmatter}',
  colorMuted: '{color}1F',
  glowColor: '{color}26',
  command: '/{command-name}',
  label: '{domain label}',
},
```

Without this step, the agent card in the dashboard will show a generic icon and no `/command` badge.

**Skip this step for custom agents** — they use `DEFAULT_META` with dynamic colors from frontmatter automatically.

## Step 5: Create Memory Folder

```bash
mkdir -p .claude/agent-memory/custom-{name}
```

The memory folder is already gitignored (`.claude/agent-memory/` is in `.gitignore`).

## Step 6: Verify

Run a quick check:
```bash
ls -la .claude/agents/custom-{name}.md
ls -la .claude/commands/custom-{name}.md
ls -d .claude/agent-memory/custom-{name}/
```

Tell the user:
- Agent created: `custom-{name}`
- Invoke with: `/custom-{name}` in Claude Code
- Visible in dashboard: Agents page (with "custom" badge)
- Memory: `.claude/agent-memory/custom-{name}/`
- To delete: remove the 3 paths above

## Agent Naming Convention

| Pattern | Example | Domain |
|---------|---------|--------|
| `custom-devops` | DevOps agent | Infrastructure monitoring |
| `custom-support` | Support agent | Customer tickets |
| `custom-legal` | Legal agent | Contract review |
| `custom-data` | Data agent | Analytics, ETL |
| `custom-qa` | QA agent | Testing, quality |

Rules:
- Always use `custom-` prefix (required for gitignore and dashboard badge)
- Use lowercase, hyphen-separated names
- Keep names short (1-2 words after prefix)
- Avoid names that conflict with core agents

## Core Agents (Do Not Duplicate)

These domains are already covered by core agents:

| Agent | Domain |
|-------|--------|
| `clawdia-assistant` | Operations, calendar, email, tasks |
| `flux-finance` | Finance, Stripe, ERP |
| `atlas-project` | Projects, GitHub, Linear |
| `pulse-community` | Community, Discord, WhatsApp |
| `pixel-social-media` | Social media, content |
| `sage-strategy` | Strategy, OKRs |
| `nex-sales` | Sales, pipeline |
| `mentor-courses` | Courses, education |
| `kai-personal-assistant` | Personal, health, habits |

If the user's request overlaps with a core agent, suggest using that agent instead or creating the custom agent for the specific subset that's different.

## Important Notes

- Custom agents (`custom-*`) are gitignored — they won't be pushed to the repo
- Custom commands (`custom-*`) are also gitignored
- Agent memory is always gitignored (all of `.claude/agent-memory/`)
- The dashboard auto-discovers custom agents and shows them with a gray "custom" badge
- Custom agents can use any existing skill — just list them in the system prompt
- To create custom skills for the agent, use the skill naming convention: `.claude/skills/{prefix}-{action}/`
