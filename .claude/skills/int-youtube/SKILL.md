---
name: int-youtube
description: "Query YouTube Data API v3 — channel stats, recent videos, top videos, comments. Supports multi-account (OAuth or API Key). Use when user asks about YouTube metrics, canal YouTube, inscritos, views, vídeos, engagement, 'como tá o YouTube', 'métricas do canal', or any reference to YouTube analytics."
---

# YouTube Data API v3

Integração com YouTube para monitorar canais da Evolution e outros. Suporta múltiplas contas via OAuth (Social Auth App) ou API Key.

## Setup

Contas configuradas via `make social-auth` (OAuth login) ou manualmente no `.env`:
```env
SOCIAL_YOUTUBE_1_LABEL=Evolution API
SOCIAL_YOUTUBE_1_ACCESS_TOKEN=ya29...
SOCIAL_YOUTUBE_1_CHANNEL_ID=UC9kZHm3TnEt41ztGOLyQO9g
SOCIAL_YOUTUBE_1_REFRESH_TOKEN=1//0h...
```

## API Client

```bash
python3 {project-root}/.claude/skills/int-youtube/scripts/youtube_client.py <command> [args]
```

### Comandos

```bash
# Listar contas configuradas
youtube_client.py accounts

# Stats do canal (inscritos, views, total vídeos)
youtube_client.py channel_stats [account_label_or_index]

# Últimos N vídeos com métricas (via playlistItems — 3 units)
youtube_client.py recent_videos [account] [N]

# Top N vídeos por views
youtube_client.py top_videos [account] [N]

# Stats de vídeos específicos
youtube_client.py video_stats VIDEO_ID [VIDEO_ID...]

# Comentários de um vídeo
youtube_client.py comments VIDEO_ID [N]

# Resumo de todas as contas
youtube_client.py summary
```

### Output JSON exemplo
```json
{
  "account": "Evolution API",
  "channel_id": "UC9kZHm3TnEt41ztGOLyQO9g",
  "subscribers": 7450,
  "total_views": 132462,
  "video_count": 27,
  "videos": [
    {
      "id": "abc",
      "title": "...",
      "published": "2026-...",
      "views": 7180,
      "likes": 500,
      "comments": 164,
      "engagement_rate": 9.25,
      "url": "https://youtube.com/watch?v=abc"
    }
  ]
}
```

## Métricas-chave
- Inscritos (delta diário/semanal/mensal)
- Views total e por vídeo
- Engagement rate: (likes + comments) / views
- Melhor vídeo do período
- Frequência de publicação
- Comentários recentes (sentimento)

## Quota
- 10.000 units/dia (reset meia-noite Pacific Time)
- `playlistItems`: 1 unit (usado em vez de `search` que custa 100)
- `channels`, `videos`, `commentThreads`: 1 unit cada
- Cada paginação cobra novamente
