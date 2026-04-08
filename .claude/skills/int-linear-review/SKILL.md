---
name: int-linear-review
description: "Review Linear projects — check issues in review, blockers, stale items, sprint progress, and assigned tasks. Use when user says 'checa o linear', 'review do linear', 'como tá o sprint', 'issues em review', 'status dos projetos', 'o que tá travado', or any reference to checking project/issue status in Linear."
---

# Linear Review — Checagem de Projetos

Skill para revisar o estado dos projetos no Linear: issues em review, blockers, items parados, progresso do sprint e tarefas atribuídas.

**Sempre responder em pt-BR.**

## Fluxo

Executar os passos abaixo silenciosamente e apresentar relatório consolidado no final.

### Passo 1 — Levantar contexto

Usar as tools do Linear MCP para coletar dados:

1. **Issues em Review** — listar issues com estado "In Review" ou "Review":
   ```
   list_issues(state="In Review")
   ```

2. **Issues do usuário** — listar issues atribuídas ao usuário:
   ```
   list_issues(assignee="me")
   ```

3. **Blockers** — listar issues com prioridade Urgent (1) ou High (2):
   ```
   list_issues(priority=1)
   list_issues(priority=2)
   ```

4. **Issues paradas** — listar issues "In Progress" que não foram atualizadas nos últimos 3 dias:
   ```
   list_issues(state="In Progress", updatedAt="-P3D")
   ```
   Comparar: se a issue está em "In Progress" mas não foi atualizada há mais de 3 dias, marcar como stale.

5. **Ciclo atual** — verificar progresso do sprint/ciclo ativo:
   ```
   list_cycles(teamId="...", type="current")
   ```

### Passo 2 — Analisar

Para cada grupo, identificar:
- **Em Review:** quem precisa revisar, há quanto tempo está pendente
- **Blockers:** o que está travando e quem é responsável
- **Stale:** issues paradas sem atividade — precisam de atenção ou repriorização
- **Minhas:** o que o usuário precisa fazer primeiro (por prioridade)

### Passo 3 — Relatório

Apresentar no formato:

```
## Linear Review — {data}

### Em Review ({N})
| Issue | Título | Responsável | Dias em review |
|-------|--------|-------------|----------------|

### Blockers ({N})
| Issue | Título | Prioridade | Responsável | Descrição do bloqueio |
|-------|--------|------------|-------------|----------------------|

### Stale — Paradas >3 dias ({N})
| Issue | Título | Responsável | Última atualização |
|-------|--------|-------------|-------------------|

### Minhas Issues ({N})
| Issue | Título | Status | Prioridade |
|-------|--------|--------|------------|

### Sprint/Ciclo Atual
- Progresso: {X}% ({concluídas}/{total})
- Prazo: {data fim}
- Risco: {alto/médio/baixo}
```

### Passo 4 — Salvar artefato HTML

Ler o template em `.claude/templates/html/linear-review.html`, preencher todos os `{{PLACEHOLDER}}` com os dados coletados nos passos anteriores e salvar o HTML completo em `02 Projects/linear-reviews/[C] YYYY-MM-DD-linear-review.html`.

Criar o diretório `02 Projects/linear-reviews/` se não existir.

## Regras

- **Não alterar issues** — apenas ler e reportar. Mudanças só com aprovação do usuário
- **Priorizar clareza** — se não conseguir determinar o time ou ciclo, listar o que encontrar sem travar
- **Destacar riscos** — issues em review há mais de 2 dias ou stale são sinais de atenção
- **Ser direto** — números, não narrativa


### Notificar no Telegram

Ao finalizar, enviar resumo curto no Telegram para o usuário:
- Usar o MCP do Telegram: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Formato: emoji + nome da rotina + resultado principal (1-3 linhas)
- Se a rotina não teve novidades, enviar mesmo assim com "sem novidades"
