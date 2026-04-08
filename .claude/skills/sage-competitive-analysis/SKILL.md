---
name: sage-competitive-analysis
description: "Analyze competitive landscape and market positioning. Use when user says 'competitive analysis', 'positioning', 'who are our competitors', 'benchmark', 'market analysis', or any reference to competitors, market positioning, or competitive advantages."
---

# Competitive Analysis — Market Positioning

Skill to analyze the competitive landscape of Evolution Foundation and identify positioning opportunities.

**Always respond in English.**

## Workflow

### Step 1 — Collect data internos

Buscar métricas atuais da Evolution:
- Stars/forks dos repos GitHub (`/int-github-review`)
- MRR e assinaturas Stripe (`/int-stripe`)
- Tamanho da comunidade Discord
- Número de instalações/instâncias (se disponível)

### Step 2 — Research competitors

Usar WebSearch/WebFetch para pesquisar os principais concorrentes no espaço de:
- APIs de WhatsApp (Baileys, wa-automate, Venom, wppconnect)
- CRMs com IA para WhatsApp (Kommo, Respond.io, Wati, MessageBird)
- Plataformas de automação (ManyChat, Botpress, Landbot)

Para cada concorrente, levantar:
- Modelo (open source vs SaaS vs enterprise)
- Pricing
- Features principais
- GitHub stars/forks (se open source)
- Pontos fortes e fracos

### Step 3 — Map positioning

Criar matriz de posicionamento:

| Dimensão | Evolution | Concorrente A | Concorrente B |
|----------|-----------|--------------|--------------|
| Modelo | Open source + SaaS | SaaS only | Enterprise |
| Preço | Freemium + planos | R$X/mês | R$X/mês |
| WhatsApp Unofficial | ✅ Baileys | ❌ | ❌ |
| WhatsApp Cloud API | ✅ | ✅ | ✅ |
| CRM integrado | ✅ Evo CRM | ❌ | ✅ |
| Comunidade | ✅ Discord + open source | ❌ | ❌ |
| IA/Agentes | ✅ Evo AI | Parcial | ❌ |

### Step 4 — Identify opportunities

- Gaps que nenhum concorrente cobre
- Features onde a Evolution lidera
- Ameaças (concorrentes crescendo rápido)
- Moats (vantagens difíceis de copiar)

### Step 5 — Save relatório

Save em `workspace/strategy/analises/[C] YYYY-MM-DD-competitiva.md`

## Rules
- Dados reais — pesquisar de verdade, não inventar
- Honesty about weaknesses — do not hide where the competition is better
- Focus on actionable — every analysis should end with "what to do about it"
- Update at most every 3 months (the market does not change every week)
