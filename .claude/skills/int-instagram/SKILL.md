---
name: int-instagram
description: "Query Instagram Graph API — profile stats, recent posts, engagement, insights. Supports multi-account (OAuth via Social Auth App). Use when user asks about Instagram metrics, seguidores, posts, engagement, 'como tá o Instagram', 'métricas do insta', or any reference to Instagram analytics."
---

# Instagram Graph API

Integração com Instagram para monitorar perfis da empresa e do usuário. Suporta múltiplas contas via OAuth (Social Auth App).

## Setup

Contas configuradas via `make social-auth` (OAuth login com Facebook). Salva no `.env`:
```env
SOCIAL_INSTAGRAM_1_LABEL=your_account
SOCIAL_INSTAGRAM_1_ACCESS_TOKEN=YOUR_TOKEN
SOCIAL_INSTAGRAM_1_ACCOUNT_ID=YOUR_ACCOUNT_ID
SOCIAL_INSTAGRAM_1_PAGE_TOKEN=YOUR_PAGE_TOKEN
```

## API Client

```bash
python3 {project-root}/.claude/skills/int-instagram/scripts/instagram_client.py <command> [args]
```

### Comandos

```bash
# Listar contas configuradas
instagram_client.py accounts

# Perfil (seguidores, bio, media count)
instagram_client.py profile [account_label]

# Últimos N posts com engagement
instagram_client.py recent_posts [account] [N]

# Top N posts por engagement
instagram_client.py top_posts [account] [N]

# Insights de um post específico
instagram_client.py post_insights POST_ID [account]

# Insights da conta (impressões, alcance, profile views — 30d)
instagram_client.py account_insights [account]

# Resumo de todas as contas
instagram_client.py summary
```

## Métricas-chave
- Seguidores (delta via snapshots diários)
- Engagement rate: (likes + comments) / followers
- Alcance e impressões (via account insights)
- Profile views
- Melhor post do período
- Reels vs posts estáticos
- Frequência de publicação

## Rate Limits
- Endpoints Instagram Platform: `4800 × impressões` por 24h
- Business Discovery / Hashtag: 200 calls/hour/user
