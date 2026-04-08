---
name: sage-okr-review
description: "Review and track OKRs progress. Use when user says 'como tão os OKRs', 'review de OKRs', 'progresso das metas', 'atualiza OKRs', 'definir OKRs do trimestre', or any reference to objectives, key results, or quarterly goals."
---

# OKR Review — Acompanhamento de Metas

Skill para revisar, atualizar ou definir OKRs trimestrais da empresa.

**Sempre responder em pt-BR.**

## Fluxo

### Se já existem OKRs (atualização)

1. Ler o arquivo de OKRs mais recente em `09 Estrategia/okrs/`
2. Para cada Key Result, buscar dados atualizados:
   - Métricas financeiras → `/int-stripe` (MRR, assinaturas)
   - Métricas de produto → `/int-linear-review` (issues, entregas)
   - Métricas de comunidade → ler relatórios em `03 Comunidade/reports/`
   - Métricas de GitHub → ler relatórios em `02 Projects/github-reviews/`
3. Calcular progresso de cada KR (0-100%)
4. Classificar: 🟢 on track (>70%) | 🟡 at risk (40-70%) | 🔴 off track (<40%)
5. Atualizar o arquivo de OKRs com os novos dados
6. Apresentar resumo

### Se não existem OKRs (definição)

1. Entrevistar o usuário sobre prioridades do trimestre
2. Propor 3-4 Objectives com 3-4 Key Results cada
3. Cada KR deve ser: mensurável, com baseline e target, com prazo
4. Salvar em `09 Estrategia/okrs/[C] YYYY-QX-okrs.md`

## Formato do arquivo de OKRs

```markdown
# OKRs — Q{X} {YYYY}

> Status: {em definição | ativo | em revisão | fechado}
> Período: {data início} → {data fim}
> Última atualização: {YYYY-MM-DD}

## O1: {Objetivo 1}

| KR | Baseline | Target | Atual | Progresso | Status |
|----|----------|--------|-------|-----------|--------|
| {KR1} | {valor} | {valor} | {valor} | {X%} | 🟢/🟡/🔴 |
| {KR2} | {valor} | {valor} | {valor} | {X%} | 🟢/🟡/🔴 |

**Notas:** {contexto relevante}

## O2: {Objetivo 2}
...
```

## Regras
- KRs devem ser números, não atividades ("aumentar MRR pra R$15k" não "trabalhar no MRR")
- Baseline obrigatório — sem baseline não dá pra medir progresso
- Não inventar dados — se não tem o número, marcar como "pendente"
- Máximo 4 Objectives por trimestre — foco > ambição
