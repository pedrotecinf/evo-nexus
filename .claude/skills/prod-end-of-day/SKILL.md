---
name: prod-end-of-day
description: "End-of-day consolidation — analyzes agent memory, ADW logs, meetings, tasks, and learnings to generate a complete daily log. Trigger when user says 'end of day', 'wrap up', 'encerra o dia', 'finaliza', 'done for today', 'goodnight', 'boa noite', 'shutdown', or anything that signals finishing a work session."
---

# End of Day — Consolidação do Dia

Rotina de encerramento que consolida tudo que aconteceu no dia: memória dos agentes, logs de ADW, reuniões, tarefas e aprendizados.

**Sempre responder em pt-BR.**

## Step 1 — Coletar dados do dia (silenciosamente)

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
Verificar `09 Reuniões/summaries/` e `09 Reuniões/fathom/` do dia para reuniões que foram sincronizadas.

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

## Step 2 — Consolidar aprendizados

Analisar tudo que foi coletado e identificar:
- **Decisões tomadas** — o que foi decidido e por quê
- **Aprendizados** — padrões, correções, feedbacks que devem ser lembrados
- **Pessoas** — contexto novo sobre pessoas do time
- **Pendências reais** — coisas que ficaram em aberto de verdade (não inventar)

## Step 3 — Salvar memória

Se houver decisões, aprendizados ou feedbacks relevantes, salvar na memória persistente em `memory/` seguindo o sistema de memória do workspace (ver `prod-memory-management`).

Não duplicar — verificar se já existe memória similar antes de criar.

## Step 4 — Gerar log do dia

Ler o template em `.claude/templates/end-of-day-log.md` e preencher com os dados consolidados.

Salvar em:
```
01 Daily Logs/[C] YYYY-MM-DD.md
```

O log deve incluir:
- O que foi feito (projetos, tarefas, reuniões)
- Arquivos criados ou alterados
- Rotinas ADW que rodaram (com status)
- Pendências (só se reais)
- Onde retomar amanhã

## Step 5 — Organizar tarefas

Rodar `/prod-review-todoist` para garantir que tarefas criadas durante o dia estão categorizadas e traduzidas.

## Step 6 — Confirmar

Apresentar resumo curto:

```
## Dia encerrado

**Log:** 01 Daily Logs/[C] YYYY-MM-DD.md
**Rotinas ADW:** {N} executadas ({status})
**Tarefas:** {concluídas}/{total} concluídas
**Memórias:** {N} criadas/atualizadas
**Aprendizados:** {N} registrados

**Amanhã:** {frase sobre onde retomar}
```


### Notificar no Telegram

Ao finalizar, enviar resumo curto no Telegram para o usuário:
- Usar o MCP do Telegram: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Formato: emoji + nome da rotina + resultado principal (1-3 linhas)
- Se a rotina não teve novidades, enviar mesmo assim com "sem novidades"
