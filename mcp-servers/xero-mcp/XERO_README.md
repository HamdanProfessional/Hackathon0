# Xero MCP Server

Model Context Protocol (MCP) server for Xero accounting integration. Enables Claude Code to create invoices, manage contacts, and track payments in Xero.

## Features

- **create_invoice** - Create new invoices in Xero
- **send_invoice** - Send invoices to customers via email
- **get_invoice** - Retrieve invoice details
- **create_contact** - Create or update contacts
- **get_profit_loss** - Get Profit and Loss statement
- **get_overdue_invoices** - Get all overdue invoices

## Setup

### 1. Install Dependencies

```bash
cd mcp-servers/xero-mcp
npm install
```

### 2. Configure Environment

Your `.env` file should already have:
```bash
XERO_CLIENT_ID=your_client_id
XERO_CLIENT_SECRET=your_client_secret
```

### 3. Authenticate with Xero

```bash
npm run authenticate
```

This will:
1. Open a browser window
2. Ask you to log in to Xero
3. Request authorization for the app
4. Save the token to `.xero_mcp_token.json`

### 4. Start the MCP Server

```bash
npm start
```

Or for development:
```bash
npm run dev
```

## Usage with Claude Code

### Configure Claude Code

Add to your Claude Code settings (`~/.config/claude-code/mcp.json`):

```json
{
  "servers": [
    {
      "name": "xero",
      "command": "node",
      "args": ["C:\\Users\\Hamdan\\Desktop\\testvault\\PERSONAL_AI_EMPLOYEE\\mcp-servers\\xero-mcp\\dist\\index.js"],
      "env": {
        "XERO_CLIENT_ID": "your_client_id",
        "XERO_CLIENT_SECRET": "your_client_secret"
      }
    }
  ]
}
```

### Example Prompts

```
"Create an invoice for Client A for $2,500 for web development services"

"Send invoice INV-001 to the customer"

"Get all overdue invoices that need follow-up"

"Create a contact for John Doe with email john@example.com"

"What's my profit and loss for this month?"
```

## Tools Reference

### create_invoice

Create a new invoice in Xero.

**Parameters:**
- `contactId` (string, required): Xero contact ID
- `lineItems` (array, required): Line items
  - `description` (string): Item description
  - `quantity` (number): Quantity
  - `unitAmount` (number): Unit price
  - `accountCode` (string): Xero account code
- `dueDate` (string, optional): Due date (YYYY-MM-DD)
- `reference` (string, optional): Reference number

**Returns:** Invoice ID

### send_invoice

Send an invoice to customer via email.

**Parameters:**
- `invoiceId` (string, required): Xero invoice ID

**Returns:** Confirmation message

### get_invoice

Get invoice details.

**Parameters:**
- `invoiceId` (string, required): Xero invoice ID

**Returns:** Invoice details

### create_contact

Create or update a contact.

**Parameters:**
- `name` (string, required): Contact name
- `email` (string, optional): Email address
- `phoneNumber` (string, optional): Phone number
- `address` (object, optional): Postal address

**Returns:** Contact ID

### get_profit_loss

Get Profit and Loss statement.

**Parameters:**
- `period` (string, optional): MONTH, QUARTER, or YEAR

**Returns:** P&L report data

### get_overdue_invoices

Get all overdue invoices.

**Parameters:** None

**Returns:** List of overdue invoices

## Development

### Build

```bash
npm run build
```

### Watch Mode

```bash
npm run watch
```

### Authentication Flow

1. Run `npm run authenticate`
2. Browser opens to Xero login
3. Authorize the app
4. Token saved to `.xero_mcp_token.json`

## Troubleshooting

### Issue: "Not authenticated"
**Solution:** Run `npm run authenticate` first

### Issue: "Token expired"
**Solution:** Delete `.xero_mcp_token.json` and re-authenticate

### Issue: "No tenant ID"
**Solution:** Make sure you select a Xero organization during authentication

### Issue: "Invoice not found"
**Solution:** Verify the invoice ID exists in your Xero account

## Security

- Credentials stored in `.env` (never commit)
- Token stored in `.xero_mcp_token.json` (gitignored)
- All actions logged by Claude Code
- Requires human approval before executing actions

## License

MIT

---

*Xero MCP Server v1.0*
