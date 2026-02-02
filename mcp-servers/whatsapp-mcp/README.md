# WhatsApp MCP Server

Model Context Protocol (MCP) server for WhatsApp integration using Playwright browser automation.

## Features

- Send messages to WhatsApp contacts and groups
- Get list of recent chats
- Retrieve message history from specific chats
- Persistent session management (no repeated QR code scans)
- Non-intrusive automation

## Installation

```bash
cd mcp-servers/whatsapp-mcp
npm install
npx playwright install chromium
```

## Configuration

Create a `.env` file in the server directory:

```bash
# Session storage path (default: ./whatsapp_mcp_session)
WHATSAPP_SESSION_PATH=./whatsapp_mcp_session

# Run headless (default: false - show browser window)
WHATSAPP_HEADLESS=false
```

## Building

```bash
npm run build
```

## Running

```bash
npm start
```

On first run, a Chromium browser window will open with WhatsApp Web. Scan the QR code with your phone to authenticate. The session will be saved for future runs.

## Available Tools

### send_message

Send a message to a WhatsApp contact or group.

**Parameters:**
- `contact` (required): Contact name or phone number
- `message` (required): Message text to send

**Example:**
```json
{
  "contact": "John Doe",
  "message": "Hello! This is an automated message."
}
```

### get_chats

Get list of recent WhatsApp chats.

**Parameters:**
- `limit` (optional): Maximum number of chats to retrieve (default: 20)

**Example:**
```json
{
  "limit": "30"
}
```

### get_messages

Get recent messages from a specific chat.

**Parameters:**
- `contact` (required): Contact name to get messages from
- `limit` (optional): Number of messages to retrieve (default: 10)

**Example:**
```json
{
  "contact": "John Doe",
  "limit": "20"
}
```

### check_status

Check WhatsApp connection status.

**Parameters:** None

## Integration with AI Employee

This MCP server can be used by:

1. **WhatsApp Watcher** - For detecting incoming messages
2. **WhatsApp Approval Monitor** - For sending approved responses
3. **Direct MCP calls** - From Claude Code or other agents

## Security Notes

- Session data is stored locally in `WHATSAPP_SESSION_PATH`
- Never commit session files to version control
- Keep your phone connected to the internet for message delivery
- The browser window must remain open for the server to function

## Troubleshooting

### QR Code Not Loading

- Ensure your internet connection is stable
- Try clearing the session directory and restarting

### Messages Not Sending

- Check that the contact name matches exactly (case-sensitive)
- Ensure WhatsApp Web is fully loaded
- Verify the browser window is not minimized

### Session Expiration

- If session expires, delete the session directory and restart
- Re-scan the QR code when prompted

## License

MIT
