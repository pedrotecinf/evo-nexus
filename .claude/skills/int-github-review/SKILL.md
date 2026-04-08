---
name: int-github-review
description: "Review GitHub repos — PRs abertos, issues da comunidade, stars/forks, releases, contribuidores. Use when user says 'checa o github', 'review do github', 'como tão os repos', 'PRs abertos', 'issues do github', 'status dos repositórios', or any reference to checking GitHub repos status."
---

# GitHub Review — Status dos Repositórios

Skill para revisar o estado dos repositórios da organização no GitHub: PRs abertos, issues da comunidade, atividade, stars e releases.

**Sempre responder em pt-BR.**

## Repositórios monitorados

| Repo | Descrição |
|------|-----------|
| `YOUR_ORG/main-api` | Main API (open source) |
| `YOUR_ORG/crm-product` | CRM + AI agents |
| `YOUR_ORG/go-service` | Go microservice |
| `YOUR_ORG/crm-community` | CRM Community edition |
| `YOUR_ORG/methodology` | Development methodology |

## Fluxo

### Passo 1 — Coletar dados de cada repo

Para cada repositório, usar `gh` CLI para buscar:

```bash
# PRs abertos
gh pr list --repo YOUR_ORG/{repo} --state open --json number,title,author,createdAt,updatedAt,labels,reviewDecision --limit 20

# Issues abertas (últimas 20)
gh issue list --repo YOUR_ORG/{repo} --state open --json number,title,author,createdAt,updatedAt,labels,comments --limit 20

# Estatísticas do repo
gh api repos/YOUR_ORG/{repo} --jq '{stargazers_count, forks_count, open_issues_count, updated_at}'

# Último release
gh release list --repo YOUR_ORG/{repo} --limit 1 --json tagName,publishedAt,name

# Atividade recente (commits últimos 7 dias)
gh api "repos/YOUR_ORG/{repo}/commits?since=$(date -v-7d +%Y-%m-%dT00:00:00Z)&per_page=5" --jq 'length'
```

### Passo 2 — Analisar

Para cada repo, classificar:

1. **PRs abertos**: quantos, há quanto tempo, quem precisa revisar, review pendente
2. **Issues da comunidade**: bugs reportados, feature requests, perguntas
3. **Issues stale**: abertas há mais de 14 dias sem resposta
4. **Atividade**: commits na semana, se está ativo ou parado
5. **Crescimento**: stars/forks (comparar com dado anterior se disponível)

### Passo 3 — Relatório

Apresentar no formato:

```
## GitHub Review — {data}

### Resumo
| Repo | PRs | Issues | Stars | Commits (7d) | Status |
|------|-----|--------|-------|---------------|--------|

### PRs que precisam de atenção
| Repo | PR | Título | Autor | Dias aberto | Review |
|------|----|----|-------|-------------|--------|

### Issues da comunidade (sem resposta)
| Repo | Issue | Título | Dias sem resposta |
|------|-------|--------|-------------------|

### Issues mais votadas / comentadas
| Repo | Issue | Título | Comentários | Labels |
|------|-------|--------|------------|--------|

### Releases recentes
| Repo | Versão | Data |
|------|--------|------|

### Atividade (últimos 7 dias)
{resumo de atividade por repo — ativo/moderado/parado}
```

### Passo 4 — Gerar relatório HTML

Ler o template em `.claude/templates/html/github-review.html`.

Substituir os placeholders `{{...}}` com os dados reais coletados.

Classificações de tempo:
- PRs/Issues < 2 dias: `fresh` (verde)
- 2-5 dias: `aging` (amarelo)
- > 5 dias: `stale` (vermelho)

Classificações de atividade:
- > 10 commits/semana: `active` (verde)
- 1-10 commits: `moderate` (amarelo)
- 0 commits: `inactive` (vermelho)

Salvar HTML preenchido em:
```
02 Projects/github-reviews/[C] YYYY-MM-DD-github-review.html
```

Criar diretório se não existir.

## Regras

- **Usar `gh` CLI** — já autenticado no sistema
- **Não criar issues ou PRs** — apenas ler e reportar
- **PRs sem review > 2 dias = alerta** — destacar
- **Issues sem resposta > 7 dias = alerta** — destacar
- **Comparar com review anterior** se existir no diretório
- **Foco em ação** — o que precisa de atenção do responsável, não só números


### Notificar no Telegram

Ao finalizar, enviar resumo curto no Telegram para o usuário:
- Usar o MCP do Telegram: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Formato: emoji + nome da rotina + resultado principal (1-3 linhas)
- Se a rotina não teve novidades, enviar mesmo assim com "sem novidades"
