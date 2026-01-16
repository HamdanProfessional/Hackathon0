---
type: email
source: gmail
from: "{{sender}}"
subject: "{{subject}}"
received: "{{timestamp}}"
priority: "{{priority}}"
status: pending
---

# Email: {{subject}}

## From
{{sender_name}} <{{sender_email}}>

## Content
{{email_body}}

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
- [ ] Add to task list
- [ ] Schedule follow-up
- [ ] Extract information to database

## Quick Reply Draft
{{reply_draft}}

## Notes
{{additional_notes}}

---
*Created by Gmail Watcher - automatic email processing*
