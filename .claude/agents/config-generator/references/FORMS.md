# Config Generator Templates

Configuration templates for PM2, MCP, and environment variables.

---

## PM2 Watcher Template

```javascript
{
  name: "{SERVICE}-watcher",
  "script": "python -m watchers.{service}_watcher --vault AI_Employee_Vault{args}",
  "interpreter": "python3",
  "exec_mode": "fork",
  "autorestart": true,
  "watch": false,
  "max_restarts": 10,
  "max_memory_restart": "500M",
  "env": {
    "PYTHONUNBUFFERED": "1",
    "VAULT_PATH": "AI_Employee_Vault"{env_vars}
  }
}
```

### Template Variables

- `{SERVICE}` - Service name (lowercase)
- `{service}` - Service name (lowercase)
- `{args}` - Additional command arguments
- `{env_vars}` - Environment variables

---

## PM2 Cron Job Template

```javascript
{
  name: "{JOB_NAME}",
  "script": "python {script_path}",
  "interpreter": "3.10",
  "cron": "{cron_schedule}",
  "autostart": true,
  "watch": false,
  "max_restarts": 1,
  "env": {
    "PYTHONUNBUFFERED": "1",
    "VAULT_PATH": "AI_Employee_Vault"
  }
}
```

### Common Cron Schedules

| Schedule | Cron Expression | Description |
|----------|----------------|-------------|
| Daily 7 AM | `0 7 * * *` | Every day at 7 AM |
| Weekdays 6 AM | `0 6 * * 1-5` | Mon-Fri at 6 AM |
| Hourly | `0 * * * *` | Every hour |
| Sundays 3 AM | `0 3 * * 0` | Every Sunday at 3 AM |

---

## MCP Server Template

```json
{
  "name": "{SERVER_NAME}",
  "command": "{node_command}",
  "args": [{args}],
  "env": {
    {env_vars}
  }
}
```

### MCP Server Types

**Node.js Server:**
```json
{
  "name": "email-mcp",
  "command": "node",
  "args": ["./mcp-servers/email-mcp/index.js"],
  "env": {
    "GMAIL_CREDENTIALS": "./.gmail_credentials.json"
  }
}
```

**Python Server:**
```json
{
  "name": "xero-mcp",
  "command": "python",
  "args": ["-m", "mcp_servers.xero_mcp"],
  "env": {
    "XERO_CLIENT_ID": "${XERO_CLIENT_ID}",
    "XERO_CLIENT_SECRET": "${XERO_CLIENT_SECRET}"
  }
}
```

---

## .env Template

```bash
# AI Employee System Configuration
# Generated: {DATE}
#
# WARNING: Never commit this file to version control!
# Copy this file to .env and fill in your credentials

# =============================================================================
# Vault Configuration
# =============================================================================
VAULT_PATH=AI_Employee_Vault

# =============================================================================
# Gmail API (OAuth 2.0)
# =============================================================================
GMAIL_CLIENT_ID=your_client_id_here
GMAIL_CLIENT_SECRET=your_client_secret_here

# =============================================================================
# Slack Bot (Token)
# =============================================================================
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_SIGNING_SECRET=your_signing_secret_here

# =============================================================================
# Telegram Bot (Token)
# =============================================================================
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# =============================================================================
# Xero API (OAuth 2.0)
# =============================================================================
XERO_CLIENT_ID=your_xero_client_id
XERO_CLIENT_SECRET=your_xero_client_secret

# =============================================================================
# WhatsApp (Session)
# =============================================================================
WHATSAPP_SESSION=./whatsapp_session

# =============================================================================
# Optional Settings
# =============================================================================
# LOG_LEVEL=INFO
# DRY_RUN=false
# CHECK_INTERVAL=60
```

---

## Credential Variable Patterns

### OAuth Credentials

```bash
{SERVICE}_CLIENT_ID=client_id
{SERVICE}_CLIENT_SECRET=client_secret
{SERVICE}_REDIRECT_URI=http://localhost:8080/callback
```

### Token-Based

```bash
{SERVICE}_TOKEN=your_token_here
{SERVICE}_API_KEY=your_api_key
```

### Session-Based

```bash
{SERVICE}_SESSION=./path_to_session
```

---

## PM2 Configuration Schema

```javascript
module.exports = {
  "apps": [
    {
      // Required fields
      name: string,              // Unique process name
      script: string,            // Command to execute

      // Optional fields
      interpreter: string,       // "python3", "node", etc.
      exec_mode: string,         // "fork" or "cluster"
      instances: number,         // Number of instances (cluster mode)
      autorestart: boolean,      // Auto-restart on crash
      watch: boolean|string[],   // Watch files for changes
      max_restarts: number,      // Max restarts before stopping
      max_memory_restart: string, // Restart if memory exceeds
      cron: string,              // Cron schedule
      env: object,               // Environment variables
      error_file: string,        // Error log file
      out_file: string,          // Output log file
      log_date_format: string,   // Log timestamp format
      merge_logs: boolean,       // Merge logs from instances
    }
  ]
}
```

---

## MCP Configuration Schema

```json
{
  "mcpServers": {
    "server-name": {
      "command": string,          // Command to run server
      "args": string[],          // Command arguments
      "env": object,             // Environment variables
      "transport": string        // "stdio" or "sse" (optional)
    }
  }
}
```

---

## Validation Rules

### PM2 Config

✅ Valid:
- `name` contains only letters, numbers, hyphens, underscores
- `script` is valid command
- `max_restarts` is positive integer
- `max_memory_restart` ends with 'M' or 'G'
- `cron` is valid cron expression

❌ Invalid:
- Duplicate `name` entries
- Missing required fields
- Invalid cron syntax
- Negative memory values

### MCP Config

✅ Valid:
- `command` is executable
- `args` is array of strings
- `env` values are strings
- File paths exist or use `${VAR}` format

❌ Invalid:
- Non-array `args`
- Missing `command`
- Invalid JSON syntax

### .env File

✅ Valid:
- `KEY=value` format
- No spaces around `=`
- Optional comments with `#`
- Empty lines allowed

❌ Invalid:
- Spaces around `=` (unless quoted)
- Multi-line values (use quotes)
- Invalid characters in keys
