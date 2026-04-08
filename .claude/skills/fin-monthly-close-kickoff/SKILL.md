---
name: fin-monthly-close-kickoff
description: "Monthly close kickoff — initiates the month-end closing process with a checklist, simplified P&L, pending reconciliations, receivables, payables, and action items for the finance team. Trigger when user says 'fechamento mensal', 'monthly close', 'inicia fechamento', 'kickoff do fechamento', or on the 1st of each month."
---

# Monthly Close Kickoff — Fechamento Mensal

Rotina mensal que inicia o processo de fechamento: gera checklist, DRE simplificada, pendências e ações para a equipe financeira.

**Sempre responder em pt-BR.**

**IMPORTANTE:** Esta rotina roda no dia 1 de cada mês e se refere ao fechamento do mês ANTERIOR.

## Step 1 — Determinar período

- Mês de referência: mês anterior ao atual (ex: se hoje é 01/04, fechar março)
- Período: primeiro ao último dia do mês de referência

## Step 2 — Coletar dados do mês (silenciosamente)

### 2a. Receitas (Stripe)
Usar `/int-stripe`:
- Total de charges succeeded no mês
- MRR no final do mês vs início
- Assinaturas: novas, canceladas, upgrades, downgrades
- Reembolsos do mês

### 2b. Receitas e despesas (Omie)
Usar `/int-omie`:
- Total de receitas recebidas no mês
- Total de despesas pagas no mês
- Categorizar por tipo (Pessoal, Infra, Serviços, Marketing, Impostos, etc.)
- NFs emitidas no mês
- NFs que deveriam ter sido emitidas e não foram

### 2c. Contas a receber pendentes
- Listar todas as contas a receber abertas (do mês ou anteriores)
- Destacar vencidas

### 2d. Contas a pagar do próximo mês
- Listar contas a pagar com vencimento no mês corrente (próximo mês)

### 2e. Mês anterior (para comparação)
- Ler relatório financeiro do mês anterior em `05 Financeiro/reports/monthly/` se existir
- Ou usar dados do último monthly close

## Step 3 — Montar DRE simplificada

Estruturar DRE com:

| Conta | Realizado | Mês Anterior | Variação |
|-------|-----------|-------------|----------|
| Receita Bruta (Stripe) | | | |
| Receita Bruta (Omie/Serviços) | | | |
| (-) Impostos | | | |
| **Receita Líquida** | | | |
| (-) Pessoal | | | |
| (-) Infraestrutura | | | |
| (-) Serviços terceiros | | | |
| (-) Marketing | | | |
| (-) Outros | | | |
| **Total Despesas** | | | |
| **Resultado Operacional** | | | |
| Margem | | | |

## Step 4 — Montar checklist de fechamento

Gerar checklist com status inicial para cada item:

1. **Conciliar Stripe** — verificar se todas as charges batem com os recebimentos
2. **Conciliar Omie** — verificar se entradas e saídas no ERP estão corretas
3. **Emitir NFs pendentes** — listar NFs que precisam ser emitidas (equipe financeira)
4. **Cobrar inadimplentes** — listar clientes com pagamento atrasado
5. **Categorizar despesas** — verificar se todas as despesas estão categorizadas
6. **Revisar lançamentos** — verificar lançamentos manuais ou atípicos
7. **Calcular impostos** — verificar obrigações fiscais do mês
8. **Gerar DRE final** — após conciliações, gerar DRE definitiva
9. **Aprovar fechamento** — O responsável revisa e aprova

Status possíveis:
- `done` (✓) — já concluído automaticamente
- `pending` (◯) — precisa ser feito
- `blocked` (✗) — depende de algo externo
- `na` (—) — não aplicável este mês

## Step 5 — Identificar pendências para a equipe financeira

Listar em bullets claros o que precisa da equipe financeira:
- NFs a emitir (quais clientes, valores)
- Pagamentos a confirmar
- Documentos faltando
- Prazos

## Step 6 — Observações do fechamento

Notas relevantes:
- Despesas atípicas (não recorrentes)
- Mudanças de plano de clientes
- Qualquer anomalia identificada
- Impacto de eventos do mês (ex: evento corporativo, parceria nova)

## Step 7 — Classificar status do close

Badge:
- **green** "No prazo": maioria dos itens ok, sem blockers
- **yellow** "Em andamento": itens pendentes mas sem risco
- **red** "Atrasado": bloqueios ou itens críticos pendentes

## Step 8 — Gerar HTML

Ler o template em `.claude/templates/html/monthly-close.html` e substituir TODOS os `{{PLACEHOLDER}}`.

Para checklist:
```html
<div class="checklist-item">
  <div class="check-icon done/pending/blocked/na">✓/◯/✗/—</div>
  <div class="checklist-text">
    <div class="cl-title">Nome do item</div>
    <div class="cl-detail">Detalhe ou observação</div>
  </div>
  <div class="checklist-owner">Financeiro / Admin / Auto</div>
</div>
```

Para DRE:
```html
<tr>
  <td>Nome da conta</td>
  <td class="right">R$ X.XXX,XX</td>
  <td class="right">R$ X.XXX,XX</td>
  <td class="right var-positive/var-negative">+X% / -X%</td>
</tr>
```

Linhas totais usar `class="total"`:
```html
<tr class="total">
  <td>Resultado Operacional</td>
  <td class="right">R$ X.XXX,XX</td>
  <td class="right">R$ X.XXX,XX</td>
  <td class="right var-positive">+X%</td>
</tr>
```

Valores em formato brasileiro: R$ 1.234,56

## Step 9 — Salvar

Salvar em:
```
05 Financeiro/reports/monthly/[C] YYYY-MM-monthly-close.html
```

Criar o diretório `05 Financeiro/reports/monthly/` se não existir.

## Step 10 — Confirmar

```
## Monthly Close Kickoff gerado

**Arquivo:** 05 Financeiro/reports/monthly/[C] YYYY-MM-monthly-close.html
**Mês:** {mês de referência}
**Receita:** R$ X.XXX | **Despesa:** R$ X.XXX | **Resultado:** R$ X.XXX
**Checklist:** X/9 concluídos
**Pendências equipe financeira:** {N} itens
```

### Notificar no Telegram

Ao finalizar, enviar resumo curto no Telegram para o usuário:
- Usar o MCP do Telegram: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Formato: emoji + "Monthly Close" + resultado do mês + pendências (2-3 linhas)
