# Config Generator Examples

---

## Example 1: Generate All Configurations

```bash
# Scan project and generate all configs
python .claude/skills/config-generator/scripts/generate_configs.py
```

Output:
```
🔧 Configuration Generator

📂 Scanning for watchers...
   Found 5 watcher(s)

📝 Generating PM2 configuration...
   5 app(s) configured
✅ Generated PM2 config: process-manager/pm2.config.js

📝 Generating MCP configuration...
   3 server(s) configured
✅ Generated MCP config: ~/.config/claude-code/mcp.json

📝 Generating .env template...
✅ Generated .env template: .env.example

✅ Configuration generation complete!
```

---

## Example 2: Custom Vault Path

```bash
python .claude/skills/config-generator/scripts/generate_configs.py \
  --vault /custom/path/to/vault
```

---

## Example 3: Dry Run

```bash
python .claude/skills/config-generator/scripts/generate_configs.py \
  --dry-run
```

Shows what would be generated without writing files.

---

## Generated PM2 Config

```javascript
module.exports = {
  "apps": [
    {
      "name": "gmail-watcher",
      "script": "python -m watchers.gmail_watcher --vault AI_Employee_Vault",
      "interpreter": "python3",
      "exec_mode": "fork",
      "autorestart": true,
      "watch": false,
      "max_restarts": 10,
      "max_memory_restart": "500M",
      "env": {
        "PYTHONUNBUFFERED": "1",
        "VAULT_PATH": "AI_Employee_Vault",
        "GMAIL_TOKEN": "${GMAIL_TOKEN}"
      }
    }
  ]
};
```

---

## Generated MCP Config

```json
{
  "mcpServers": {
    "email-mcp": {
      "command": "node",
      "args": ["./mcp-servers/email-mcp/index.js"],
      "env": {
        "GMAIL_CREDENTIALS": "./.gmail_credentials.json"
      }
    }
  }
}
```
