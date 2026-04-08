---
name: pulse-monthly
description: "Monthly community report — aggregates Discord and WhatsApp activity for the full month: MAM, growth, sentiment trends, top contributors, product insights, docs gaps, and week-over-week evolution. Generates an HTML report using the Evolution brand. Use when user says 'community monthly', 'monthly community report', 'monthly pulse', or any reference to monthly community analysis."
---

# Monthly Community Report

Monthly routine that analyzes all Discord and WhatsApp activity for the month and generates a complete HTML report with trends, insights, and recommendations.

**Always respond in English.**

## Workflow

### Step 1 — Determine period

- Mês de referência: mês anterior ao atual (ex: se hoje é 01/04, analisar março)
- Período: primeiro ao último dia do mês de referência
- Dividir o mês em semanas (W1, W2, W3, W4/W5) para análise de tendência

### Step 2 — Collect Discord data (30 dias)

Usar a skill `/discord-get-messages` para buscar mensagens do mês nos canais principais.

Guild ID: `YOUR_GUILD_ID`

Canais a monitorar:
- Todos os canais de texto da comunidade (chat-pt, chat-en, chat-es, help, feedback, suggestions, showcase, news)
- Canal de novos membros (`🆕・new-members`)

Para cada canal, buscar mensagens paginadas (100 por request) até cobrir o mês completo.

### Step 3 — Collect WhatsApp data (30 dias)

Usar a skill `/int-whatsapp`:

```bash
python3 {project-root}/.claude/skills/int-whatsapp/scripts/whatsapp_client.py messages_30d
python3 {project-root}/.claude/skills/int-whatsapp/scripts/whatsapp_client.py stats --start YYYY-MM-01 --end YYYY-MM-DD
python3 {project-root}/.claude/skills/int-whatsapp/scripts/whatsapp_client.py groups --start YYYY-MM-01 --end YYYY-MM-DD
```

### Step 4 — Calculate monthly KPIs

1. **MAM (Monthly Active Members)**: membros únicos que enviaram mensagem no mês (Discord + WhatsApp)
2. **Total Mensagens**: Discord + WhatsApp separados e somados
3. **Novos Membros**: entradas em `🆕・new-members` do Discord no mês
4. **Taxa de Resolução**: perguntas respondidas / total em #help (meta: >80%)
5. **Comparison**: comparar todos os KPIs com o mês anterior (ler relatório anterior se existir em `workspace/community/reports/monthly/`)

### Step 5 — Weekly evolution

Para cada semana do mês, calcular:
- Mensagens
- Membros ativos
- Novos membros
- Sentimento (positivo/neutro/negativo)
- Tickets suporte abertos

Apresentar em tabela para visualizar tendência ao longo do mês.

### Step 6 — Metrics by platform

**Discord:**
- Total de mensagens, membros ativos, tickets suporte, sentimento
- Canal mais ativo, canal mais ajudado

**WhatsApp:**
- Total de mensagens, grupos ativos, participantes únicos, sentimento
- Grupo mais ativo

### Step 7 — Top contributors

Rankear por volume de mensagens + respostas dadas em #help:
- Top 10 membros mais ativos
- Plataforma principal (Discord/WhatsApp)
- Destaque (helper, novo membro ativo, líder de tópico)

### Step 8 — Month's topics

Agrupar todas as discussões por tema:
- Top 10 tópicos mais discutidos
- Frequência, sentimento por tópico
- Fontes (Discord, WhatsApp, ou ambos)

### Step 9 — Product insights

1. **Features solicitadas**: pedidos espontâneos de funcionalidades (com frequência)
2. **Bugs reportados**: problemas técnicos mencionados (com frequência)
3. **Docs gaps**: perguntas recorrentes cuja resposta deveria estar na documentação

### Step 10 — Sentiment trend

Para cada semana do mês:
- % positivo, % neutro, % negativo
- Tendência: melhorando, estável, piorando

### Step 11 — Analysis and recommendations

**Análise** (3-5 bullets):
- Crescimento ou retração da comunidade
- Padrões de engajamento (dias/horários de pico)
- Evolução do sentimento
- Eficácia do suporte
- Discord vs WhatsApp: qual plataforma cresce mais?

**Recomendações** (3-5 bullets):
- Ações para melhorar engajamento
- Docs a criar/atualizar
- Features a priorizar baseado no feedback
- Membros a reconhecer/engajar

### Step 12 — Generate HTML report

Read the template at `.claude/templates/html/community-monthly-report.html` e substituir TODOS os `{{PLACEHOLDER}}`.

Para rows dinâmicas, usar o padrão das outras skills pulse:

**Semanas:**
```html
<tr>
  <td>Semana 1 (01-07/MM)</td>
  <td class="right">XXX</td>
  <td class="right">XX</td>
  <td class="right">X</td>
  <td class="right"><span class="badge green">Positivo</span></td>
  <td class="right">X</td>
</tr>
```

**Top contributors:**
```html
<tr>
  <td>Nome</td>
  <td><span class="badge blue">Discord</span></td>
  <td class="right">XXX</td>
  <td class="right">XX</td>
  <td><span class="badge green">Helper</span></td>
</tr>
```

**Tópicos:**
```html
<div class="list-item">Tópico — XX menções, sentimento positivo/misto/negativo</div>
```

**Features/Bugs:**
```html
<div class="list-item">Descrição — X menções (Discord/WhatsApp)</div>
```

**Docs gaps:**
```html
<tr>
  <td>Pergunta recorrente</td>
  <td>Discord #help / WhatsApp</td>
  <td class="right">X vezes</td>
  <td><span class="badge yellow">Instalação</span></td>
</tr>
```

### Step 13 — Save

Save em:
```
workspace/community/reports/monthly/[C] YYYY-MM-community-monthly.html
```

Create the directory `workspace/community/reports/monthly/` if it does not exist.

### Step 14 — Confirm

```
## Community Monthly gerado

**Arquivo:** workspace/community/reports/monthly/[C] YYYY-MM-community-monthly.html
**Mês:** {mês de referência}
**MAM:** {N} ({delta}%) | **Mensagens:** {N} | **Novos:** {N}
**Sentimento:** {tendência} | **Resolução:** {X}%
**Destaques:** {N} features, {N} bugs, {N} docs gaps
```

### Notify via Telegram

Upon completion, send a short summary via Telegram to the user:
- Use the Telegram MCP: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Format: emoji + "Community Monthly" + MAM + sentiment + highlights (2-3 lines)
