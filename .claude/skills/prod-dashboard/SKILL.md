---
name: prod-dashboard
description: "Daily consolidation dashboard — reads outputs from all routines (morning, linear, github, community, strategy, meetings, metrics) and generates a unified HTML dashboard. Trigger when user says 'dashboard', 'gera dashboard', 'visão geral', 'consolidação', 'overview', or 'painel geral'."
---

# Dashboard Consolidado — Visão 360

Rotina de consolidação que lê os outputs das outras rotinas e gera um HTML dashboard unificado com visão geral de todas as áreas do negócio.

**Sempre responder em pt-BR.**

**IMPORTANTE:** Esta rotina NÃO busca dados novos. Ela lê os outputs já gerados pelas outras rotinas do dia/semana e consolida tudo numa view única.

## Step 1 — Coletar dados das fontes (silenciosamente)

Ler todas as fontes disponíveis sem narrar cada passo. Se alguma fonte não existir (rotina não rodou ainda), usar "—" ou "sem dados" como fallback.

### 1a. Tarefas
Rodar `todoist list --filter "today | overdue"` para contar tarefas pendentes.

### 1b. Linear / Sprint
Ler o último relatório de Linear em `02 Projects/linear-reviews/` (arquivo mais recente `[C] *-linear-review.html`). Extrair:
- Progresso do sprint (% e contagem)
- Blockers
- Issues em review
- Issues concluídas

### 1c. GitHub
Ler o último relatório de GitHub em `02 Projects/github-reviews/` (arquivo mais recente `[C] *-github-review.html`). Extrair:
- PRs abertos
- Issues da comunidade
- Stars da semana
- Último release

### 1d. Comunidade
Ler o último community pulse em `03 Comunidade/reports/daily/` ou weekly em `03 Comunidade/reports/weekly/`. Extrair:
- WAM (Weekly Active Members)
- Sentimento geral
- Tickets de suporte
- Docs gaps

### 1e. Financeiro
Ler o último strategy digest em `09 Estrategia/digests/` (arquivo mais recente). Extrair:
- MRR
- Assinaturas
- Runway
- Pipeline comercial

### 1f. Agenda
Usar /gog-calendar para listar eventos de hoje.

### 1g. Reuniões
Ler `07 Reuniões/summaries/` ou `09 Reuniões/summaries/` — últimas 5 reuniões. Extrair:
- Data, título, participantes, action items

### 1h. Métricas de rotinas
Ler `ADWs/logs/metrics.json` para status de cada rotina automatizada:
- Nome, agente, última execução, duração média, taxa de sucesso

### 1i. Morning Briefing
Ler o briefing matinal de hoje em `01 Daily Logs/[C] YYYY-MM-DD-morning.html` se existir, para complementar dados de agenda e tarefas prioritárias.

## Step 2 — Calcular health badges

Para cada área, definir o status (classe CSS):
- **saudavel** (verde): tudo ok, métricas dentro do esperado
- **misto** (amarelo): algum ponto de atenção
- **risco** (vermelho): problemas sérios precisam de ação

Critérios:
- **Produto:** blockers > 0 = misto; blockers > 3 = risco; progresso sprint < 50% com >60% do tempo = risco
- **Comunidade:** sentimento negativo = risco; docs gaps > 5 = misto
- **Financeiro:** MRR caindo = misto; runway < 6 meses = risco
- **Rotinas:** qualquer rotina com taxa < 80% = misto; taxa < 50% = risco

## Step 3 — Gerar dashboard HTML

Ler o template em `.claude/templates/html/dashboard-consolidation.html` e substituir TODOS os `{{PLACEHOLDER}}` com os dados coletados.

Para rows dinâmicas (marcadas com `<!-- TEMPLATE -->`), gerar o HTML correto:

### Agenda rows
```html
<div class="metric-row">
  <div class="mr-label">HH:MM</div>
  <div class="mr-value">Nome do evento</div>
</div>
```

### Tarefas prioritárias rows
```html
<div class="list-item">Tarefa descrição</div>
```

### Reuniões rows
```html
<tr>
  <td>DD/MM</td>
  <td>Nome da reunião</td>
  <td>Pessoa 1, Pessoa 2</td>
  <td>N action items</td>
</tr>
```

### Rotinas rows
```html
<tr>
  <td>Nome da Rotina</td>
  <td>@agente</td>
  <td>DD/MM HH:MM</td>
  <td>XXs</td>
  <td><span class="rotina-rate high/medium/low">XX%</span></td>
  <td><div class="rotina-status"><div class="rotina-dot ok/falha"></div></div></td>
</tr>
```

### Pontos de atenção
Consolidar em bullets os itens que requerem atenção imediata. Exemplos:
- Blockers no sprint
- PRs sem review há mais de 2 dias
- Sentimento negativo na comunidade
- Rotinas falhando
- MRR em queda

Se não houver pontos de atenção, escrever "Nenhum ponto de atenção no momento."

## Step 4 — Salvar

Salvar o HTML preenchido em:
```
01 Daily Logs/[C] YYYY-MM-DD-dashboard.html
```

## Step 5 — Confirmar

Apresentar resumo curto:

```
## Dashboard gerado

**Arquivo:** 01 Daily Logs/[C] YYYY-MM-DD-dashboard.html
**Health:** Produto {status} | Comunidade {status} | Financeiro {status} | Rotinas {status}
**Alertas:** {N} pontos de atenção
```

### Notificar no Telegram

Ao finalizar, enviar resumo curto no Telegram para o usuário:
- Usar o MCP do Telegram: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Formato: emoji + nome da rotina + health status de cada área (1-3 linhas)
- Se não teve novidades, enviar mesmo assim com "sem novidades"
