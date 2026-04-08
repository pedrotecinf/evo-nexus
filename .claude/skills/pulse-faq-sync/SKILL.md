---
name: pulse-faq-sync
description: "Sync and update the community FAQ from Discord conversations, WhatsApp groups, and GitHub issues. Identifies recurring questions, adds new entries, and keeps the FAQ as a living knowledge base. Use when user says 'atualiza faq', 'sync faq', 'faq da comunidade', 'perguntas frequentes', or when running community routines that detect unanswered/recurring questions."
---

# FAQ Sync — Base de Conhecimento Viva

Rotina que mantém o FAQ da comunidade sempre atualizado, alimentado por perguntas do Discord, WhatsApp e issues do GitHub.

**Sempre responder em pt-BR.**

## Arquivo principal

```
03 Comunidade/[C] FAQ.md
```

Este é o arquivo fonte de verdade. Todos os agentes e bots de suporte devem consultar este arquivo.

## Estrutura do FAQ

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

## Fluxo

### Passo 1 — Ler FAQ atual

Ler `03 Comunidade/[C] FAQ.md`. Se não existir, criar com a estrutura base.

Contar quantas entradas existem e quais categorias.

### Passo 2 — Coletar perguntas novas

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

### Passo 3 — Analisar e classificar

Para cada pergunta encontrada:

1. **Já existe no FAQ?** → Se sim, verificar se a resposta precisa de atualização
2. **É recorrente?** → Se apareceu 2+ vezes (Discord ou GitHub), adicionar com prioridade
3. **Tem resposta?** → Se alguém respondeu no Discord/GitHub, usar como base
4. **Qual categoria?** → Classificar na categoria correta do FAQ

### Passo 4 — Atualizar FAQ

Para cada pergunta nova que deve entrar:
- Formular pergunta clara em PT-BR
- Escrever resposta objetiva e acionável
- Incluir fonte (Discord/GitHub + link se possível)
- Incluir data
- Adicionar na categoria correta

Para perguntas existentes:
- Atualizar resposta se houve informação nova
- Marcar como "atualizado" com nova data

### Passo 5 — Atualizar header

Atualizar o header do FAQ com:
- Data/hora da última sync
- Total de perguntas
- Categorias existentes

### Passo 6 — Relatório

Apresentar resumo curto:

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

## Regras

- **Qualidade > quantidade** — só adicionar perguntas que realmente são recorrentes ou úteis
- **Respostas acionáveis** — não copiar texto genérico, escrever resposta que resolve o problema
- **PT-BR** — todas as perguntas e respostas em português
- **Não duplicar** — sempre verificar se já existe antes de adicionar
- **Fonte obrigatória** — toda entrada deve ter de onde veio
- **Não inventar respostas** — se não tem resposta clara, marcar como "pendente de documentação"
- **Tags nos comentários** — manter as tags HTML comment pra facilitar busca
- **Manter organizado** — categorias em ordem lógica (instalação → config → integrações → produto → billing → erros)


### Notificar no Telegram

Ao finalizar, enviar resumo curto no Telegram para o usuário:
- Usar o MCP do Telegram: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Formato: emoji + nome da rotina + resultado principal (1-3 linhas)
- Se a rotina não teve novidades, enviar mesmo assim com "sem novidades"
