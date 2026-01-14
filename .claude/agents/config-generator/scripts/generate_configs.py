#!/usr/bin/env python3
"""
Config Generator - Generate PM2, MCP, and .env configurations
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
import re


def scan_watchers(watchers_path: str = "watchers") -> list:
    """Scan for watcher scripts"""
    watchers_dir = Path(watchers_path)
    if not watchers_dir.exists():
        return []

    watchers = []
    for file in watchers_dir.glob("*_watcher.py"):
        watchers.append({
            'name': file.stem.replace('_watcher', ''),
            'file': file
        })
    return watchers


def generate_pm2_config(watchers: list, vault_path: str = "AI_Employee_Vault") -> dict:
    """Generate PM2 configuration for watchers"""
    apps = []

    for watcher in watchers:
        name = watcher['name']
        service_name = name.lower().replace('-', '_')

        app = {
            "name": f"{name}-watcher",
            "script": f"python -m watchers.{service_name}_watcher --vault {vault_path}",
            "interpreter": "python3",
            "exec_mode": "fork",
            "autorestart": True,
            "watch": False,
            "max_restarts": 10,
            "max_memory_restart": "500M",
            "env": {
                "PYTHONUNBUFFERED": "1",
                "VAULT_PATH": vault_path,
                f"{name.upper()}_TOKEN": f"${{{name.upper()}_TOKEN}}"
            }
        }
        apps.append(app)

    return {"apps": apps}


def generate_mcp_config(mcp_servers_path: str = "mcp-servers") -> dict:
    """Generate MCP server configuration"""
    mcp_dir = Path(mcp_servers_path)
    if not mcp_dir.exists():
        return {"mcpServers": {}}

    servers = {}

    for server_dir in mcp_dir.iterdir():
        if not server_dir.is_dir():
            continue

        # Check for package.json (Node.js) or main.py (Python)
        package_json = server_dir / "package.json"
        main_py = server_dir / "main.py"

        if package_json.exists():
            # Node.js server
            with open(package_json) as f:
                pkg = json.load(f)

            servers[server_dir.name] = {
                "command": "node",
                "args": [f"./{server_dir}/index.js"],
                "env": {}
            }

        elif main_py.exists():
            # Python server
            servers[server_dir.name] = {
                "command": "python",
                "args": ["-m", f"mcp_servers.{server_dir.name}"],
                "env": {}
            }

    return {"mcpServers": servers}


def generate_env_template() -> str:
    """Generate .env template"""
    template = f"""# AI Employee System Configuration
# Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
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
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret

# =============================================================================
# Slack Bot (Token)
# =============================================================================
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token

# =============================================================================
# Telegram Bot (Token)
# =============================================================================
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

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
LOG_LEVEL=INFO
DRY_RUN=false
CHECK_INTERVAL=60
"""
    return template


def backup_config(filepath: Path) -> Path:
    """Backup existing configuration"""
    if filepath.exists():
        backup_path = filepath.parent / f"{filepath.name}.backup"
        content = filepath.read_text()
        backup_path.write_text(content)
        print(f"✅ Backed up {filepath} to {backup_path}")
        return backup_path
    return None


def write_pm2_config(config: dict, output_path: str = "process-manager/pm2.config.js"):
    """Write PM2 configuration to file"""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Backup existing config
    backup_config(output_file)

    # Convert to JavaScript format
    js_content = f"/**\n * PM2 Configuration\n * Generated: {datetime.utcnow().isoformat()}\n */\n\n"
    js_content += "module.exports = " + json.dumps(config, indent=2) + ";\n"

    output_file.write_text(js_content)
    print(f"✅ Generated PM2 config: {output_file}")


def write_mcp_config(config: dict, output_path: str = "~/.config/claude-code/mcp.json"):
    """Write MCP configuration to file"""
    from pathlib import Path
    import os

    # Expand ~ in path
    output_file = Path(output_path).expanduser()
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Backup existing config
    backup_config(output_file)

    output_file.write_text(json.dumps(config, indent=2))
    print(f"✅ Generated MCP config: {output_file}")


def write_env_template(template: str, output_path: str = ".env.example"):
    """Write .env template to file"""
    output_file = Path(output_path)

    output_file.write_text(template)
    print(f"✅ Generated .env template: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Config Generator')
    parser.add_argument('--vault', default='AI_Employee_Vault',
                       help='Vault path')
    parser.add_argument('--watchers-path', default='watchers',
                       help='Path to watchers directory')
    parser.add_argument('--mcp-path', default='mcp-servers',
                       help='Path to MCP servers directory')
    parser.add_argument('--pm2-output', default='process-manager/pm2.config.js',
                       help='PM2 config output path')
    parser.add_argument('--mcp-output', default='~/.config/claude-code/mcp.json',
                       help='MCP config output path')
    parser.add_argument('--env-output', default='.env.example',
                       help='.env template output path')
    parser.add_argument('--dry-run', action='store_true',
                       help='Generate but don\'t write files')

    args = parser.parse_args()

    print("🔧 Configuration Generator")
    print()

    # Scan for watchers
    print("📂 Scanning for watchers...")
    watchers = scan_watchers(args.watchers_path)
    print(f"   Found {len(watchers)} watcher(s)")

    # Generate PM2 config
    print("\n📝 Generating PM2 configuration...")
    pm2_config = generate_pm2_config(watchers, args.vault)
    print(f"   {len(pm2_config['apps'])} app(s) configured")

    if not args.dry_run:
        write_pm2_config(pm2_config, args.pm2_output)

    # Generate MCP config
    print("\n📝 Generating MCP configuration...")
    mcp_config = generate_mcp_config(args.mcp_path)
    print(f"   {len(mcp_config['mcpServers'])} server(s) configured")

    if not args.dry_run:
        write_mcp_config(mcp_config, args.mcp_output)

    # Generate .env template
    print("\n📝 Generating .env template...")
    env_template = generate_env_template()

    if not args.dry_run:
        write_env_template(env_template, args.env_output)

    print("\n✅ Configuration generation complete!")

    if args.dry_run:
        print("\n⚠️  Dry run mode - files not written")
        print("\nPM2 Config:")
        print(json.dumps(pm2_config, indent=2))
        print("\nMCP Config:")
        print(json.dumps(mcp_config, indent=2))


if __name__ == '__main__':
    main()
