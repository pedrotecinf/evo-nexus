---
name: prod-licensing-monthly
description: "Monthly open source growth report — comprehensive 30d analysis of licensing data: growth trajectory, geographic expansion, version adoption lifecycle, message volume scaling, feature adoption curves, commercial alerts summary. Generates HTML report. Use when user says 'licensing monthly', 'crescimento mensal open source', 'relatório mensal licensing', or any reference to monthly licensing analysis."
---

# Licensing Monthly — Crescimento Open Source (30 dias)

Rotina mensal que faz análise completa de crescimento do open source.

**Sempre responder em pt-BR.**

## Fluxo

### Passo 1 — Coletar telemetria 30d

```bash
python3 {project-root}/.claude/skills/int-licensing/scripts/licensing_client.py telemetry --period 30d
```

### Passo 2 — Coletar dados complementares

```bash
python3 {project-root}/.claude/skills/int-licensing/scripts/licensing_client.py alerts
python3 {project-root}/.claude/skills/int-licensing/scripts/licensing_client.py keys --status active --page 1 --limit 5
python3 {project-root}/.claude/skills/int-licensing/scripts/licensing_client.py products
```

### Passo 3 — Comparar com mês anterior

Ler relatório anterior em `02 Projects/licensing-reports/monthly/`. Calcular:
- Crescimento de instâncias (% e absoluto, mês a mês)
- Novos mercados (países que não existiam antes)
- Evolução de versões (quais cresceram, quais declinaram)
- Escala de mensagens (crescimento do volume)
- Features com maior adoção

### Passo 4 — Análise profunda

Escrever análise de crescimento cobrindo:
- Trajetória: acelerando, linear, desacelerando?
- Mercados-chave: onde está o maior potencial?
- Adoção de versão: tempo médio de migração
- Uso real: mensagens por instância está crescendo? (mais uso, não só mais instâncias)
- Alertas: padrão de problemas recorrentes
- Projeção: se mantiver o ritmo, onde estará em 3 meses?

### Passo 5 — Classificar e gerar HTML

Ler template `.claude/templates/html/licensing-report.html`. `{{REPORT_TYPE}}` = "Monthly". `{{PERIODO}}` = "Mês/YYYY".

### Passo 6 — Salvar

```
02 Projects/licensing-reports/monthly/[C] YYYY-MM-licensing-monthly.html
```

### Passo 7 — Resumo + Telegram

Notificar com: instâncias totais, crescimento % mensal, top 3 países, projeção trimestral.
