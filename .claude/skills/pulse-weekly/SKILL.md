---
name: pulse-weekly
description: "Weekly community analysis report — aggregates Discord AND WhatsApp activity, engagement metrics, sentiment trends, top contributors, product insights, and docs gaps. Generates an HTML report using the Evolution brand. Use when user says 'relatório semanal comunidade', 'weekly community', 'análise da comunidade', 'como foi a semana no discord', 'como foi o whatsapp', or any reference to weekly community analysis."
---

# Relatório Semanal da Comunidade

Rotina semanal que analisa a atividade do Discord e WhatsApp dos últimos 7 dias e gera um relatório HTML completo.

**Sempre responder em pt-BR.**

## Fluxo

### Passo 1 — Coletar dados da semana

Usar a skill `/discord-get-messages` para buscar mensagens dos últimos 7 dias nos canais principais.

Guild ID: `YOUR_GUILD_ID`

Canais a monitorar:
- Todos os canais de texto da comunidade (chat-pt, chat-en, chat-es, help, feedback, suggestions, showcase, news)
- Canal de novos membros (`🆕・new-members`)

Para cada canal, buscar mensagens paginadas (100 por request) até cobrir 7 dias.

### Passo 1b — Coletar dados do WhatsApp (7 dias)

Usar a skill `/int-whatsapp` para buscar mensagens e stats dos últimos 7 dias:

```bash
python3 {project-root}/.claude/skills/int-whatsapp/scripts/whatsapp_client.py messages_7d
python3 {project-root}/.claude/skills/int-whatsapp/scripts/whatsapp_client.py stats --start $(date -u -v-7d '+%Y-%m-%d') --end $(date -u '+%Y-%m-%d')
python3 {project-root}/.claude/skills/int-whatsapp/scripts/whatsapp_client.py groups --start $(date -u -v-7d '+%Y-%m-%d') --end $(date -u '+%Y-%m-%d')
```

Incluir no relatório como seção separada "WhatsApp" com: grupos ativos, total mensagens, participantes únicos, tópicos, perguntas de suporte.

### Passo 2 — Calcular métricas

1. **Crescimento**: total membros (estimativa), novos vs saídas, churn net
2. **WAM (Weekly Active Members)**: membros únicos que enviaram mensagem
3. **Communicators**: % dos visitantes que conversam (meta: 50%)
4. **Taxa de resolução**: perguntas respondidas / total em #help (meta: >80%)
5. **Tempo de primeira resposta**: mediana do tempo entre pergunta e primeira resposta
6. **Mensagens por membro ativo**: total msgs / WAM (meta: >4)

### Passo 3 — Analisar sentimento e tópicos

Para cada dia da semana:
1. **Sentimento**: classificar mensagens como positivo/neutro/negativo
2. **Tópicos**: agrupar discussões por tema, contar frequência

Consolidar:
- Top 5 tópicos com barra de sentimento
- Tendência de sentimento ao longo da semana

### Passo 4 — Identificar destaques

1. **Top 5 membros mais ativos**: por volume de mensagens + respostas dadas
2. **Novos membros que contribuíram**: quem é novo e já participou
3. **Membros em risco de churn**: previamente ativos, inativos esta semana

### Passo 5 — Extrair insights para o produto

Analisar as mensagens e identificar:
1. **Features mais solicitadas**: pedidos espontâneos de funcionalidades
2. **Bugs reportados**: problemas técnicos mencionados
3. **Docs gap**: perguntas cuja resposta deveria estar na documentação (indicar frequência)

### Passo 6 — Comparativo

Se existirem relatórios anteriores em `03 Comunidade/reports/weekly/`, comparar:
- WAM esta semana vs anterior
- Novos membros vs anterior
- Taxa de resolução vs anterior
- Tempo de resposta vs anterior

### Passo 7 — Gerar relatório HTML

Ler o template em `.claude/templates/html/community-weekly-report.html`.

Substituir os placeholders `{{...}}` com os dados reais.

Logo disponível em: `02 Projects/Evolution Foundation/Logos finais/Favicon logo/SVG/Favicon Color 500.svg`

Salvar em:
```
03 Comunidade/reports/weekly/[C] YYYY-WXX-community-report.html
```

### Passo 8 — Resumo executivo

Apresentar no terminal:

```
## Relatório Semanal — Semana {WXX}

Membros: {N} ({+/-}) | WAM: {N} ({X}%)
Resolução: {X}% | 1st response: {X} min
Sentimento: {label}
Top: {tópico 1}, {tópico 2}, {tópico 3}
Insights: {N} features, {N} bugs, {N} docs gaps

Relatório salvo em 03 Comunidade/reports/weekly/
```

## Regras

- **Não responder mensagens** — apenas ler e analisar
- **Dados reais** — métricas baseadas em mensagens coletadas, sem inventar
- **Docs gap é ouro** — cada pergunta sem doc vira item de backlog
- **Comparar é fundamental** — sempre mostrar tendência vs semana anterior
- **Insights para produto** — a seção mais valiosa, cuidar bem


### Notificar no Telegram

Ao finalizar, enviar resumo curto no Telegram para o usuário:
- Usar o MCP do Telegram: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Formato: emoji + nome da rotina + resultado principal (1-3 linhas)
- Se a rotina não teve novidades, enviar mesmo assim com "sem novidades"
