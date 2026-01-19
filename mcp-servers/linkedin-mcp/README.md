# LinkedIn MCP Server

Model Context Protocol server for posting to LinkedIn.

## Description

This MCP server enables Claude Code to post content to LinkedIn via the Model Context Protocol. It uses Playwright with Chrome DevTools Protocol (CDP) for browser automation.

## Features

- **Post to LinkedIn** - Publish text posts with hashtags and emojis
- **Dry Run Mode** - Preview posts without publishing (for testing)
- **Chrome CDP** - Uses existing Chrome session (preserves login)
- **Error Handling** - Comprehensive error handling and logging

## Installation

```bash
cd mcp-servers/linkedin-mcp
npm install
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LINKEDIN_DRY_RUN` | `true` | Set to `false` to actually publish posts |
| `CDP_ENDPOINT` | `http://127.0.0.1:9222` | Chrome DevTools Protocol endpoint |

### Chrome Setup

1. **Start Chrome with CDP enabled:**

**Windows:**
```batch
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\Users\User\ChromeAutomationProfile"
```

**Or use the provided batch file:**
```batch
scripts\social-media\START_AUTOMATION_CHROME.bat
```

2. **Log in to LinkedIn** in the Chrome automation window

3. **Session persists** - No need to log in again

## Usage

### Available Tools

#### `post_to_linkedin`

Post a message to LinkedIn.

**Parameters:**
- `content` (string, required): The post content (max 3000 characters)

**Returns:**
```json
{
  "success": true,
  "message": "Post published successfully",
  "platform": "LinkedIn",
  "dryRun": false
}
```

### Example Usage (via Claude)

```
Please post this to LinkedIn:
"Excited to announce our new AI Employee system! 🚀 #AI #Automation"
```

### Manual Testing

```bash
# Dry run (preview only, no posting)
LINKEDIN_DRY_RUN=true npm start

# Actually publish
LINKEDIN_DRY_RUN=false npm start
```

## Claude Code Configuration

Add to your Claude Code settings (`.claude/settings.json`):

```json
{
  "mcpServers": {
    "linkedin-mcp": {
      "command": "node",
      "args": ["mcp-servers/linkedin-mcp/server.js"],
      "env": {
        "LINKEDIN_DRY_RUN": "false"
      }
    }
  }
}
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Claude Code (Reasoning)                                     │
│ - Decides what to post                                      │
│ - Invokes MCP tool                                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ LinkedIn MCP Server (This Server)                          │
│ - Receives tool call from Claude                            │
│ - Uses Playwright + Chrome CDP                              │
│ - Posts to LinkedIn                                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ LinkedIn (External Service)                                 │
└─────────────────────────────────────────────────────────────┘
```

## Security Notes

- **Session Isolation**: Uses separate Chrome profile for automation
- **No Credentials Stored**: Login is handled by Chrome session
- **Human-in-the-Loop**: Requires approval before posting
- **Dry Run Default**: Safe by default (won't post without explicit opt-in)

## Troubleshooting

### "Failed to connect to Chrome CDP"

**Solution:** Start Chrome with CDP enabled:
```batch
scripts\social-media\START_AUTOMATION_CHROME.bat
```

### "Not logged in to LinkedIn"

**Solution:** Log in to LinkedIn via the Chrome automation window

### "Could not find 'Post' button"

**Solution:** LinkedIn may have changed UI. Check if post modal loaded correctly

### Posts not publishing

**Solution:** Check `LINKEDIN_DRY_RUN` environment variable is set to `false`

## Development

### Watch Mode (Auto-restart on changes)

```bash
npm run dev
```

### Logging

Server logs to stderr (visible in Claude Code debug output):
```
[LinkedIn MCP] Posting to LinkedIn...
[LinkedIn MCP] Content: Excited to announce...
[LinkedIn MCP] Dry Run: false
[LinkedIn MCP] Connecting to Chrome CDP...
[LinkedIn MCP] Content typed successfully
[LinkedIn MCP] Post published successfully
```

## Requirements

- Node.js v18+
- Chrome/Chromium browser
- Playwright
- LinkedIn account (logged in via automation Chrome)

## License

MIT
