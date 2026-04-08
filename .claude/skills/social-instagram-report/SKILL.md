---
name: social-instagram-report
description: "Instagram analytics report — queries profile stats, recent posts, engagement rates, insights for all connected accounts. Generates HTML report. Use when user says 'instagram report', 'relatório instagram', 'como tá o insta', 'métricas instagram', or any reference to Instagram performance analysis."
---

# Instagram Report — Analytics dos Perfis

Rotina que puxa dados do Instagram via `/int-instagram` e gera relatório HTML de performance.

**Sempre responder em pt-BR.**

## Fluxo

### Passo 1 — Coletar dados de todas as contas

Para cada conta Instagram configurada:

```bash
python3 {project-root}/.claude/skills/int-instagram/scripts/instagram_client.py summary
python3 {project-root}/.claude/skills/int-instagram/scripts/instagram_client.py recent_posts [account] 20
python3 {project-root}/.claude/skills/int-instagram/scripts/instagram_client.py account_insights [account]
```

### Passo 2 — Comparar com período anterior

Ler relatório anterior em `04 Redes Sociais/reports/instagram/` se existir. Calcular deltas de seguidores, engagement, impressões.

### Passo 3 — Analisar

Por conta:
1. **KPIs:** seguidores, media count, engagement rate médio
2. **Posts do período:** publicados, likes, comments, engagement
3. **Top post:** melhor performance
4. **Tipo de conteúdo:** Reels vs Image vs Carousel — qual performa melhor
5. **Account insights:** impressões, alcance, profile views (se disponível)

### Passo 4 — Gerar HTML

Usar template `.claude/templates/html/social-analytics-report.html` com `{{REPORT_TYPE}}` = "Instagram".

### Passo 5 — Salvar

```
04 Redes Sociais/reports/instagram/[C] YYYY-MM-DD-instagram-report.html
```

### Passo 6 — Telegram

Notificar: seguidores por conta + engagement médio + melhor post
