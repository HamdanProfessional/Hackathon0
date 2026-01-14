---
name: config-generator
description: Generate PM2 configs, MCP configs, and .env templates for the AI Employee system. Use when adding new watchers, MCP servers, or updating system configuration.
---

# Config Generator Agent

Automatically generate and validate configuration files for the AI Employee system.

## When to Use This Agent

Use this agent when you need to:
- Add a new watcher to PM2 configuration
- Add a new MCP server to Claude Code config
- Generate `.env` templates for credentials
- Validate existing configuration syntax
- Backup configurations before making changes
- Get diff view of configuration changes

## What This Agent Does

Config Generator handles all configuration management:

1. **PM2 Configuration** - Generates `process-manager/pm2.config.js` entries
2. **MCP Configuration** - Updates Claude Code `mcp.json`
3. **Environment Templates** - Creates `.env` files with all required variables
4. **Validation** - Checks configuration syntax before writing
5. **Backups** - Creates backups before modifying configs
6. **Credential Detection** - Scans code for required credentials

## Quick Start

### Generate PM2 Config

```
Generate PM2 config for:
- gmail-watcher with OAuth credentials
- slack-watcher with token authentication
- telegram-watcher with bot token

All using vault path: AI_Employee_Vault
```

### Generate MCP Config

```
Add to Claude Code MCP config:
- Email MCP server at ./mcp-servers/email-mcp
- Calendar MCP server at ./mcp-servers/calendar-mcp
```

### Generate .env Template

```
Create .env template with:
- Gmail credentials (CLIENT_ID, CLIENT_SECRET)
- Slack bot token
- Xero API credentials
```

## Workflow

1. **Scan Project**
   - Detect existing watchers and MCP servers
   - Find credentials in code
   - Load existing configurations

2. **Generate Configurations**
   - Create PM2 entries for all watchers
   - Create MCP entries for all servers
   - Generate .env with all environment variables

3. **Validate**
   - Check JSON/JavaScript syntax
   - Verify file paths exist
   - Validate credential variable names

4. **Backup & Write**
   - Backup existing configs
   - Write new configurations
   - Show diff of changes

## Output Structure

```
process-manager/
├── pm2.config.js (updated)
└── pm2.config.js.backup (created)

~/.config/claude-code/
├── mcp.json (updated)
└── mcp.json.backup (created)

.env (created)
.env.example (created)

.claude/agents/config-generator/
└── outputs/
    └── config_report.md (summary)
```

## Configuration Types

### PM2 Configuration

Generates PM2 process entries for:
- Watchers (gmail, calendar, xero, etc.)
- Orchestrator
- Approval monitors
- Scheduled tasks (daily briefing, etc.)

**Features:**
- Auto-restart on crash
- Memory limits
- Environment variable injection
- Cron schedule support
- Watch mode for development

### MCP Configuration

Generates Claude Code MCP server entries:
- Server command and arguments
- Environment variables
- Transport type (stdio, SSE)
- Server dependencies

**Features:**
- Automatic server discovery
- Environment variable propagation
- Server-specific configuration

### Environment Templates

Generates `.env` files with:
- All credential variables
- Default values where safe
- Comments explaining each variable
- Security warnings

**Features:**
- Scans code for `os.getenv()` calls
- Groups related variables
- Marks required vs optional

## Advanced Usage

### Partial Updates

```
Update only PM2 config, don't touch MCP or .env
```

### Dry Run

```
Generate configurations but don't write files
```

### Validation Only

```
Validate existing configurations without generating new ones
```

## Templates

See `references/FORMS.md` for:
- PM2 config templates
- MCP config templates
- .env templates
- Credential variable patterns

## Reference

See `references/reference.md` for:
- PM2 configuration schema
- MCP configuration schema
- Environment variable naming conventions
- Validation rules

## Examples

See `references/examples.md` for:
- Complete configuration generation walkthrough
- Adding a new watcher to existing config
- Merging multiple configuration sources
- Troubleshooting configuration issues

---

**Next:** Use the config-generator agent to generate your configurations!
