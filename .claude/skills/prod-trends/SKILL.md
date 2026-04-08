---
name: prod-trends
description: "Weekly trends analysis — compares community, GitHub, and financial metrics week-over-week to detect patterns, risks and opportunities. Use when user says 'análise de tendências', 'trends', 'como estão as métricas', 'comparativo semanal', 'evolução das métricas', or as part of the weekly review routine."
---

# Análise de Tendências — Comparativo Semanal

Rotina que compara métricas de comunidade, GitHub e financeiro semana a semana pra detectar padrões, riscos e oportunidades.

**Sempre responder em pt-BR.**

## Fontes de dados

### 1. Comunidade (Discord)
Ler relatórios anteriores em:
- `03 Comunidade/reports/daily/` — pulsos diários (HTML)
- `03 Comunidade/reports/weekly/` — relatórios semanais (HTML)

Extrair do HTML ou gerar a partir dos dados:
- Mensagens por dia (volume)
- Membros ativos (WAM)
- Perguntas sem resposta
- Sentimento geral
- Top tópicos recorrentes

### 2. GitHub
Ler relatórios anteriores em:
- `02 Projects/github-reviews/` — reviews (HTML)

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

## Fluxo

### Passo 1 — Coletar dados da semana atual

Buscar os dados mais recentes de cada fonte (últimos 7 dias).

### Passo 2 — Coletar dados da semana anterior

Buscar os dados de 7-14 dias atrás pra comparação. Se não existirem (primeira execução), marcar como "baseline" e pular comparativo.

### Passo 3 — Calcular tendências

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

### Passo 4 — Detectar padrões

Analisar as últimas semanas (quantas tiver) e identificar:
- **Tendências persistentes** — métrica subindo/descendo por 2+ semanas seguidas
- **Correlações** — ex: aumento de issues no GitHub + aumento de perguntas no Discord = possível bug
- **Anomalias** — pico ou queda incomum vs média
- **Sazonalidade** — padrões que se repetem (ex: segunda tem mais atividade)

### Passo 5 — Gerar relatório HTML

Ler o template em `.claude/templates/html/trends-report.html`.
Substituir os placeholders `{{...}}` com os dados reais.

Classificação do health geral:
- Todos 🟢 ou maioria 🟢: `healthy` — "Saudável"
- Mix de 🟢 e 🟡: `mixed` — "Atenção"
- Qualquer 🔴: `risk` — "Risco"

**OBRIGATÓRIO:** Sempre gerar o HTML primeiro. Ler o template, substituir os placeholders, e salvar o arquivo HTML completo. Isso vale inclusive na primeira execução (baseline) — mesmo sem comparativo, preencher o scorecard com os valores atuais e "—" no anterior.

Salvar HTML em `01 Daily Logs/[C] YYYY-WXX-trends.html`.

Depois, salvar também uma versão markdown resumida em `01 Daily Logs/[C] YYYY-WXX-trends.md`:

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

### Passo 6 — Salvar snapshot

Salvar um snapshot das métricas atuais em `memory/trends/YYYY-WXX.json` pra acumular histórico:

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

Criar `memory/trends/` se não existir.

## Regras

- **Primeira execução = baseline** — não tem comparativo, só coleta e salva snapshot
- **Dados reais** — não inventar métricas, usar o que está disponível
- **Se uma fonte não tem dados, pular** — não travar por falta de um relatório
- **Foco em ação** — cada insight deve levar a uma recomendação concreta
- **Não alarmar sem evidência** — 🔴 só quando métrica realmente indica risco


### Notificar no Telegram

Ao finalizar, enviar resumo curto no Telegram para o usuário:
- Usar o MCP do Telegram: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Formato: emoji + nome da rotina + resultado principal (1-3 linhas)
- Se a rotina não teve novidades, enviar mesmo assim com "sem novidades"
