---
name: pulse-daily
description: "Daily community pulse report — reads Discord AND WhatsApp messages from the last 24h, analyzes activity, sentiment, support questions, and top topics. Generates an HTML report using the Evolution brand. Use when user says 'pulso da comunidade', 'community pulse', 'como tá o discord', 'como tá o whatsapp', 'relatório diário comunidade', or any reference to daily community health check."
---

# Pulso Diário da Comunidade

Rotina diária que lê as mensagens do Discord e WhatsApp das últimas 24h e gera um relatório HTML de saúde da comunidade.

**Sempre responder em pt-BR.**

## Fluxo

### Passo 1 — Coletar dados do Discord

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

### Passo 1b — Coletar dados do WhatsApp

Usar a skill `/int-whatsapp` para buscar mensagens das últimas 24h:

```bash
python3 {project-root}/.claude/skills/int-whatsapp/scripts/whatsapp_client.py messages_24h
```

E também as estatísticas:
```bash
python3 {project-root}/.claude/skills/int-whatsapp/scripts/whatsapp_client.py stats --start $(date -u -v-1d '+%Y-%m-%d') --end $(date -u '+%Y-%m-%d')
```

Extrair: total de mensagens, grupos ativos, participantes únicos, tópicos discutidos, perguntas de suporte.

### Passo 2 — Analisar

A partir das mensagens coletadas, calcular:

1. **Atividade**: total de mensagens (Discord + WhatsApp separados), membros únicos ativos, canal/grupo mais ativo
2. **Novos membros**: checar `🆕・new-members` para entradas do dia
3. **Suporte**: perguntas sem resposta em `🆘・help` (Discord) + perguntas nos grupos WhatsApp, tempo sem resposta
4. **Sentimento**: analisar o tom geral (positivo/neutro/negativo) com base no conteúdo de ambas as plataformas
5. **Top tópicos**: agrupar por tema as discussões mais frequentes de Discord + WhatsApp (máximo 6)
6. **WhatsApp**: grupos ativos, total mensagens, participantes únicos, tópicos — seção separada no relatório
7. **Saúde geral**: Normal (>80% positivo, <3 perguntas abertas), Atenção (sentimento misto ou 3-5 perguntas abertas), Crítico (sentimento negativo ou >5 perguntas sem resposta)

### Passo 3 — Gerar relatório HTML

Ler o template em `.claude/templates/html/community-daily-pulse.html`.

Substituir os placeholders `{{...}}` com os dados reais coletados.

Logo da Evolution disponível em: `02 Projects/Evolution Foundation/Logos finais/Favicon logo/SVG/Favicon Color 500.svg`

Salvar o HTML preenchido em:
```
03 Comunidade/reports/daily/[C] YYYY-MM-DD-community-pulse.html
```

Criar diretório se não existir.

### Passo 4 — Resumo no terminal

Apresentar resumo curto no terminal:

```
## Pulso Diário — {data}

Saúde: {Normal/Atenção/Crítico}
Mensagens: {N} | Ativos: {N} | Novos: {N}
Suporte: {N} sem resposta
Sentimento: {emoji} {label}
Top: {tópico 1}, {tópico 2}, {tópico 3}

Relatório salvo em 03 Comunidade/reports/daily/
```

## Regras

- **Não responder mensagens no Discord** — apenas ler e analisar
- **Sentimento baseado em conteúdo real** — não chutar, analisar as mensagens
- **Perguntas sem resposta = prioridade** — destacar sempre
- **Comparar com média** — se tiver relatórios anteriores no diretório, comparar métricas
- **Canais vazios = OK** — se um canal não teve atividade, não reportar como problema


### Notificar no Telegram

Ao finalizar, enviar resumo curto no Telegram para o usuário:
- Usar o MCP do Telegram: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Formato: emoji + nome da rotina + resultado principal (1-3 linhas)
- Se a rotina não teve novidades, enviar mesmo assim com "sem novidades"
