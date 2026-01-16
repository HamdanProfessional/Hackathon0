/**
 * PM2 Configuration
 *
 * Process Manager 2 configuration for running all AI Employee processes.
 * All paths are relative to process-manager/ directory.
 */

module.exports = {
  "apps": [
    // ==================== WATCHERS ====================
    {
      name: "gmail-watcher",
      script: "../scripts/run_gmail_watcher.py",
      args: "--vault ../AI_Employee_Vault --credentials ../mcp-servers/email-mcp/credentials.json",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
      }
    },

    {
      name: "calendar-watcher",
      script: "../scripts/run_calendar_watcher.py",
      args: "--vault ../AI_Employee_Vault --credentials ../mcp-servers/calendar-mcp/credentials.json",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
      }
    },

    {
      name: "slack-watcher",
      script: "../scripts/run_slack_watcher.py",
      args: "--vault ../AI_Employee_Vault",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
      }
    },

    {
      name: "odoo-watcher",
      script: "../scripts/run_odoo_watcher.py",
      args: "--vault ../AI_Employee_Vault --interval 300",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
        // TODO: Set Odoo credentials via environment variables:
        // ODOO_URL, ODOO_DB, OODO_USERNAME, ODOO_PASSWORD
      }
    },

    {
      name: "filesystem-watcher",
      script: "../scripts/run_filesystem_watcher.py",
      args: "--vault ../AI_Employee_Vault --watch-folder Inbox",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
      }
    },

    {
      name: "whatsapp-watcher",
      script: "../scripts/run_whatsapp_watcher.py",
      args: "--vault ../AI_Employee_Vault",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
      }
    },

    // ==================== APPROVAL MONITORS ====================
    {
      name: "email-approval-monitor",
      script: "../scripts/monitors/email_approval_monitor.py",
      args: "--vault ../AI_Employee_Vault",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
      }
    },

    {
      name: "calendar-approval-monitor",
      script: "../scripts/monitors/calendar_approval_monitor.py",
      args: "--vault ../AI_Employee_Vault",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
      }
    },

    {
      name: "slack-approval-monitor",
      script: "../scripts/monitors/slack_approval_monitor.py",
      args: "--vault ../AI_Employee_Vault",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
      }
    },

    {
      name: "linkedin-approval-monitor",
      script: "../scripts/social-media/linkedin_approval_monitor.py",
      args: "--vault ../AI_Employee_Vault",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "LINKEDIN_DRY_RUN": "false"
      }
    },

    {
      name: "twitter-approval-monitor",
      script: "../scripts/social-media/twitter_approval_monitor.py",
      args: "--vault ../AI_Employee_Vault",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "TWITTER_DRY_RUN": "false"
      }
    },

    {
      name: "facebook-approval-monitor",
      script: "../scripts/social-media/facebook-approval-monitor.py",
      args: "--vault ../AI_Employee_Vault",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "META_DRY_RUN": "false"
      }
    },

    {
      name: "instagram-approval-monitor",
      script: "../scripts/social-media/instagram-approval-monitor.py",
      args: "--vault ../AI_Employee_Vault",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "META_DRY_RUN": "false"
      }
    },

    // ==================== CRON JOBS ====================
    {
      name: "monday-ceo-briefing",
      script: "../.claude/skills/weekly-briefing/scripts/generate_ceo_briefing.py",
      args: "--vault ../AI_Employee_Vault",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: false,
      watch: false,
      max_restarts: 3,
      cron_schedule: "0 7 * * 1",  // 7 AM every Monday
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
      }
    },

    {
      name: "daily-review",
      script: "../.claude/skills/daily-review/scripts/generate_daily_plan.py",
      args: "--vault ../AI_Employee_Vault",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: false,
      watch: false,
      max_restarts: 3,
      cron_schedule: "0 6 * * 1-5",  // 6 AM weekdays
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
      }
    },

    {
      name: "social-media-scheduler",
      script: "../.claude/skills/social-media-manager/scripts/generate_linkedin_ai.py",
      args: "--vault ../AI_Employee_Vault",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: false,
      watch: false,
      max_restarts: 3,
      cron_schedule: "0 8 * * 1,3,5",  // 8 AM Mon/Wed/Fri
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
      }
    },

    {
      name: "audit-log-cleanup",
      script: "../scripts/cleanup_old_logs.py",
      args: "--vault ../AI_Employee_Vault --days 90",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: false,
      watch: false,
      max_restarts: 3,
      cron_schedule: "0 3 * * 0",  // 3 AM Sundays
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
      }
    },

    // ==================== DASHBOARD ====================
    {
      name: "ai-employee-dashboard",
      script: "../dashboard/server.js",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PORT": "3000",
        "NODE_ENV": "production"
      }
    }
  ]
};
