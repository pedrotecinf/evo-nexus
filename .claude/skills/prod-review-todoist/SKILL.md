---
name: prod-review-todoist
description: "Review and organize Todoist tasks in the Evolution project. Finds uncategorized, untranslated, or messy tasks and organizes them with proper categories, PT-BR translation, and actionable titles. Use when user says 'review todoist', 'organize tasks', 'todoist triage', 'clean up todoist', or similar."
---

# Review Todoist — Evolution Project Triage

Skill to review and organize tasks in the Evolution Todoist project. Identifies uncategorized, English-only, generic, or disorganized tasks and fixes them directly.

## Prerequisites

- CLI `todoist` instalado e autenticado
- Projeto `Evolution` existente no Todoist

## Workflow

### Step 1 — List Evolution project tasks

```bash
todoist tasks -p "Evolution"
```

### Step 2 — Identify tasks that need organization

A task needs triage if it meets **any** of these criteria:

1. **No category** — does not have `[Categoria]` prefix in the title
2. **In English** — title is not in PT-BR
3. **Generic/vague** — title does not make clear what to do (ex: "update thing", "send docs")
4. **No context** — no comment with origin/objective (especially tasks from sync-meetings)

### Step 3 — Organize each task

For each task that needs triage, apply:

#### 3a. Categorize

Add `[Categoria]` prefix to the title. Available categories:

| Category | When to use |
|---|---|
| `[Produto & Tech]` | Development, bugs, features, infra, deploy, code |
| `[Marketing]` | Content, campaigns, videos, social media, launches |
| `[Comercial]` | Pipeline, proposals, partnerships, leads, pricing |
| `[Financeiro]` | Accounts, invoices, payments, financial metrics |
| `[Operação]` | Internal processes, groups, access, team communication |
| `[Estratégia]` | OKRs, roadmap, analyses, strategic decisions |
| `[Comunidade]` | Discord, support, user feedback, beta testers |
| `[Roadmap]` | Future roadmap items, feature evaluation |

#### 3b. Translate to PT-BR

If the title is in English, translate to Brazilian Portuguese keeping clarity and objectivity.

**Before:** `Send event registration link to team member`
**After:** `[Operação] Enviar link de inscrição do evento para membro do time`

#### 3c. Make actionable

The title should make clear:
- **What** to do (infinitive verb)
- **For whom/where** (if applicable)
- **Expected result** (if not obvious)

**Before:** `Upload web panel; grant team member access`
**After:** `[Operação] Publicar painel web do evento e liberar acesso para membro do time`

#### 3d. Apply the update

```bash
todoist update <task-id> --content "[Categoria] Título traduzido e acionável"
```

### Step 4 — Execute directly

**Fundamental rule: execute the organization directly, without an intermediate report.**

Do not list tasks before organizing. Do not ask for confirmation on each one. Organize all at once and confirm at the end.

### Step 5 — Save artefato

Save um relatório curto em `workspace/daily-logs/[C] YYYY-MM-DD-todoist-review.md` com:

```markdown
# Triagem Todoist — YYYY-MM-DD

**Projeto:** Evolution
**Tarefas revisadas:** {N}
**Organizadas:** {M} (categorizadas, traduzidas ou reescritas)
**Já OK:** {K} (sem alteração necessária)

## Tarefas Organizadas

| Tarefa | Antes | Depois |
|--------|-------|--------|
| ... | ... | ... |
```

Create the directory `workspace/daily-logs/` if it does not exist.

### Step 6 — Final report (curto)

When finished, present only:

```
## Triagem Todoist — Concluído

**Projeto:** Evolution
**Tarefas revisadas:** {N}
**Organizadas:** {M} (categorizadas, traduzidas ou reescritas)
**Já OK:** {K} (sem alteração necessária)
```

If the user wants to see details of what changed, they ask.

## Important Rules

- **Default project is always `Evolution`** — do not move tasks to other projects
- **Always translate to PT-BR** — no exceptions
- **Do not modify already organized tasks** (que já têm `[Categoria]` e estão em PT-BR)
- **Do not complete or delete tasks** — only reorganize
- **Do not create new tasks** — only edit existing ones
- **Keep existing comments** — do not modify comments, only the title
- **If unsure about the category**, use `[Operação]` as fallback
- **Execute first, report after** — no intermediate report


### Notify via Telegram

Upon completion, send a short summary via Telegram to the user:
- Use the Telegram MCP: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Format: emoji + routine name + main result (1-3 lines)
- If the routine had no updates, send anyway with "no updates"
