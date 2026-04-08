---
name: social-youtube-report
description: "YouTube analytics report — queries channel stats, recent videos, engagement rates, top content. Generates HTML report. Use when user says 'youtube report', 'relatório youtube', 'como tá o canal', 'métricas youtube', 'youtube analytics', or any reference to YouTube performance analysis. Supports daily, weekly, and monthly periods."
---

# YouTube Report — Analytics do Canal

Rotina que puxa dados do YouTube via `/int-youtube` e gera relatório HTML de performance do canal.

**Sempre responder em pt-BR.**

## Fluxo

### Passo 1 — Determinar período

Baseado no comando:
- `make youtube` → período "daily" (snapshot do dia)
- `make youtube-weekly` → período "weekly" (últimos 7 dias)
- `make youtube-monthly` → período "monthly" (últimos 30 dias)

Se chamado diretamente, perguntar ou usar "daily" como default.

### Passo 2 — Coletar dados

Para cada conta YouTube configurada:

```bash
# Stats do canal
python3 {project-root}/.claude/skills/int-youtube/scripts/youtube_client.py channel_stats

# Últimos vídeos com métricas
python3 {project-root}/.claude/skills/int-youtube/scripts/youtube_client.py recent_videos 1 20

# Resumo de todas as contas
python3 {project-root}/.claude/skills/int-youtube/scripts/youtube_client.py summary
```

### Passo 3 — Comparar com período anterior

Ler relatório anterior em `04 Redes Sociais/reports/youtube/` se existir. Calcular deltas:
- Inscritos: delta absoluto e %
- Views total: delta
- Engagement rate médio: delta
- Vídeos publicados no período

### Passo 4 — Analisar

1. **KPIs do canal:** inscritos, views total, engagement rate médio
2. **Vídeos do período:** publicados, views, likes, comments
3. **Top vídeo:** melhor performance por engagement rate
4. **Tendência:** crescendo, estável, desacelerando
5. **Comentários recentes:** sentimento geral (se daily, puxar comments do vídeo mais recente)

### Passo 5 — Gerar HTML

Usar template `.claude/templates/html/social-analytics-report.html` com `{{REPORT_TYPE}}` = "YouTube Daily/Weekly/Monthly".

Se for a única plataforma configurada, adaptar o template pra focar em YouTube (não mostrar tabela comparativa cross-platform vazia).

### Passo 6 — Salvar

```
04 Redes Sociais/reports/youtube/[C] YYYY-MM-DD-youtube-{period}.html
```

Criar diretório se não existir.

### Passo 7 — Telegram

Notificar: `reply(chat_id="946857210", text="...")`
Formato: emoji + canal + inscritos + delta + melhor vídeo
