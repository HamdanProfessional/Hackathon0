# Config Generator Reference

Technical reference for configuration generation and validation.

---

## PM2 Configuration Schema

Complete schema for PM2 process entries:

```javascript
{
  name: string,              // Required: Unique process name
  script: string,            // Required: Command to execute
  interpreter: string,       // Optional: "python3", "node"
  exec_mode: string,         // Optional: "fork" (default) or "cluster"
  instances: number,         // Optional: Number of instances (cluster mode)
  autorestart: boolean,      // Optional: Auto-restart on crash (default: true)
  watch: boolean|string[],   // Optional: Watch files for changes
  max_restarts: number,      // Optional: Max restarts before stopping
  max_memory_restart: string,// Optional: "500M", "1G"
  cron: string,              // Optional: Cron schedule
  env: object,               // Optional: Environment variables
}
```

---

## MCP Configuration Schema

```json
{
  "mcpServers": {
    "server-name": {
      "command": "node|python",
      "args": ["path/to/server"],
      "env": {"VAR": "value"}
    }
  }
}
```

---

## Environment Variable Naming

### Convention: `{SERVICE}_{PARAMETER}`

Examples:
- `GMAIL_CLIENT_ID`
- `SLACK_BOT_TOKEN`
- `XERO_CLIENT_SECRET`

### Types

**OAuth:**
- `{SERVICE}_CLIENT_ID`
- `{SERVICE}_CLIENT_SECRET`
- `{SERVICE}_REDIRECT_URI`

**Token:**
- `{SERVICE}_TOKEN`
- `{SERVICE}_API_KEY`

**Session:**
- `{SERVICE}_SESSION`

---

## File Locations

| Config | Location |
|--------|----------|
| PM2 | `process-manager/pm2.config.js` |
| MCP | `~/.config/claude-code/mcp.json` |
| Environment | `.env` (project root) |
| Vault | `AI_Employee_Vault/` |

---

## Validation Rules

### PM2 Config

✅ Valid name: `[a-z0-9-_]+`
✅ Valid memory: `\d+[MG]`
✅ Valid cron: `* * * * *`

### MCP Config

✅ Valid command: Executable exists
✅ Valid args: Array of strings
✅ Valid JSON: Proper syntax

### .env File

✅ Valid format: `KEY=value`
✅ No spaces around `=`
✅ Comments: `# comment`

---

## Usage

```bash
# Generate all configs
python .claude/skills/config-generator/scripts/generate_configs.py

# Generate with custom vault path
python .claude/skills/config-generator/scripts/generate_configs.py --vault custom_vault

# Dry run (don't write files)
python .claude/skills/config-generator/scripts/generate_configs.py --dry-run
```
