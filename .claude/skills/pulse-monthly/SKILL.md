---
name: pulse-monthly
description: "Monthly community report — aggregates Discord and WhatsApp activity for the full month: MAM, growth, sentiment trends, top contributors, product insights, docs gaps, and week-over-week evolution. Generates an HTML report using the Evolution brand. Use when user says 'relatório mensal comunidade', 'community monthly', 'como foi o mês na comunidade', 'monthly pulse', 'relatório mensal discord', or any reference to monthly community analysis."
---

# Relatório Mensal da Comunidade

Rotina mensal que analisa toda a atividade do Discord e WhatsApp do mês e gera um relatório HTML completo com tendências, insights e recomendações.

**Sempre responder em pt-BR.**

## Fluxo

### Passo 1 — Determinar período

- Mês de referência: mês anterior ao atual (ex: se hoje é 01/04, analisar março)
- Período: primeiro ao último dia do mês de referência
- Dividir o mês em semanas (W1, W2, W3, W4/W5) para análise de tendência

### Passo 2 — Coletar dados do Discord (30 dias)

Usar a skill `/discord-get-messages` para buscar mensagens do mês nos canais principais.

Guild ID: `YOUR_GUILD_ID`

Canais a monitorar:
- Todos os canais de texto da comunidade (chat-pt, chat-en, chat-es, help, feedback, suggestions, showcase, news)
- Canal de novos membros (`🆕・new-members`)

Para cada canal, buscar mensagens paginadas (100 por request) até cobrir o mês completo.

### Passo 3 — Coletar dados do WhatsApp (30 dias)

Usar a skill `/int-whatsapp`:

```bash
python3 {project-root}/.claude/skills/int-whatsapp/scripts/whatsapp_client.py messages_30d
python3 {project-root}/.claude/skills/int-whatsapp/scripts/whatsapp_client.py stats --start YYYY-MM-01 --end YYYY-MM-DD
python3 {project-root}/.claude/skills/int-whatsapp/scripts/whatsapp_client.py groups --start YYYY-MM-01 --end YYYY-MM-DD
```

### Passo 4 — Calcular KPIs mensais

1. **MAM (Monthly Active Members)**: membros únicos que enviaram mensagem no mês (Discord + WhatsApp)
2. **Total Mensagens**: Discord + WhatsApp separados e somados
3. **Novos Membros**: entradas em `🆕・new-members` do Discord no mês
4. **Taxa de Resolução**: perguntas respondidas / total em #help (meta: >80%)
5. **Comparativo**: comparar todos os KPIs com o mês anterior (ler relatório anterior se existir em `03 Comunidade/reports/monthly/`)

### Passo 5 — Evolução semanal

Para cada semana do mês, calcular:
- Mensagens
- Membros ativos
- Novos membros
- Sentimento (positivo/neutro/negativo)
- Tickets suporte abertos

Apresentar em tabela para visualizar tendência ao longo do mês.

### Passo 6 — Métricas por plataforma

**Discord:**
- Total de mensagens, membros ativos, tickets suporte, sentimento
- Canal mais ativo, canal mais ajudado

**WhatsApp:**
- Total de mensagens, grupos ativos, participantes únicos, sentimento
- Grupo mais ativo

### Passo 7 — Top contribuidores

Rankear por volume de mensagens + respostas dadas em #help:
- Top 10 membros mais ativos
- Plataforma principal (Discord/WhatsApp)
- Destaque (helper, novo membro ativo, líder de tópico)

### Passo 8 — Tópicos do mês

Agrupar todas as discussões por tema:
- Top 10 tópicos mais discutidos
- Frequência, sentimento por tópico
- Fontes (Discord, WhatsApp, ou ambos)

### Passo 9 — Insights para produto

1. **Features solicitadas**: pedidos espontâneos de funcionalidades (com frequência)
2. **Bugs reportados**: problemas técnicos mencionados (com frequência)
3. **Docs gaps**: perguntas recorrentes cuja resposta deveria estar na documentação

### Passo 10 — Tendência de sentimento

Para cada semana do mês:
- % positivo, % neutro, % negativo
- Tendência: melhorando, estável, piorando

### Passo 11 — Análise e recomendações

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

### Passo 12 — Gerar relatório HTML

Ler o template em `.claude/templates/html/community-monthly-report.html` e substituir TODOS os `{{PLACEHOLDER}}`.

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

**Top contribuidores:**
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

### Passo 13 — Salvar

Salvar em:
```
03 Comunidade/reports/monthly/[C] YYYY-MM-community-monthly.html
```

Criar o diretório `03 Comunidade/reports/monthly/` se não existir.

### Passo 14 — Confirmar

```
## Community Monthly gerado

**Arquivo:** 03 Comunidade/reports/monthly/[C] YYYY-MM-community-monthly.html
**Mês:** {mês de referência}
**MAM:** {N} ({delta}%) | **Mensagens:** {N} | **Novos:** {N}
**Sentimento:** {tendência} | **Resolução:** {X}%
**Destaques:** {N} features, {N} bugs, {N} docs gaps
```

### Notificar no Telegram

Ao finalizar, enviar resumo curto no Telegram para o usuário:
- Usar o MCP do Telegram: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Formato: emoji + "Community Monthly" + MAM + sentimento + destaques (2-3 linhas)
