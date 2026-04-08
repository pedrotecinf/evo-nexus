---
name: int-linkedin
description: "Query LinkedIn API — profile info, posts (when approved), org stats. Supports multi-account via OAuth. Use when user asks about LinkedIn metrics, perfil LinkedIn, posts LinkedIn, 'como tá o LinkedIn', or any reference to LinkedIn analytics."
---

# LinkedIn API

Integração com LinkedIn para monitorar perfil do usuário e (futuramente) Company Page. Multi-account via OAuth (Social Auth App).

## Setup

Contas configuradas via `make social-auth`. Salva no `.env`:
```env
SOCIAL_LINKEDIN_1_LABEL=Your Name
SOCIAL_LINKEDIN_1_ACCESS_TOKEN=YOUR_TOKEN
SOCIAL_LINKEDIN_1_PERSON_URN=urn:li:person:YOUR_URN
```

## API Client

```bash
python3 {project-root}/.claude/skills/int-linkedin/scripts/linkedin_client.py <command> [args]
```

### Comandos

```bash
linkedin_client.py accounts                    # Listar contas
linkedin_client.py profile [account]           # Perfil (nome, email, foto)
linkedin_client.py my_posts [account] [N]      # Posts recentes (requer scope w_member_social)
linkedin_client.py post_stats POST_URN         # Reactions/comments de um post
linkedin_client.py org_followers [account]     # Seguidores da org (requer Advertising API)
linkedin_client.py summary                     # Resumo de todas as contas
```

## Scopes disponíveis

| Scope | Status | Produto LinkedIn |
|-------|--------|-----------------|
| `openid profile email` | ✅ Ativo | Sign In with OpenID Connect |
| `w_member_social` | ✅ Ativo | Share on LinkedIn |
| `r_organization_social` | Pendente | Advertising API (request form) |
| `r_organization_admin` | Pendente | Advertising API (request form) |

## Limitações atuais
- **Posts:** Leitura de posts requer scope adicional não disponível no tier atual
- **Company Page:** Requer Advertising API (pendente aprovação)
- **Workaround:** Export CSV do LinkedIn Analytics pra dados de Company Page

## Nota sobre versioned API
- Base URL: `https://api.linkedin.com/rest/` (endpoints org/analytics)
- Headers obrigatórios: `Linkedin-Version: 202603`, `X-Restli-Protocol-Version: 2.0.0`
- Perfil pessoal usa `/v2/userinfo` (OpenID Connect)
