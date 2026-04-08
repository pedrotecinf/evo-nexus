---
name: sage-strategy-digest
description: "Generate weekly strategy digest consolidating financial, product, community, and market data into strategic insights. Use when user says 'strategy digest', 'digest estratégico', 'resumo estratégico da semana', 'como tá a empresa', or as part of the weekly strategy review routine."
---

# Strategy Digest — Resumo Estratégico Semanal

Rotina semanal que consolida dados de todas as áreas numa visão estratégica pra tomada de decisão.

**Sempre responder em pt-BR.**

## Fluxo

### Passo 1 — Coletar dados de cada área

**Financeiro:**
- Consultar `/int-stripe` — MRR atual, variação, novas assinaturas, churn, reembolsos
- Se disponível, ler último relatório em `05 Financeiro/`

**Produto:**
- Ler último `/int-linear-review` em `02 Projects/linear-reviews/`
- Ler último `/int-github-review` em `02 Projects/github-reviews/`
- Resumir: entregas da semana, blockers, PRs, issues da comunidade

**Comunidade:**
- Ler último relatório em `03 Comunidade/reports/weekly/`
- Resumir: WAM, sentimento, tópicos quentes, FAQ gaps

**Comercial:**
- Se existir pipeline em `02 Projects/comercial/`, ler status
- Verificar parcerias ativas

**Tendências:**
- Ler último trends report em `01 Daily Logs/`

### Passo 2 — Analisar estrategicamente

Cruzar os dados e responder:
1. **Saúde do negócio** — caixa, receita, runway. Estamos seguros?
2. **Momentum de produto** — estamos entregando? O que tá travado?
3. **Comunidade** — crescendo? Sentimento positivo? Suporte em dia?
4. **Mercado** — alguma mudança relevante na concorrência ou no setor?
5. **Riscos** — o que pode dar errado nas próximas 2-4 semanas?
6. **Oportunidades** — o que devemos considerar fazer?

### Passo 3 — Gerar digest (HTML + MD)

**HTML:** Ler o template em `.claude/templates/html/strategy-digest.html`, preencher todos os `{{PLACEHOLDER}}` com os dados coletados e salvar em `09 Estrategia/digests/[C] YYYY-WXX-strategy-digest.html`. Criar o diretório se não existir.

**MD:** Também salvar versão markdown em `09 Estrategia/digests/[C] YYYY-WXX-strategy-digest.md` com o seguinte formato:

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

### Passo 4 — Resumo no terminal

Apresentar versão curta e direta.

## Regras
- **Dados reais** — não inventar métricas. Se não tem o dado, dizer "sem dados"
- **Opinião sinalizada** — quando é opinião vs dado, deixar claro
- **Uma recomendação** — não dar 10 sugestões, dar 1 clara
- **Conectar os pontos** — o valor do digest é cruzar áreas, não repetir relatórios individuais


### Notificar no Telegram

Ao finalizar, enviar resumo curto no Telegram para o usuário:
- Usar o MCP do Telegram: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Formato: emoji + nome da rotina + resultado principal (1-3 linhas)
- Se a rotina não teve novidades, enviar mesmo assim com "sem novidades"
