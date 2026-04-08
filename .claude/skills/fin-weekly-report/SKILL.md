---
name: fin-weekly-report
description: "Weekly financial report — consolidates Stripe and Omie data for the week: revenue, expenses, cash flow projection, overdue accounts, and variance analysis. Trigger when user says 'relatório financeiro semanal', 'financial weekly', 'como foi a semana financeiramente', 'resumo financeiro da semana'."
---

# Financial Weekly — Relatório Financeiro Semanal

Rotina semanal que consolida dados financeiros da semana: receitas, despesas, Stripe, Omie, fluxo de caixa projetado e análise.

**Sempre responder em pt-BR.**

## Step 1 — Coletar receitas da semana (silenciosamente)

### 1a. Stripe — receitas
Usar `/int-stripe` para buscar:
- Charges succeeded da semana (seg-dom) → agrupar por tipo/plano
- Comparar com semana anterior
- MRR atual vs início da semana
- Novos clientes vs cancelamentos
- Falhas de pagamento

### 1b. Omie — receitas
Usar `/int-omie` para buscar:
- Recebimentos confirmados na semana
- NFs emitidas na semana

Agrupar receitas por categoria:
- Assinaturas Stripe
- Serviços / Consultoria
- Parcerias
- Outros

## Step 2 — Coletar despesas da semana (silenciosamente)

### 2a. Omie — despesas
Usar `/int-omie` para buscar:
- Pagamentos efetuados na semana
- Categorizar: Pessoal, Infraestrutura, Serviços, Marketing, Impostos, Outros

### 2b. Comparativo
- Calcular variação vs semana anterior para cada categoria
- Calcular % do total para cada categoria

## Step 3 — Stripe detalhado

Consolidar métricas Stripe da semana:
- MRR e variação
- Total de assinaturas ativas e variação
- Churn rate
- Novos clientes
- Falhas de pagamento e valor em risco

## Step 4 — Omie detalhado

Consolidar métricas Omie da semana:
- Contas a receber vencidas (inadimplência)
- Contas a pagar da próxima semana
- NFs pendentes de emissão
- NFs emitidas na semana
- Recebimentos confirmados

## Step 5 — Projeção de fluxo de caixa (4 semanas)

Com base nos dados coletados, projetar:
- Entradas esperadas (recorrência Stripe + contas a receber)
- Saídas esperadas (contas a pagar + despesas recorrentes)
- Saldo e acumulado por semana

## Step 6 — Contas vencidas

Listar todas as contas vencidas (a receber e a pagar):
- Cliente/Fornecedor, tipo, valor, vencimento, dias de atraso

## Step 7 — Análise e recomendações

Escrever análise curta (3-5 bullets) cobrindo:
- Tendência de receita (crescendo/estável/caindo)
- Gastos fora do padrão
- Situação de inadimplência
- Fluxo de caixa (confortável ou apertado)

Escrever ações recomendadas (bullets):
- Cobranças a fazer
- NFs a emitir
- Pagamentos a antecipar/postergar
- Qualquer flag para o responsável ou equipe financeira

## Step 8 — Classificar saúde financeira

Badge de saúde (classe CSS):
- **green** "Saudável": receita > despesa, sem inadimplência relevante, fluxo positivo
- **yellow** "Atenção": margem apertada, ou inadimplência > R$ 2.000, ou fluxo projetado negativo
- **red** "Risco": despesa > receita, ou inadimplência > R$ 10.000, ou runway < 3 meses

## Step 9 — Gerar HTML

Ler o template em `.claude/templates/html/financial-weekly.html` e substituir TODOS os `{{PLACEHOLDER}}`.

Para tabelas dinâmicas de receitas/despesas:
```html
<tr>
  <td>Nome da Categoria</td>
  <td class="right">R$ X.XXX,XX</td>
  <td class="right">XX%</td>
  <td class="right var-positive/var-negative">+X% / -X%</td>
</tr>
```

Para fluxo de caixa:
```html
<tr>
  <td>Semana DD/MM - DD/MM</td>
  <td class="right">R$ X.XXX</td>
  <td class="right">R$ X.XXX</td>
  <td class="right" style="color:var(--green/--red)">R$ X.XXX</td>
  <td class="right">R$ XX.XXX</td>
</tr>
```

Valores em formato brasileiro: R$ 1.234,56

## Step 10 — Salvar

Salvar em:
```
05 Financeiro/reports/weekly/[C] YYYY-WXX-financial-weekly.html
```

Criar o diretório `05 Financeiro/reports/weekly/` se não existir.

## Step 11 — Confirmar

```
## Financial Weekly gerado

**Arquivo:** 05 Financeiro/reports/weekly/[C] YYYY-WXX-financial-weekly.html
**Receita:** R$ X.XXX ({var}%) | **Despesa:** R$ X.XXX ({var}%)
**MRR:** R$ X.XXX | **Saldo projetado 30d:** R$ XX.XXX
**Alertas:** {N} contas vencidas | {N} NFs pendentes
```

### Notificar no Telegram

Ao finalizar, enviar resumo curto no Telegram para o usuário:
- Usar o MCP do Telegram: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Formato: emoji + "Financial Weekly" + receita vs despesa + MRR + alertas (2-3 linhas)
