---
name: sage-competitive-analysis
description: "Analyze competitive landscape and market positioning. Use when user says 'análise competitiva', 'como tão os concorrentes', 'posicionamento', 'quem compete com a gente', 'benchmark', 'market analysis', or any reference to competitors, market positioning, or competitive advantages."
---

# Análise Competitiva — Posicionamento de Mercado

Skill para analisar o cenário competitivo da Evolution Foundation e identificar oportunidades de posicionamento.

**Sempre responder em pt-BR.**

## Fluxo

### Passo 1 — Coletar dados internos

Buscar métricas atuais da Evolution:
- Stars/forks dos repos GitHub (`/int-github-review`)
- MRR e assinaturas Stripe (`/int-stripe`)
- Tamanho da comunidade Discord
- Número de instalações/instâncias (se disponível)

### Passo 2 — Pesquisar concorrentes

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

### Passo 3 — Mapear posicionamento

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

### Passo 4 — Identificar oportunidades

- Gaps que nenhum concorrente cobre
- Features onde a Evolution lidera
- Ameaças (concorrentes crescendo rápido)
- Moats (vantagens difíceis de copiar)

### Passo 5 — Salvar relatório

Salvar em `09 Estrategia/analises/[C] YYYY-MM-DD-competitiva.md`

## Regras
- Dados reais — pesquisar de verdade, não inventar
- Honestidade sobre fraquezas — não esconder onde a concorrência é melhor
- Foco em actionable — toda análise deve terminar com "o que fazer com isso"
- Atualizar no máximo a cada 3 meses (mercado não muda toda semana)
