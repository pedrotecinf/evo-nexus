---
name: prod-trends
description: "Weekly trends analysis — compares community, GitHub, and financial metrics week-over-week to detect patterns, risks and opportunities. Use when user says 'trends analysis', 'trends', 'how are the metrics', 'weekly comparison', 'metrics evolution', or as part of the weekly review routine."
---

# Trends Analysis — Weekly Comparison

Routine that compares community, GitHub, and financial metrics week-over-week to detect patterns, risks, and opportunities.

**Always respond in English.**

## Data Sources

### 1. Comunidade (Discord)
Ler relatórios anteriores em:
- `workspace/community/reports/daily/` — pulsos diários (HTML)
- `workspace/community/reports/weekly/` — relatórios semanais (HTML)

Extrair do HTML ou gerar a partir dos dados:
- Mensagens por dia (volume)
- Membros ativos (WAM)
- Perguntas sem resposta
- Sentimento geral
- Top tópicos recorrentes

### 2. GitHub
Ler relatórios anteriores em:
- `workspace/projects/github-reviews/` — reviews (HTML)

Extrair ou gerar:
- PRs abertos (tendência: acumulando ou sendo resolvidos?)
- Issues abertas vs fechadas
- Stars/forks (crescimento)
- Commits por semana (atividade do time)
- Tempo médio de PR aberto

### 3. Financeiro
Consultar dados via skills:
- `/int-stripe` — MRR, cobranças, reembolsos, assinaturas ativas
- `/int-omie` — contas a receber/pagar (se disponível)

Métricas:
- MRR (Monthly Recurring Revenue)
- Cobranças do mês vs mês anterior
- Reembolsos
- Assinaturas ativas (crescimento/churn)

### 4. Operacional (ADWs)
Ler métricas do runner:
- `ADWs/logs/metrics.json` — runs, success rate, avg time por rotina

## Workflow

### Step 1 — Collect the week's data atual

Buscar os dados mais recentes de cada fonte (últimos 7 dias).

### Step 2 — Collect the week's data anterior

Buscar os dados de 7-14 dias atrás pra comparação. Se não existirem (primeira execução), marcar como "baseline" e pular comparativo.

### Step 3 — Calculate trends

Para cada métrica, calcular:
- Valor atual vs anterior
- Variação absoluta e percentual
- Direção: ↑ (subindo), ↓ (descendo), = (estável)
- Classificação: 🟢 saudável, 🟡 atenção, 🔴 risco

**Critérios de classificação:**

| Métrica | 🟢 Saudável | 🟡 Atenção | 🔴 Risco |
|---------|------------|-----------|---------|
| WAM | estável ou ↑ | queda <10% | queda >10% |
| Perguntas sem resposta | <5 | 5-10 | >10 |
| Sentimento | positivo | neutro | negativo |
| PRs abertos | <10 | 10-20 | >20 acumulando |
| Issues sem resposta | <5 | 5-15 | >15 |
| Stars (semanal) | >10 | 5-10 | <5 |
| MRR | estável ou ↑ | queda <5% | queda >5% |
| Success rate ADWs | >90% | 70-90% | <70% |

### Step 4 — Detect patterns

Analyze as últimas semanas (quantas tiver) e identificar:
- **Tendências persistentes** — métrica subindo/descendo por 2+ semanas seguidas
- **Correlações** — ex: aumento de issues no GitHub + aumento de perguntas no Discord = possível bug
- **Anomalias** — pico ou queda incomum vs média
- **Sazonalidade** — padrões que se repetem (ex: segunda tem mais atividade)

### Step 5 — Generate HTML report

Read the template at `.claude/templates/html/trends-report.html`.
Replace the placeholders `{{...}}` with the actual data.

Classificação do health geral:
- Todos 🟢 ou maioria 🟢: `healthy` — "Saudável"
- Mix de 🟢 e 🟡: `mixed` — "Atenção"
- Qualquer 🔴: `risk` — "Risco"

**OBRIGATÓRIO:** Sempre gerar o HTML primeiro. Ler o template, substituir os placeholders, e salvar o arquivo HTML completo. Isso vale inclusive na primeira execução (baseline) — mesmo sem comparativo, preencher o scorecard com os valores atuais e "—" no anterior.

Save HTML em `workspace/daily-logs/[C] YYYY-WXX-trends.html`.

Depois, salvar também uma versão markdown resumida em `workspace/daily-logs/[C] YYYY-WXX-trends.md`:

```markdown
# Análise de Tendências — Semana {WXX}

## Resumo Executivo
{3 bullets: o que melhorou, o que piorou, oportunidade}

## Scorecard

| Área | Métrica | Atual | Anterior | Var | Trend | Status |
|------|---------|-------|----------|-----|-------|--------|
| Comunidade | WAM | {N} | {N} | {+/-X%} | ↑/↓/= | 🟢/🟡/🔴 |
| Comunidade | Perguntas s/ resposta | {N} | {N} | | | |
| Comunidade | Sentimento | {label} | {label} | | | |
| GitHub | PRs abertos | {N} | {N} | | | |
| GitHub | Issues s/ resposta | {N} | {N} | | | |
| GitHub | Stars (semana) | {N} | {N} | | | |
| Financeiro | MRR | R${N} | R${N} | {var%} | | |
| Financeiro | Assinaturas ativas | {N} | {N} | | | |
| Operacional | Success rate ADWs | {X}% | {X}% | | | |

## Padrões Detectados
- {padrão 1 com evidência}
- {padrão 2 com evidência}

## Riscos
- {risco com métrica de suporte}

## Oportunidades
- {oportunidade baseada nos dados}

## Recomendações
1. {ação concreta baseada nos dados}
2. {ação concreta}
```

### Step 6 — Save snapshot

Save um snapshot das métricas atuais em `memory/trends/YYYY-WXX.json` pra acumular histórico:

```json
{
  "week": "YYYY-WXX",
  "date": "YYYY-MM-DD",
  "community": {"wam": N, "messages": N, "unanswered": N, "sentiment": "positive"},
  "github": {"prs_open": N, "issues_open": N, "issues_unanswered": N, "stars_week": N, "commits_week": N},
  "financial": {"mrr": N, "subscriptions": N, "refunds": N},
  "operational": {"adw_runs": N, "adw_success_rate": N, "adw_avg_seconds": N}
}
```

Criar `memory/trends/` if it does not exist.

## Rules

- **First run = baseline** — no comparison, just collect and save snapshot
- **Real data** — do not fabricate metrics, use what is available
- **If a source has no data, skip** — do not block due to a missing report
- **Focus on action** — each insight should lead to a concrete recommendation
- **Do not alarm without evidence** — red only when the metric truly indicates risk


### Notify via Telegram

Upon completion, send a short summary via Telegram to the user:
- Use the Telegram MCP: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Format: emoji + routine name + main result (1-3 lines)
- If the routine had no updates, send anyway with "no updates"
