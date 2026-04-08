---
name: sage-strategy-digest
description: "Generate weekly strategy digest consolidating financial, product, community, and market data into strategic insights. Use when user says 'strategy digest', 'weekly strategy summary', 'company status', or as part of the weekly strategy review routine."
---

# Strategy Digest — Weekly Strategic Summary

Weekly routine that consolidates data from all areas into a strategic view for decision-making.

**Always respond in English.**

## Workflow

### Step 1 — Collect data de cada área

**Financeiro:**
- Consultar `/int-stripe` — MRR atual, variação, novas assinaturas, churn, reembolsos
- Se disponível, ler último relatório em `workspace/finance/`

**Produto:**
- Ler último `/int-linear-review` em `workspace/projects/linear-reviews/`
- Ler último `/int-github-review` em `workspace/projects/github-reviews/`
- Resumir: entregas da semana, blockers, PRs, issues da comunidade

**Comunidade:**
- Ler último relatório em `workspace/community/reports/weekly/`
- Resumir: WAM, sentimento, tópicos quentes, FAQ gaps

**Comercial:**
- Se existir pipeline em `workspace/projects/comercial/`, ler status
- Verificar parcerias ativas

**Tendências:**
- Ler último trends report em `workspace/daily-logs/`

### Step 2 — Analyze estrategicamente

Cruzar os dados e responder:
1. **Saúde do negócio** — caixa, receita, runway. Estamos seguros?
2. **Momentum de produto** — estamos entregando? O que tá travado?
3. **Comunidade** — crescendo? Sentimento positivo? Suporte em dia?
4. **Mercado** — alguma mudança relevante na concorrência ou no setor?
5. **Riscos** — o que pode dar errado nas próximas 2-4 semanas?
6. **Oportunidades** — o que devemos considerar fazer?

### Step 3 — Generate digest (HTML + MD)

**HTML:** Read the template at `.claude/templates/html/strategy-digest.html`, preencher todos os `{{PLACEHOLDER}}` com os dados coletados e salvar em `workspace/strategy/digests/[C] YYYY-WXX-strategy-digest.html`. Create the directory if it does not exist.

**MD:** Também salvar versão markdown em `workspace/strategy/digests/[C] YYYY-WXX-strategy-digest.md` com o seguinte formato:

```markdown
# Strategy Digest — Semana {WXX}

> Gerado em: {YYYY-MM-DD}
> Agente: @sage

## Saúde do Negócio
**Status:** 🟢/🟡/🔴
- MRR: R${X} ({var%})
- Assinaturas: {N} ({+/-})
- Runway: {N} meses

## Produto
**Status:** 🟢/🟡/🔴
- Entregas: {resumo}
- Blockers: {N}
- Issues comunidade: {N} abertas

## Comunidade
**Status:** 🟢/🟡/🔴
- WAM: {N}
- Sentimento: {label}
- Docs gaps: {N}

## Comercial
- Pipeline: {resumo}
- Parcerias: {status}

## Riscos (próximas 2-4 semanas)
1. {risco com evidência}

## Oportunidades
1. {oportunidade com justificativa}

## Recomendação da semana
{Uma frase: o que o responsável deveria priorizar baseado em tudo acima}
```

### Step 4 — Terminal summary

Present a short and direct version.

## Rules
- **Real data** — do not fabricate metrics. If data is unavailable, say "no data"
- **Opinions flagged** — when it is opinion vs data, make it clear
- **One recommendation** — do not give 10 suggestions, give 1 clear one
- **Connect the dots** — the value of the digest is crossing areas, not repeating individual reports


### Notify via Telegram

Upon completion, send a short summary via Telegram to the user:
- Use the Telegram MCP: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Format: emoji + routine name + main result (1-3 lines)
- If the routine had no updates, send anyway with "no updates"
