# Xero MCP Server - Quick Setup

## What's Included

✅ **Xero MCP Server** - Create invoices, manage contacts, track payments
✅ **OAuth Authentication** - Secure Xero API integration
✅ **6 MCP Tools** - Complete accounting workflow
✅ **TypeScript Implementation** - Type-safe and maintainable

---

## Setup (10 minutes)

### 1. Install Node.js Dependencies

```bash
cd mcp-servers/xero-mcp
npm install
```

### 2. Authenticate with Xero

Your `.env` file already has the credentials:
```bash
XERO_CLIENT_ID=636ACEF71DD944CAA6161E5051F1D883
XERO_CLIENT_SECRET=S_T4i5ET80CEAYoaLp0Oyl4it8bgWUQgXi9InyZ_pzdbD7hP
```

Run authentication:
```bash
npm run authenticate
```

This will:
1. Open your browser
2. Ask you to log in to Xero
3. Request authorization
4. Save token to `.xero_mcp_token.json`

### 3. Build the Server

```bash
npm run build
```

### 4. Configure Claude Code

Add to `~/.config/claude-code/mcp.json` (or Windows equivalent):

```json
{
  "servers": [
    {
      "name": "xero",
      "command": "node",
      "args": ["C:\\Users\\Hamdan\\Desktop\\testvault\\PERSONAL_AI_EMPLOYEE\\mcp-servers\\xero-mcp\\dist\\index.js"],
      "env": {
        "XERO_CLIENT_ID": "636ACEF71DD944CAA6161E5051F1D883",
        "XERO_CLIENT_SECRET": "S_T4i5ET80CEAYoaLp0Oyl4it8bgWUQgXi9InyZ_pzdbD7hP"
      }
    }
  ]
}
```

---

## Available Tools

| Tool | Description | Example Usage |
|------|-------------|---------------|
| `create_invoice` | Create new invoice | "Create invoice for $2,500" |
| `send_invoice` | Send to customer | "Send invoice INV-001" |
| `get_invoice` | Get invoice details | "Show invoice INV-001" |
| `create_contact` | Add/update contact | "Create contact for John Doe" |
| `get_profit_loss` | Get P&L statement | "What's my profit this month?" |
| `get_overdue_invoices` | List overdue invoices | "Show overdue invoices" |

---

## Example Workflow

### Create and Send Invoice

```
You: Create an invoice for Client ABC Company for $3,000
     for web development services due in 30 days.

Claude: I'll create that invoice for you.
       [Uses create_invoice tool]

You: Send it to the customer.

Claude: I'll send the invoice now.
       [Uses send_invoice tool]
```

### Check Overdue Invoices

```
You: Which invoices are overdue?

Claude: [Uses get_overdue_invoices tool]
       You have 2 overdue invoices:
       - INV-005: $1,500 (15 days overdue)
       - INV-008: $2,000 (7 days overdue)
```

---

## File Structure

```
mcp-servers/xero-mcp/
├── src/
│   ├── index.ts          # Main MCP server
│   ├── authenticate.ts    # OAuth authentication
│   ├── xero-client.ts    # Xero API wrapper
│   └── tools.ts          # MCP tool definitions
├── dist/                 # Compiled JavaScript (auto-generated)
├── package.json
├── tsconfig.json
└── README.md
```

---

## Testing

### Test Authentication

```bash
npm run authenticate
```

If successful, you'll see:
```
✓ Authentication Successful!
Token saved to .xero_mcp_token.json
Tenant ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### Test MCP Server

Start the server:
```bash
npm start
```

In Claude Code, test with:
```
"Get my profit and loss statement"
```

---

## Troubleshooting

### Issue: "Cannot find module 'xero-node'"
**Solution:** Run `npm install` in the xero-mcp folder

### Issue: "Not authenticated"
**Solution:** Run `npm run authenticate` again

### Issue: "No tenant ID"
**Solution:** Make sure you select an organization during Xero login

### Issue: "Token expired"
**Solution:** Delete `.xero_mcp_token.json` and re-authenticate

---

## Next Steps

1. **Test with real data**: Create a test invoice
2. **Set up approval workflow**: Invoices go through `/Approved/` folder first
3. **Automate with watchers**: Auto-create invoices from time tracking
4. **Integrate with briefings**: Financial data in CEO Briefing

---

## Security Notes

✅ Credentials in `.env` (gitignored)
✅ Token in `.xero_mcp_token.json` (gitignored)
✅ OAuth 2.0 flow (secure)
✅ All actions logged by Claude Code

---

*Xero MCP Server - Quick Setup v1.0*
