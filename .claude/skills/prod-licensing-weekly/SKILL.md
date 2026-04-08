---
name: prod-licensing-weekly
description: "Weekly open source growth report — queries licensing API for 7d telemetry with trend analysis: instance growth, geo expansion, version adoption, message volume trends, feature usage evolution. Generates HTML report. Use when user says 'licensing weekly', 'crescimento semanal', 'como cresceu o open source', or any reference to weekly licensing analysis."
---

# Licensing Weekly — Crescimento Open Source (7 dias)

Rotina semanal que analisa tendências de crescimento do open source.

**Sempre responder em pt-BR.**

## Fluxo

### Passo 1 — Coletar telemetria 7d

```bash
python3 {project-root}/.claude/skills/int-licensing/scripts/licensing_client.py telemetry --period 7d
```

### Passo 2 — Coletar alertas e keys

```bash
python3 {project-root}/.claude/skills/int-licensing/scripts/licensing_client.py alerts
python3 {project-root}/.claude/skills/int-licensing/scripts/licensing_client.py keys --status active --page 1 --limit 5
```

### Passo 3 — Comparar com semana anterior

Ler relatório anterior em `02 Projects/licensing-reports/weekly/`. Calcular:
- Crescimento de instâncias (% e absoluto)
- Novos países/cidades
- Migração de versões (adoção de novas versões)
- Trend de mensagens dia a dia (usar `daily_message_trend`)

### Passo 4 — Analisar tendências

- Quais países estão crescendo mais?
- Qual versão ganha adoção?
- Volume de mensagens subindo ou caindo?
- Features novas sendo adotadas?

### Passo 5 — Classificar e gerar HTML

Ler template `.claude/templates/html/licensing-report.html`. `{{REPORT_TYPE}}` = "Weekly". `{{PERIODO}}` = "Semana WXX — DD/MM a DD/MM".

### Passo 6 — Salvar

```
02 Projects/licensing-reports/weekly/[C] YYYY-WXX-licensing-weekly.html
```

### Passo 7 — Resumo + Telegram

Notificar com: instâncias, crescimento %, top país novo, versão dominante.
