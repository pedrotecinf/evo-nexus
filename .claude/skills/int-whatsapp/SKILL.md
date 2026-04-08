---
name: int-whatsapp
description: "Query WhatsApp group messages via Evolution Foundation API. Fetch messages, list groups, get stats by day/group/participant. Use when user asks about WhatsApp messages, group activity, WhatsApp community, 'mensagens do WhatsApp', 'grupos WhatsApp', 'atividade WhatsApp', or when community analysis needs WhatsApp data alongside Discord."
---

# WhatsApp Messages API

Integração com a API de mensagens WhatsApp da Evolution Foundation para consultar mensagens de grupos, listar grupos ativos e gerar estatísticas.

## Setup

Requer variável de ambiente:
```bash
export WHATSAPP_API_KEY="your_api_key_here"
```

## API Client

Use o script Python para todas as operações:

```bash
python3 {project-root}/.claude/skills/int-whatsapp/scripts/whatsapp_client.py <command> [args]
```

### Comandos disponíveis

#### Mensagens
```bash
# Últimas 24 horas (todas as mensagens)
python3 scripts/whatsapp_client.py messages_24h

# Últimas 24h de um grupo específico
python3 scripts/whatsapp_client.py messages_24h --group "120363140928731556@g.us"

# Últimos 7 dias
python3 scripts/whatsapp_client.py messages_7d

# Últimos 30 dias
python3 scripts/whatsapp_client.py messages_30d

# Filtros avançados
python3 scripts/whatsapp_client.py messages --start 2026-04-01 --end 2026-04-08 --group "ID" --type conversation --page 1 --limit 50
```

#### Grupos
```bash
# Listar grupos ativos (últimos 7 dias por padrão)
python3 scripts/whatsapp_client.py groups

# Grupos ativos em período específico
python3 scripts/whatsapp_client.py groups --start 2026-04-01 --end 2026-04-08
```

Retorna: groupId, instance, total de mensagens, participantes únicos.

#### Estatísticas
```bash
# Stats dos últimos 7 dias
python3 scripts/whatsapp_client.py stats

# Stats de período específico
python3 scripts/whatsapp_client.py stats --start 2026-04-01 --end 2026-04-08
```

Retorna: total de mensagens, breakdown por dia, por grupo, por tipo de mensagem, e top 20 participantes.

## Tipos de mensagem

| messageType | Descrição |
|---|---|
| `conversation` | Mensagem de texto |
| `imageMessage` | Imagem |
| `videoMessage` | Vídeo |
| `audioMessage` | Áudio |
| `documentMessage` | Documento/arquivo |
| `stickerMessage` | Figurinha |
| `reactionMessage` | Reação |

## Integração com Community Pulse

Esta skill é usada pelas rotinas de comunidade (`pulse-daily`, `pulse-weekly`) para complementar os dados do Discord com atividade dos grupos WhatsApp. O fluxo é:

1. Buscar mensagens do período (`messages_24h` ou `messages_7d`)
2. Gerar stats (`stats`)
3. Incorporar no relatório de comunidade junto com Discord

## Limites da API

- **Paginação:** máximo 100 itens por página
- **Rate limit:** sem limite documentado, mas usar com moderação
- **Timeout:** 30 segundos
