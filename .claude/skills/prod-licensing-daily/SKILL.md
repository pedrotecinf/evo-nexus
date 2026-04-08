---
name: prod-licensing-daily
description: "Daily open source growth report — queries licensing API for 24h telemetry: active instances, heartbeat, geo distribution, versions, message volume, feature usage, commercial alerts. Generates HTML report. Use when user says 'licensing daily', 'crescimento diário', 'instâncias hoje', 'como tá o open source', or any reference to daily licensing metrics."
---

# Licensing Daily — Crescimento Open Source (24h)

Rotina diária que consulta a API de licenciamento e gera relatório HTML de crescimento.

**Sempre responder em pt-BR.**

## Fluxo

### Passo 1 — Coletar telemetria 24h

```bash
python3 {project-root}/.claude/skills/int-licensing/scripts/licensing_client.py telemetry --period 24h
```

Extrair: geo_distribution, version_distribution, city_distribution, heartbeat_coverage, message_metrics, feature_usage, daily_message_trend.

### Passo 2 — Coletar alertas comerciais

```bash
python3 {project-root}/.claude/skills/int-licensing/scripts/licensing_client.py alerts
```

### Passo 3 — Comparar com dia anterior

Ler o relatório do dia anterior em `02 Projects/licensing-reports/daily/` se existir. Calcular deltas para todos os KPIs.

### Passo 4 — Classificar crescimento

- **green** "Crescendo": instâncias ativas subindo, heartbeat > 80%, sem alertas críticos
- **yellow** "Estável": sem variação significativa ou heartbeat entre 60-80%
- **red** "Atenção": instâncias caindo, heartbeat < 60%, ou alertas não resolvidos > 5

### Passo 5 — Gerar HTML

Ler template `.claude/templates/html/licensing-report.html`. Substituir `{{REPORT_TYPE}}` por "Daily" e todos os placeholders. `{{PERIODO}}` = data de hoje.

### Passo 6 — Salvar

```
02 Projects/licensing-reports/daily/[C] YYYY-MM-DD-licensing-daily.html
```

### Passo 7 — Resumo + Telegram

Apresentar resumo curto e notificar no Telegram:
- `reply(chat_id="946857210", text="...")`
- Formato: emoji + instâncias ativas + heartbeat% + msgs enviadas + alertas
