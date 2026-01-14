/**
 * PM2 Configuration - FIXED
 *
 * Process Manager 2 configuration file for running all AI Employee processes.
 *
 * Usage:
 *   pm2 start pm2.config.js
 *
 * To set up:
 *   npm install -g pm2
 *   pm2 start pm2.config.js
 *   pm2 save
 *   pm2 startup
 */

module.exports = {
  "apps": [
    {
      name: "gmail-watcher",
      script: "run_gmail_watcher.py",
      args: "--vault AI_Employee_Vault --credentials mcp-servers/email-mcp/credentials.json",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1"
      }
    },

    {
      name: "calendar-watcher",
      script: "run_calendar_watcher.py",
      args: "--vault AI_Employee_Vault --credentials mcp-servers/calendar-mcp/credentials.json",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1"
      }
    },

    // XERO WATCHER - Uses Xero MCP for data (MCP version with wrapper)
    {
      name: "xero-watcher",
      script: "run_xero_watcher.py",
      args: "--vault AI_Employee_Vault",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1"
      }
    },

    {
      name: "slack-watcher",
      script: "run_slack_watcher.py",
      args: "--vault AI_Employee_Vault",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1"
        // NOTE: SLACK_BOT_TOKEN should be set in environment or .env file
        // DO NOT hardcode tokens here as this file may be committed to git
      }
    },

    {
      name: "filesystem-watcher",
      script: "run_filesystem_watcher.py",
      args: "--vault AI_Employee_Vault --watch-folder AI_Employee_Vault/Inbox",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1"
      }
    },

    {
      name: "whatsapp-watcher",
      script: "run_whatsapp_watcher.py",
      args: "--vault AI_Employee_Vault --session ./whatsapp_session --headless",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1"
      },
      // Commented out by default - requires Playwright setup
      // To enable: uncomment and run: pip install playwright && playwright install chromium
      // Also requires first-time WhatsApp login: run without --headless flag first
      // autostart: false
    },

    // Approval Monitors - Watch /Approved/ folder and execute actions
    // These monitors handle the human-in-the-loop workflow

    {
      name: "email-approval-monitor",
      script: "scripts/monitors/email_approval_monitor.py",
      args: "--vault AI_Employee_Vault",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "300M",
      env: {
        "PYTHONUNBUFFERED": "1"
      }
    },

    {
      name: "calendar-approval-monitor",
      script: "scripts/monitors/calendar_approval_monitor.py",
      args: "--vault AI_Employee_Vault",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "300M",
      env: {
        "PYTHONUNBUFFERED": "1"
      }
    },

    {
      name: "slack-approval-monitor",
      script: "scripts/monitors/slack_approval_monitor.py",
      args: "--vault AI_Employee_Vault",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "300M",
      env: {
        "PYTHONUNBUFFERED": "1"
        // NOTE: SLACK_BOT_TOKEN should be set in environment or .env file
        // DO NOT hardcode tokens here as this file may be committed to git
      }
    },

    {
      name: "linkedin-approval-monitor",
      script: "scripts/social-media/linkedin_approval_monitor.py",
      args: "--vault AI_Employee_Vault",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "300M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "LINKEDIN_DRY_RUN": "false"
      }
    },

    {
      name: "twitter-approval-monitor",
      script: "scripts/social-media/twitter_approval_monitor.py",
      args: "--vault AI_Employee_Vault",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "300M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "TWITTER_DRY_RUN": "false"
      }
    },

    {
      name: "meta-approval-monitor",
      script: "scripts/social-media/meta_approval_monitor.py",
      args: "--vault AI_Employee_Vault",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "300M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "META_DRY_RUN": "false"
      }
    },

    // Scheduled tasks for periodic operations
    {
      name: "daily-briefing",
      script: ".claude/skills/weekly-briefing/scripts/generate_ceo_briefing.py",
      args: "--vault AI_Employee_Vault",
      interpreter: "python",
      cron: "0 7 * * *",  // 7 AM daily
      autorestart: false,  // Don't auto-restart cron jobs
      watch: false,
      env: {
        "PYTHONUNBUFFERED": "1"
      }
    },
    {
      name: "daily-review",
      script: ".claude/skills/daily-review/scripts/generate_daily_plan.py",
      args: "--vault AI_Employee_Vault",
      interpreter: "python",
      cron: "0 6 * * 1-5",  // 6 AM weekdays
      autorestart: false,
      watch: false,
      env: {
        "PYTHONUNBUFFERED": "1"
      }
    },
    {
      name: "social-media-scheduler",
      script: ".claude/skills/social-media-manager/scripts/generate_content_calendar.py",
      args: "--vault AI_Employee_Vault",
      interpreter: "python",
      cron: "0 8 * * 1,3,5",  // 8 AM Mon, Wed, Fri
      autorestart: false,
      watch: false,
      env: {
        "PYTHONUNBUFFERED": "1"
      }
    },
    {
      name: "invoice-review",
      script: ".claude/skills/xero-manager/scripts/check_overdue_invoices.py",
      args: "--vault AI_Employee_Vault",
      interpreter: "python",
      cron: "0 17 * * 1",  // 5 PM Mondays
      autorestart: false,
      watch: false,
      env: {
        "PYTHONUNBUFFERED": "1"
      }
    },
    {
      name: "audit-log-cleanup",
      script: "scripts/cleanup_old_logs.py",
      args: "--vault AI_Employee_Vault --days 90",
      interpreter: "python",
      cron: "0 3 * * 0",  // 3 AM Sundays
      autorestart: false,
      watch: false,
      env: {
        "PYTHONUNBUFFERED": "1"
      }
    },
  ]
};
