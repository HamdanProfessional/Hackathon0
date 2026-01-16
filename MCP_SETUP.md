# MCP Servers Setup Guide

## ✅ Configured MCP Servers

| Server | Status | Location | Use Case |
|--------|--------|----------|----------|
| **filesystem** | ✅ Ready | Built-in | Read/write files in project |
| **email** | ✅ Built | `mcp-servers/email-mcp/` | Send/draft/search emails |
| **calendar** | ✅ Built | `mcp-servers/calendar-mcp/` | Create/update events |
| **slack** | ✅ Built | `mcp-servers/slack-mcp/` | Send messages, read channels |
| **browser** | ✅ Installed | `@modelcontextprotocol/server-puppeteer` | Navigate, click, fill forms |
| **xero** | ⏸️ Disabled | `mcp-servers/xero-mcp/` | Accounting (OAuth issues) |

---

## 🔑 Required Credentials

### 1. Slack Bot Token (Required for Slack MCP)

**Create a Slack App:**
1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name: `AI Employee Bot`
4. Workspace: Select your workspace
5. Add OAuth Scopes:
   - `chat:write` - Send messages
   - `channels:read` - Read channels
   - `channels:history` - Read message history
   - `groups:read` - Read private channels
   - `groups:history` - Read private channel history
   - `im:write` - Send DMs
   - `im:history` - Read DM history
   - `mpim:write` - Send group DMs
   - `mpim:history` - Read group DM history
6. Install App to Workspace
7. Copy **Bot User OAuth Token** (starts with `xoxb-`)

**Update Config:**
```bash
# Edit .claude/config.json
"SLACK_BOT_TOKEN": "xoxb-your-actual-token-here"
```

### 2. Xero Credentials (Optional - Accounting)

**Create Xero App:**
1. Go to https://developer.xero.com/app/manage
2. Create Custom App
3. Add OAuth 2.0 credentials
4. Set redirect URI: `http://localhost:3000/callback`
5. Add scopes:
   - `accounting.transactions`
   - `accounting.reports.read`
   - `accounting.contacts`
   - `offline_access`

**Update Config:**
```bash
# Edit .claude/config.json
"XERO_CLIENT_ID": "your-client-id"
"XERO_CLIENT_SECRET": "your-client-secret"
```

---

## 🧪 Testing MCP Servers

### Test Filesystem MCP:
```bash
# Ask Claude: "List files in AI_Employee_Vault/Pending_Approval"
```

### Test Slack MCP (after adding token):
```bash
# Ask Claude: "List Slack channels"
# Ask Claude: "Send message to #general: Hello from AI Employee"
```

### Test Browser MCP:
```bash
# Ask Claude: "Navigate to https://example.com and get the page title"
```

### Test Email MCP:
```bash
# Ask Claude: "Draft an email to test@example.com with subject 'Test'"
```

### Test Calendar MCP:
```bash
# Ask Claude: "Create a calendar event for tomorrow at 2pm titled 'Meeting'"
```

---

## 📝 Configuration File Location

**MCP Config:** `.claude/config.json`

After adding credentials, restart Claude Code to reload MCP servers.

---

## 🚀 Quick Start

1. **Get Slack Bot Token** (5 minutes)
   - https://api.slack.com/apps → Create App → Add OAuth scopes → Install
   - Copy token to `.claude/config.json`

2. **Restart Claude Code**

3. **Test with:**
   ```
   /mcp
   ```

You should see all MCP servers listed!
