---
name: fin-daily-pulse
description: "Daily financial pulse — queries Stripe (MRR, charges, churn, failures) and Omie (contas a pagar/receber, NFs) to generate an HTML snapshot of the company's financial health. Trigger when user says 'financial pulse', 'pulso financeiro', 'como tá o financeiro hoje', 'snapshot financeiro', or 'métricas financeiras'."
---

# Financial Pulse — Snapshot Financeiro Diário

Rotina diária que puxa dados do Stripe e Omie para gerar um snapshot HTML da saúde financeira.

**Sempre responder em pt-BR.**

## Step 1 — Coletar dados do Stripe (silenciosamente)

Usar a skill `/int-stripe` para buscar:

### 1a. MRR e Assinaturas
- Listar assinaturas ativas (`status=active`) → contar e somar valores para calcular MRR
- Comparar com dados anteriores se disponíveis em `05 Financeiro/`

### 1b. Charges de hoje
- Listar charges criadas hoje (`created` >= início do dia UTC-3)
- Somar valor total cobrado
- Contar charges com `status=succeeded` vs `status=failed`

### 1c. Churn (últimos 30 dias)
- Listar assinaturas canceladas nos últimos 30 dias
- Calcular taxa de churn vs total de assinaturas

### 1d. Reembolsos (últimos 7 dias)
- Listar refunds dos últimos 7 dias
- Somar valor total reembolsado

### 1e. Novos clientes (últimos 7 dias)
- Listar customers criados nos últimos 7 dias

## Step 2 — Coletar dados do Omie (silenciosamente)

Usar a skill `/int-omie` para buscar:

### 2a. Contas a receber vencidas
- Buscar contas a receber com vencimento anterior a hoje e status "aberto"

### 2b. Contas a pagar (próximos 7 dias)
- Buscar contas a pagar com vencimento nos próximos 7 dias

### 2c. Notas fiscais
- Buscar NFs pendentes de emissão
- Contar NFs emitidas no mês corrente

## Step 3 — Movimentações do dia

Consolidar todas as movimentações financeiras do dia:
- Charges do Stripe (receitas)
- Pagamentos registrados no Omie (despesas)
- Reembolsos

Formatar cada movimentação com: tipo (Receita/Despesa/Reembolso), descrição, valor, status.

## Step 4 — Classificar saúde financeira

Definir o badge de saúde (classe CSS):
- **green** "Saudável": MRR estável ou crescendo, sem inadimplência relevante, churn < 5%
- **yellow** "Atenção": churn entre 5-10%, ou contas vencidas > R$ 1.000, ou falhas de pagamento > 3
- **red** "Risco": churn > 10%, ou contas vencidas > R$ 5.000, ou MRR caindo

## Step 5 — Alertas

Gerar lista de alertas financeiros:
- Falhas de pagamento que precisam de retry ou contato
- Contas vencidas há mais de 7 dias
- NFs que deveriam ter sido emitidas
- Churn acima do normal
- Qualquer anomalia nos valores

Se não houver alertas: "Nenhum alerta financeiro no momento."

## Step 6 — Gerar HTML

Ler o template em `.claude/templates/html/financial-pulse.html` e substituir TODOS os `{{PLACEHOLDER}}` com os dados coletados.

Para movimentações (tabela dinâmica):
```html
<tr>
  <td><span class="badge green/red/yellow">Receita/Despesa/Reembolso</span></td>
  <td>Descrição</td>
  <td class="right">R$ X.XXX,XX</td>
  <td><span class="badge green/yellow">Confirmado/Pendente</span></td>
</tr>
```

Valores em formato brasileiro: R$ 1.234,56

## Step 7 — Salvar

Salvar o HTML preenchido em:
```
05 Financeiro/reports/daily/[C] YYYY-MM-DD-financial-pulse.html
```

Criar o diretório `05 Financeiro/reports/daily/` se não existir.

## Step 8 — Confirmar

```
## Financial Pulse gerado

**Arquivo:** 05 Financeiro/reports/daily/[C] YYYY-MM-DD-financial-pulse.html
**MRR:** R$ X.XXX | **Assinaturas:** N | **Churn:** X%
**Alertas:** {N} pontos de atenção
```

### Notificar no Telegram

Ao finalizar, enviar resumo curto no Telegram para o usuário:
- Usar o MCP do Telegram: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Formato: emoji + "Financial Pulse" + MRR + alertas (1-3 linhas)
