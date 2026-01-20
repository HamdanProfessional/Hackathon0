# Domain Classification

This folder contains tasks and events classified by domain type.

## Folder Structure

### `/Needs_Action/Personal/`
**Tasks related to personal life:**
- Health and medical appointments
- Family matters
- Personal finance and banking
- Education and learning
- Hobbies and personal interests
- Personal shopping
- Insurance and subscriptions

**Examples:**
- Doctor appointment reminders
- Family events
- Personal budget tracking
- Course enrollment confirmations

### `/Needs_Action/Business/`
**Tasks related to business operations:**
- Client communications
- Invoice and payment processing
- Project management
- Social media management
- Accounting and bookkeeping
- Vendor relationships
- Business development

**Examples:**
- Client inquiries
- Invoice follow-ups
- Project deliverables
- Social media posts
- Accounting reports

### `/Needs_Action/Shared/`
**Tasks that affect both personal and business domains:**
- Urgent reminders
- Scheduling conflicts
- Important notifications
- System alerts
- Cross-domain dependencies

**Examples:**
- Urgent deadlines
- Meeting reminders
- Travel planning (business + personal)
- Emergency notifications

## Classification Logic

Tasks are automatically classified by the `domain_classifier.py` module using:

1. **Keyword Analysis** - Content is scanned for domain-specific keywords
2. **Sender Analysis** - Email sender domains are checked
3. **Context Analysis** - Overall context determines classification

## Manual Classification

If automatic classification is incorrect, you can manually move files between domain folders.

## Usage in Watchers

Watchers automatically classify new items:

```python
from watchers.domain_classifier import classify_domain, get_domain_folder

# Classify an email
domain = classify_domain(
    subject="Invoice #1234 from Acme Corp",
    content="Please find attached invoice",
    sender="billing@acmecorp.com",
    source="gmail"
)
# Returns: Domain.BUSINESS

# Get domain folder
domain_folder = get_domain_folder(vault_path, domain)
# Returns: AI_Employee_Vault/Needs_Action/Business/
```

---

*Last Updated: 2026-01-20*
*System Version: v1.5.0 (Platinum Tier)*
