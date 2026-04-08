---
name: pulse-faq-sync
description: "Sync and update the community FAQ from Discord conversations, WhatsApp groups, and GitHub issues. Identifies recurring questions, adds new entries, and keeps the FAQ as a living knowledge base. Use when user says 'update faq', 'sync faq', 'community faq', 'frequently asked questions', or when running community routines that detect unanswered/recurring questions."
---

# FAQ Sync — Living Knowledge Base

Routine that keeps the community FAQ always updated, fed by questions from Discord, WhatsApp, and GitHub issues.

**Always respond in English.**

## Main file

```
workspace/community/[C] FAQ.md
```

Este é o arquivo fonte de verdade. Todos os agentes e bots de suporte devem consultar este arquivo.

## FAQ Structure

O arquivo segue este formato:

```markdown
# FAQ — Community

> Atualizado automaticamente. Última sync: {YYYY-MM-DD HH:MM}
> Fontes: Discord (#help, #feedback) + GitHub Issues
> Total: {N} perguntas

---

## Instalação & Setup
<!-- tag: instalação, setup, docker, deploy -->

### Como instalar a API principal via Docker?
**Resposta:** [resposta clara e direta]
**Fonte:** Discord #help (recorrente) | [Link doc oficial se existir]
**Adicionado:** YYYY-MM-DD

### Como configurar SSL/HTTPS?
**Resposta:** [...]
**Fonte:** GitHub YOUR_ORG/main-api#123
**Adicionado:** YYYY-MM-DD

---

## Configuração
<!-- tag: config, env, variáveis, webhook -->

### Como configurar webhooks?
...

---

## Integrações
<!-- tag: whatsapp, telegram, typebot, n8n, chatwoot -->

...

## Evo CRM
<!-- tag: crm, agentes, pipeline, leads -->

...

## Evo Go
<!-- tag: evogo, go, manager -->

...

## Billing & Licenças
<!-- tag: licença, plano, preço, pagamento -->

...

## Erros Comuns
<!-- tag: erro, bug, 503, 401, timeout -->

...
```

## Workflow

### Step 1 — Read current FAQ

Ler `workspace/community/[C] FAQ.md`. Se não existir, criar com a estrutura base.

Contar quantas entradas existem e quais categorias.

### Step 2 — Collect new questions

**Do Discord (últimas 24h):**
Usar `/discord-get-messages` nos canais:
- `🆘・help` (ID do canal de help)
- `🆘・feedback`
- `💬・chat-pt`

Identificar mensagens que são **perguntas** (terminam em ?, pedem ajuda, reportam erro).

**Do GitHub (últimas 24h):**
```bash
# Issues abertas recentemente nos 5 repos
gh issue list --repo YOUR_ORG/main-api --state open --json title,body,labels,createdAt --limit 10
gh issue list --repo YOUR_ORG/crm-product --state open --json title,body,labels,createdAt --limit 10
gh issue list --repo YOUR_ORG/go-service --state open --json title,body,labels,createdAt --limit 10
gh issue list --repo YOUR_ORG/crm-community --state open --json title,body,labels,createdAt --limit 10
gh issue list --repo YOUR_ORG/methodology --state open --json title,body,labels,createdAt --limit 5
```

Filtrar issues que são perguntas ou bugs recorrentes.

**Do WhatsApp (últimas 24h):**
Usar `/int-whatsapp` para buscar mensagens dos grupos:

```bash
python3 {project-root}/.claude/skills/int-whatsapp/scripts/whatsapp_client.py messages_24h
```

Filtrar mensagens que são perguntas (terminam em ?, pedem ajuda, reportam erro, pedem orientação sobre configuração). Marcar fonte como "WhatsApp {nome do grupo}".

**Do Linear — Projeto "Evolution Suporte":**
Usar MCP do Linear para buscar issues resolvidas recentemente no projeto de suporte pago:
```
list_issues(project="Evolution Suporte", state="Done", updatedAt="-P1D")
```

Issues resolvidas no suporte pago são fonte de ouro para o FAQ — são problemas reais de clientes com soluções validadas. Para cada issue resolvida:
- Extrair o problema reportado como pergunta
- Extrair a resolução como resposta
- Marcar fonte como "Linear — Suporte Pago"
- Priorizar inclusão no FAQ (clientes pagantes = alta relevância)

### Step 3 — Analyze e classificar

Para cada pergunta encontrada:

1. **Já existe no FAQ?** → Se sim, verificar se a resposta precisa de atualização
2. **É recorrente?** → Se apareceu 2+ vezes (Discord ou GitHub), adicionar com prioridade
3. **Tem resposta?** → Se alguém respondeu no Discord/GitHub, usar como base
4. **Qual categoria?** → Classificar na categoria correta do FAQ

### Step 4 — Update FAQ

Para cada pergunta nova que deve entrar:
- Formular pergunta clara em PT-BR
- Escrever resposta objetiva e acionável
- Incluir fonte (Discord/GitHub + link se possível)
- Incluir data
- Adicionar na categoria correta

Para perguntas existentes:
- Atualizar resposta se houve informação nova
- Marcar como "atualizado" com nova data

### Step 5 — Update header

Atualizar o header do FAQ com:
- Data/hora da última sync
- Total de perguntas
- Categorias existentes

### Step 6 — Report

Present a short summary:

```
## FAQ Sync — {data}

Perguntas no FAQ: {total}
Novas adicionadas: {N}
Atualizadas: {N}
Fontes: Discord ({N} perguntas) + GitHub ({N} issues)

Novas:
- {pergunta 1} → {categoria}
- {pergunta 2} → {categoria}
```

## Rules

- **Quality > quantity** — only add questions that are truly recurring or useful
- **Actionable answers** — do not copy generic text, write answers that solve the problem
- **PT-BR** — all questions and answers in Portuguese
- **Do not duplicate** — always check if it already exists before adding
- **Source required** — every entry must have its origin
- **Do not fabricate answers** — if there is no clear answer, mark as "pending documentation"
- **Tags in comments** — keep HTML comment tags for easy searching
- **Keep organized** — categories in logical order (installation -> config -> integrations -> product -> billing -> errors)


### Notify via Telegram

Upon completion, send a short summary via Telegram to the user:
- Use the Telegram MCP: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Format: emoji + routine name + main result (1-3 lines)
- If the routine had no updates, send anyway with "no updates"
