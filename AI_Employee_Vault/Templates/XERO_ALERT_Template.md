---
type: {{alert_type}}
source: xero
priority: {{priority}}
status: pending
created: {{timestamp}}
---

# Xero Alert: {{alert_title}}

## Alert Details
- **Type:** {{alert_type}}
- **Date:** {{date}}
- **Amount:** {{amount}}

## Description
{{description}}

## Action Required
- [ ] Review in Xero dashboard
- [ ] Update records
- [ ] Contact relevant party
- [ ] Update budget if needed

## Xero Links
- **Dashboard:** https://go.xero.com/
- **Tenant:** AI EMPLOYEE
- **Tenant ID:** b154c8d6-0dbc-4891-9100-34af087c31f1

## Alert Types

### Invoice Overdue
- Invoice is 7+ days past due date
- Created when invoices exceed OVERDUE_DAYS threshold

### Unusual Expense
- Expense exceeds UNUSUAL_EXPENSE_THRESHOLD ($500)
- Requires review for legitimacy

### Payment Received
- Client has paid an invoice
- For informational purposes

## Notes
{{additional_notes}}

---
*Created by Xero Watcher - monthly accounting in Accounting/ folder*
