# In Progress - Local - Shared Domain

Shared (cross-domain) items currently being processed by Local machine.

**Purpose:** Temporary storage for cross-domain items that are actively being worked on by Local.

**Lifecycle:**
1. Item synced from Cloud or created locally
2. Local claims item → moves here
3. Local processes item → moves to `Pending_Approval/` or `Done/Shared/`

**Claim-by-Move:** Moving an item here claims it for Local processing.
