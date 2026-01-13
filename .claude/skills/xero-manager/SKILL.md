---
name: xero-manager
description: Monitor Xero accounting for transactions, invoices, and overdue payments. Create action files for financial events.
license: Apache-2.0
---

# Xero Manager

Monitor Xero accounting system for financial events requiring action.

## Purpose

**Detect and Alert** on important Xero accounting events automatically. The Xero Manager **monitors** your Xero account for invoices, payments, and unusual transactions, **creating** action files in your Obsidian vault for financial review.

## Design Principles

1. **API-Based Monitoring**: Uses Xero API for reliable financial data access
2. **OAuth2 Authentication**: Secure token-based authentication
3. **Event Filtering**: Detects overdue payments, new invoices, unusual expenses
4. **Human-in-the-Loop**: Creates action files rather than auto-processing

## Usage

```bash
# First-time setup (requires OAuth)
python -m watchers.xero_watcher --vault . --credentials .xero_credentials.json --once

# Run continuously
python -m watchers.xero_watcher --vault . --credentials .xero_credentials.json
```

## Monitored Events

- **New Invoices**: Issued and received invoices
- **Overdue Payments**: Payments overdue by >7 days
- **Unusual Expenses**: Expenses exceeding $500
- **Payment Received**: Incoming payment notifications

## Output Format

`Needs_Action/INVOICE_*.md` or `PAYMENT_*.md` containing:
- Invoice/payment details
- Amount and due date
- Action required (follow up, record, etc.)

## Integration Points

- **Accounting**: Financial reports and reconciliation
- **Weekly Briefing**: CEO financial summaries
