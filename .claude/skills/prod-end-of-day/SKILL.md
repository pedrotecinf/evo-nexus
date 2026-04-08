---
name: prod-end-of-day
description: "End-of-day consolidation — analyzes agent memory, ADW logs, meetings, tasks, and learnings to generate a complete daily log. Trigger when user says 'end of day', 'wrap up', 'done for today', 'goodnight', 'shutdown', or anything that signals finishing a work session."
---

# End of Day — Daily Consolidation

End-of-day routine that consolidates everything that happened during the day: agent memory, ADW logs, meetings, tasks, and learnings.

**Always respond in English.**

## Step 1 — Collect data do dia (silenciosamente)

Ler todas as fontes disponíveis sem narrar cada passo:

### 1a. Memória dos agentes
Ler os arquivos de memória recentes de cada agente em `.claude/agent-memory/`:
- `flux-financeiro/` — decisões financeiras do dia
- `atlas-project/` — atualizações de projetos
- `kai-personal-assistant/` — se houver algo relevante
- Qualquer outro agente que tenha sido usado

### 1b. Logs de ADW
Ler o log JSONL de hoje em `ADWs/logs/YYYY-MM-DD.jsonl` para ver quais rotinas rodaram, duração e status.

### 1c. Reuniões do dia
Verificar `workspace/meetings/summaries/` e `workspace/meetings/fathom/` do dia para reuniões que foram sincronizadas.

### 1d. Tarefas
Rodar `todoist today` para ver tarefas concluídas e pendentes do dia.

### 1e. Git changes do dia
Rodar `git diff --stat` e `git log --oneline --since="today 00:00"` pra ver:
- Arquivos criados, modificados ou deletados hoje
- Commits feitos (mensagens e autores)
- Mudanças não commitadas (working tree)

Isso dá o panorama real do que mudou no workspace — mais preciso que ler a conversa.

### 1f. Sessão atual
Revisar a conversa da sessão atual — o que foi discutido, decidido e feito.

## Step 2 — Consolidate learnings

Analyze tudo que foi coletado e identificar:
- **Decisões tomadas** — o que foi decidido e por quê
- **Aprendizados** — padrões, correções, feedbacks que devem ser lembrados
- **Pessoas** — contexto novo sobre pessoas do time
- **Pendências reais** — coisas que ficaram em aberto de verdade (não inventar)

## Step 3 — Save memória

Se houver decisões, aprendizados ou feedbacks relevantes, salvar na memória persistente em `memory/` seguindo o sistema de memória do workspace (ver `prod-memory-management`).

Não duplicar — verificar se já existe memória similar antes de criar.

## Step 4 — Generate daily log

Read the template at `.claude/templates/end-of-day-log.md` e preencher com os dados consolidados.

Save em:
```
workspace/daily-logs/[C] YYYY-MM-DD.md
```

O log deve incluir:
- O que foi feito (projetos, tarefas, reuniões)
- Arquivos criados ou alterados
- Rotinas ADW que rodaram (com status)
- Pendências (só se reais)
- Onde retomar amanhã

## Step 5 — Organize tasks

Rodar `/prod-review-todoist` para garantir que tarefas criadas durante o dia estão categorizadas e traduzidas.

## Step 6 — Confirm

Present a short summary:

```
## Dia encerrado

**Log:** workspace/daily-logs/[C] YYYY-MM-DD.md
**Rotinas ADW:** {N} executadas ({status})
**Tarefas:** {concluídas}/{total} concluídas
**Memórias:** {N} criadas/atualizadas
**Aprendizados:** {N} registrados

**Amanhã:** {frase sobre onde retomar}
```


### Notify via Telegram

Upon completion, send a short summary via Telegram to the user:
- Use the Telegram MCP: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Format: emoji + routine name + main result (1-3 lines)
- If the routine had no updates, send anyway with "no updates"
