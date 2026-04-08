---
name: fin-daily-pulse
description: "Daily financial pulse — queries Stripe (MRR, charges, churn, failures) and Omie (accounts payable/receivable, invoices) to generate an HTML snapshot of the company's financial health. Trigger when user says 'financial pulse', 'financial snapshot', or 'financial metrics'."
---

# Financial Pulse — Daily Financial Snapshot

Daily routine that pulls data from Stripe and Omie to generate an HTML snapshot of financial health.

**Always respond in English.**

## Step 1 — Collect Stripe data (silently)

Use the `/int-stripe` skill to fetch:

### 1a. MRR and Subscriptions
- List active subscriptions (`status=active`) → count and sum values to calculate MRR
- Compare with previous data if available in `workspace/finance/`

### 1b. Today's Charges
- List charges created today (`created` >= start of day UTC-3)
- Sum total charged amount
- Count charges with `status=succeeded` vs `status=failed`

### 1c. Churn (last 30 days)
- List subscriptions canceled in the last 30 days
- Calculate churn rate vs total subscriptions

### 1d. Refunds (last 7 days)
- List refunds from the last 7 days
- Sum total refunded amount

### 1e. New customers (last 7 days)
- List customers created in the last 7 days

## Step 2 — Collect Omie data (silently)

Use the `/int-omie` skill to fetch:

### 2a. Overdue receivables
- Fetch receivables with due date before today and status "open"

### 2b. Payables (next 7 days)
- Fetch payables with due date in the next 7 days

### 2c. Invoices
- Fetch invoices pending issuance
- Count invoices issued in the current month

## Step 3 — Day's transactions

Consolidate all financial transactions for the day:
- Stripe charges (revenue)
- Payments recorded in Omie (expenses)
- Refunds

Format each transaction with: type (Revenue/Expense/Refund), description, amount, status.

## Step 4 — Classify financial health

Define the health badge (CSS class):
- **green** "Healthy": MRR stable or growing, no significant delinquency, churn < 5%
- **yellow** "Warning": churn between 5-10%, or overdue accounts > R$ 1,000, or payment failures > 3
- **red** "Risk": churn > 10%, or overdue accounts > R$ 5,000, or MRR declining

## Step 5 — Alerts

Generate list of financial alerts:
- Payment failures that need retry or follow-up
- Accounts overdue for more than 7 days
- Invoices that should have been issued
- Churn above normal levels
- Any anomalies in amounts

If there are no alerts: "No financial alerts at this time."

## Step 6 — Generate HTML

Read the template at `.claude/templates/html/financial-pulse.html` and replace ALL `{{PLACEHOLDER}}` with the collected data.

For transactions (dynamic table):
```html
<tr>
  <td><span class="badge green/red/yellow">Revenue/Expense/Refund</span></td>
  <td>Description</td>
  <td class="right">R$ X,XXX.XX</td>
  <td><span class="badge green/yellow">Confirmed/Pending</span></td>
</tr>
```

Values in Brazilian format: R$ 1.234,56

## Step 7 — Save

Save the filled HTML to:
```
workspace/finance/reports/daily/[C] YYYY-MM-DD-financial-pulse.html
```

Create the directory `workspace/finance/reports/daily/` if it does not exist.

## Step 8 — Confirm

```
## Financial Pulse generated

**File:** workspace/finance/reports/daily/[C] YYYY-MM-DD-financial-pulse.html
**MRR:** R$ X,XXX | **Subscriptions:** N | **Churn:** X%
**Alerts:** {N} attention points
```

### Notify via Telegram

Upon completion, send a short summary via Telegram to the user:
- Use the Telegram MCP: `reply(chat_id="YOUR_CHAT_ID", text="...")`
- Format: emoji + "Financial Pulse" + MRR + alerts (1-3 lines)
