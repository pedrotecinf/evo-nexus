---
name: social-linkedin-report
description: "LinkedIn analytics report — profile data, posts (when available), org stats. Use when user says 'linkedin report', 'relatório linkedin', 'como tá o linkedin', or any reference to LinkedIn performance."
---

# LinkedIn Report — Analytics

Rotina que puxa dados do LinkedIn via `/int-linkedin` e gera relatório.

**Sempre responder em pt-BR.**

## Fluxo

### Passo 1 — Coletar dados

```bash
python3 {project-root}/.claude/skills/int-linkedin/scripts/linkedin_client.py summary
python3 {project-root}/.claude/skills/int-linkedin/scripts/linkedin_client.py my_posts 1 10
```

Se `my_posts` retornar erro de permissão, informar que precisa de aprovação e usar dados disponíveis.

### Passo 2 — Gerar relatório

Usar template `.claude/templates/html/social-analytics-report.html` com dados disponíveis. Marcar seções sem dados como "Pendente — requer aprovação LinkedIn Advertising API".

### Passo 3 — Salvar

```
04 Redes Sociais/reports/linkedin/[C] YYYY-MM-DD-linkedin-report.html
```

### Passo 4 — Telegram

Notificar com dados disponíveis.
