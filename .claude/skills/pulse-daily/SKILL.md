---
name: pulse-daily
description: "Daily community pulse report — reads Discord AND WhatsApp messages from the last 24h, analyzes activity, sentiment, support questions, and top topics. Generates an HTML report using the Evolution brand. Use when user says 'community pulse', 'daily community report', or any reference to daily community health check."
---

# Daily Community Pulse

Daily routine that reads Discord and WhatsApp messages from the last 24h and generates an HTML community health report.

**Always respond in English.**

## Workflow

### Step 1 — Collect Discord data

Usar a skill `/discord-get-messages` para buscar mensagens das últimas 24h nos canais principais:

Canais a monitorar (Guild ID: `YOUR_GUILD_ID`):
- `💬・chat-pt` — chat principal PT
- `💬・chat-en` — chat principal EN
- `💬・chat-es` — chat principal ES
- `🆘・help` — suporte
- `🆘・feedback` — feedback
- `💡・suggestions` — sugestões
- `💎・showcase` — showcase
- `📢・news` — notícias

Para cada canal, buscar as últimas 100 mensagens e filtrar as das últimas 24h.

### Step 1b — Collect WhatsApp data

Usar a skill `/int-whatsapp` para buscar mensagens das últimas 24h:

```bash
python3 {project-root}/.claude/skills/int-whatsapp/scripts/whatsapp_client.py messages_24h
```

E também as estatísticas:
```bash
python3 {project-root}/.claude/skills/int-whatsapp/scripts/whatsapp_client.py stats --start $(date -u -v-1d '+%Y-%m-%d') --end $(date -u '+%Y-%m-%d')
```

Extrair: total de mensagens, grupos ativos, participantes únicos, tópicos discutidos, perguntas de suporte.

### Step 2 — Analyze

A partir das mensagens coletadas, calcular:

1. **Atividade**: total de mensagens (Discord + WhatsApp separados), membros únicos ativos, canal/grupo mais ativo
2. **Novos membros**: checar `🆕・new-members` para entradas do dia
3. **Suporte**: perguntas sem resposta em `🆘・help` (Discord) + perguntas nos grupos WhatsApp, tempo sem resposta
4. **Sentimento**: analisar o tom geral (positivo/neutro/negativo) com base no conteúdo de ambas as plataformas
5. **Top tópicos**: agrupar por tema as discussões mais frequentes de Discord + WhatsApp (máximo 6)
6. **WhatsApp**: grupos ativos, total mensagens, participantes únicos, tópicos — seção separada no relatório
7. **Saúde geral**: Normal (>80% positivo, <3 perguntas abertas), Atenção (sentimento misto ou 3-5 perguntas abertas), Crítico (sentimento negativo ou >5 perguntas sem resposta)

### Step 3 — Generate HTML report

Read the template at `.claude/templates/html/community-daily-pulse.html`.

Replace the placeholders `{{...}}` with the actual collected data.

Evolution logo available at: `workspace/projects/Evolution Foundation/Logos finais/Favicon logo/SVG/Favicon Color 500.svg`

Save o HTML preenchido em:
```
workspace/community/reports/daily/[C] YYYY-MM-DD-community-pulse.html
```

Criar diretório if it does not exist.

### Step 4 — Terminal summary

Present a short summary in the terminal:

```
## Pulso Diário — {data}

Saúde: {Normal/Atenção/Crítico}
Mensagens: {N} | Ativos: {N} | Novos: {N}
Suporte: {N} sem resposta
Sentimento: {emoji} {label}
Top: {tópico 1}, {tópico 2}, {tópico 3}

Report salvo em workspace/community/reports/daily/
```

## Rules

- **Do not reply to messages on Discord** — only read and analyze
- **Sentiment based on real content** — do not guess, analyze the messages
- **Unanswered questions = priority** — always highlight
- **Compare with average** — if previous reports exist in the directory, compare metrics
- **Empty channels = OK** — if a channel had no activity, do not report as a problem


### Notify via Telegram

Upon completion, send a short summary via Telegram to the user:
- Use the Telegram MCP: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Format: emoji + routine name + main result (1-3 lines)
- If the routine had no updates, send anyway with "no updates"
