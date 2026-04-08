---
name: pulse-weekly
description: "Weekly community analysis report — aggregates Discord AND WhatsApp activity, engagement metrics, sentiment trends, top contributors, product insights, and docs gaps. Generates an HTML report using the Evolution brand. Use when user says 'weekly community', 'community analysis', 'weekly community report', or any reference to weekly community analysis."
---

# Weekly Community Report

Weekly routine that analyzes Discord and WhatsApp activity from the last 7 days and generates a complete HTML report.

**Always respond in English.**

## Workflow

### Step 1 — Collect the week's data

Usar a skill `/discord-get-messages` para buscar mensagens dos últimos 7 dias nos canais principais.

Guild ID: `YOUR_GUILD_ID`

Canais a monitorar:
- Todos os canais de texto da comunidade (chat-pt, chat-en, chat-es, help, feedback, suggestions, showcase, news)
- Canal de novos membros (`🆕・new-members`)

Para cada canal, buscar mensagens paginadas (100 por request) até cobrir 7 dias.

### Step 1b — Collect WhatsApp data (7 dias)

Usar a skill `/int-whatsapp` para buscar mensagens e stats dos últimos 7 dias:

```bash
python3 {project-root}/.claude/skills/int-whatsapp/scripts/whatsapp_client.py messages_7d
python3 {project-root}/.claude/skills/int-whatsapp/scripts/whatsapp_client.py stats --start $(date -u -v-7d '+%Y-%m-%d') --end $(date -u '+%Y-%m-%d')
python3 {project-root}/.claude/skills/int-whatsapp/scripts/whatsapp_client.py groups --start $(date -u -v-7d '+%Y-%m-%d') --end $(date -u '+%Y-%m-%d')
```

Incluir no relatório como seção separada "WhatsApp" com: grupos ativos, total mensagens, participantes únicos, tópicos, perguntas de suporte.

### Step 2 — Calculate metrics

1. **Crescimento**: total membros (estimativa), novos vs saídas, churn net
2. **WAM (Weekly Active Members)**: membros únicos que enviaram mensagem
3. **Communicators**: % dos visitantes que conversam (meta: 50%)
4. **Taxa de resolução**: perguntas respondidas / total em #help (meta: >80%)
5. **Tempo de primeira resposta**: mediana do tempo entre pergunta e primeira resposta
6. **Mensagens por membro ativo**: total msgs / WAM (meta: >4)

### Step 3 — Analyze sentimento e tópicos

Para cada dia da semana:
1. **Sentimento**: classificar mensagens como positivo/neutro/negativo
2. **Tópicos**: agrupar discussões por tema, contar frequência

Consolidar:
- Top 5 tópicos com barra de sentimento
- Sentiment trend ao longo da semana

### Step 4 — Identify highlights

1. **Top 5 membros mais ativos**: por volume de mensagens + respostas dadas
2. **Novos membros que contribuíram**: quem é novo e já participou
3. **Membros em risco de churn**: previamente ativos, inativos esta semana

### Step 5 — Extract product insights

Analyze as mensagens e identificar:
1. **Features mais solicitadas**: pedidos espontâneos de funcionalidades
2. **Bugs reportados**: problemas técnicos mencionados
3. **Docs gap**: perguntas cuja resposta deveria estar na documentação (indicar frequência)

### Step 6 — Comparison

Se existirem relatórios anteriores em `workspace/community/reports/weekly/`, comparar:
- WAM esta semana vs anterior
- Novos membros vs anterior
- Taxa de resolução vs anterior
- Tempo de resposta vs anterior

### Step 7 — Generate HTML report

Read the template at `.claude/templates/html/community-weekly-report.html`.

Replace the placeholders `{{...}}` with the actual data.

Logo available at: `workspace/projects/Evolution Foundation/Logos finais/Favicon logo/SVG/Favicon Color 500.svg`

Save em:
```
workspace/community/reports/weekly/[C] YYYY-WXX-community-report.html
```

### Step 8 — Executive summary

Present in the terminal:

```
## Report Semanal — Semana {WXX}

Membros: {N} ({+/-}) | WAM: {N} ({X}%)
Resolução: {X}% | 1st response: {X} min
Sentimento: {label}
Top: {tópico 1}, {tópico 2}, {tópico 3}
Insights: {N} features, {N} bugs, {N} docs gaps

Report salvo em workspace/community/reports/weekly/
```

## Rules

- **Do not reply to messages** — only read and analyze
- **Real data** — metrics based on collected messages, no fabrication
- **Docs gap is gold** — each question without docs becomes a backlog item
- **Comparison is fundamental** — always show trend vs previous week
- **Product insights** — a seção mais valiosa, cuidar bem


### Notify via Telegram

Upon completion, send a short summary via Telegram to the user:
- Use the Telegram MCP: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Format: emoji + routine name + main result (1-3 lines)
- If the routine had no updates, send anyway with "no updates"
