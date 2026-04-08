---
name: prod-review-todoist
description: "Review and organize Todoist tasks in the Evolution project. Finds uncategorized, untranslated, or messy tasks and organizes them with proper categories, PT-BR translation, and actionable titles. Use when user says 'review todoist', 'organiza tarefas', 'triagem todoist', 'limpa o todoist', 'organiza o Evolution' or similar."
---

# Review Todoist — Triagem do Projeto Evolution

Skill para revisar e organizar tarefas do projeto Evolution no Todoist. Identifica tarefas sem categoria, em inglês, genéricas ou desorganizadas e corrige diretamente.

## Pré-requisitos

- CLI `todoist` instalado e autenticado
- Projeto `Evolution` existente no Todoist

## Fluxo

### Passo 1 — Listar tarefas do projeto Evolution

```bash
todoist tasks -p "Evolution"
```

### Passo 2 — Identificar tarefas que precisam de organização

Uma tarefa precisa de triagem se atende **qualquer** destes critérios:

1. **Sem categoria** — não tem prefixo `[Categoria]` no título
2. **Em inglês** — título não está em PT-BR
3. **Genérica/vaga** — título não deixa claro o que fazer (ex: "update thing", "send docs")
4. **Sem contexto** — não tem comentário com origem/objetivo (especialmente tarefas vindas do sync-meetings)

### Passo 3 — Organizar cada tarefa

Para cada tarefa que precisa de triagem, aplicar:

#### 3a. Categorizar

Adicionar prefixo `[Categoria]` ao título. Categorias disponíveis:

| Categoria | Quando usar |
|---|---|
| `[Produto & Tech]` | Desenvolvimento, bugs, features, infra, deploy, código |
| `[Marketing]` | Conteúdo, campanhas, vídeos, social media, lançamentos |
| `[Comercial]` | Pipeline, propostas, parcerias, leads, pricing |
| `[Financeiro]` | Contas, NFs, pagamentos, métricas financeiras |
| `[Operação]` | Processos internos, grupos, acessos, comunicação do time |
| `[Estratégia]` | OKRs, roadmap, análises, decisões estratégicas |
| `[Comunidade]` | Discord, suporte, feedback de usuários, beta testers |
| `[Roadmap]` | Itens de roadmap futuro, avaliação de features |

#### 3b. Traduzir para PT-BR

Se o título está em inglês, traduzir para português brasileiro mantendo clareza e objetividade.

**Antes:** `Send event registration link to team member`
**Depois:** `[Operação] Enviar link de inscrição do evento para membro do time`

#### 3c. Tornar acionável

O título deve deixar claro:
- **O que** fazer (verbo no infinitivo)
- **Para quem/onde** (se aplicável)
- **Qual o resultado esperado** (se não for óbvio)

**Antes:** `Upload web panel; grant team member access`
**Depois:** `[Operação] Publicar painel web do evento e liberar acesso para membro do time`

#### 3d. Aplicar a atualização

```bash
todoist update <task-id> --content "[Categoria] Título traduzido e acionável"
```

### Passo 4 — Executar direto

**Regra fundamental: executar a organização diretamente, sem relatório intermediário.**

Não listar as tarefas antes de organizar. Não pedir confirmação para cada uma. Organizar todas de uma vez e confirmar no final.

### Passo 5 — Salvar artefato

Salvar um relatório curto em `01 Daily Logs/[C] YYYY-MM-DD-todoist-review.md` com:

```markdown
# Triagem Todoist — YYYY-MM-DD

**Projeto:** Evolution
**Tarefas revisadas:** {N}
**Organizadas:** {M} (categorizadas, traduzidas ou reescritas)
**Já OK:** {K} (sem alteração necessária)

## Tarefas Organizadas

| Tarefa | Antes | Depois |
|--------|-------|--------|
| ... | ... | ... |
```

Criar o diretório `01 Daily Logs/` se não existir.

### Passo 6 — Relatório final (curto)

Ao terminar, apresentar apenas:

```
## Triagem Todoist — Concluído

**Projeto:** Evolution
**Tarefas revisadas:** {N}
**Organizadas:** {M} (categorizadas, traduzidas ou reescritas)
**Já OK:** {K} (sem alteração necessária)
```

Se o usuário quiser ver detalhes do que mudou, ele pede.

## Regras Importantes

- **Projeto padrão é sempre `Evolution`** — não mover tarefas para outros projetos
- **Traduzir sempre para PT-BR** — sem exceção
- **Não alterar tarefas já organizadas** (que já têm `[Categoria]` e estão em PT-BR)
- **Não completar nem deletar tarefas** — apenas reorganizar
- **Não criar tarefas novas** — apenas editar as existentes
- **Manter comentários existentes** — não alterar comentários, apenas o título
- **Se não souber a categoria**, usar `[Operação]` como fallback
- **Executar primeiro, reportar depois** — sem relatório intermediário


### Notificar no Telegram

Ao finalizar, enviar resumo curto no Telegram para o usuário:
- Usar o MCP do Telegram: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Formato: emoji + nome da rotina + resultado principal (1-3 linhas)
- Se a rotina não teve novidades, enviar mesmo assim com "sem novidades"
