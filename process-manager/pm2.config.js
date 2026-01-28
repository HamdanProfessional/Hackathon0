/**
 * PM2 Configuration
 *
 * Process Manager 2 configuration for running all AI Employee processes.
 * Uses dynamic path resolution for cross-platform compatibility.
 */

const path = require('path');

// Project root directory - dynamically resolved for cross-platform compatibility
// Works on Windows, Linux, and macOS
const PROJECT_ROOT = process.cwd();
const VAULT_PATH = path.join(PROJECT_ROOT, 'AI_Employee_Vault');

module.exports = {
  "apps": [
    // ==================== WATCHERS ====================
    {
      name: "gmail-watcher",
      script: path.join(PROJECT_ROOT, ".claude/skills/email-manager/scripts", "run_gmail_watcher.py"),
      args: "--vault " + VAULT_PATH + " --credentials " + path.join(PROJECT_ROOT, "mcp-servers", "email-mcp", "credentials.json"),
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
      script: path.join(PROJECT_ROOT, ".claude/skills/calendar-manager/scripts", "run_calendar_watcher.py"),
      args: "--vault " + VAULT_PATH + " --credentials " + path.join(PROJECT_ROOT, "mcp-servers", "calendar-mcp", "credentials.json"),
      interpreter: "python",
      exec_mode: "fork",
      autorestart: false,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      instances: 0,
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
      }
    },

    {
      name: "slack-watcher",
      script: path.join(PROJECT_ROOT, ".claude/skills/slack-manager/scripts", "run_slack_watcher.py"),
      args: "--vault " + VAULT_PATH,
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
      script: path.join(PROJECT_ROOT, ".claude/skills/odoo-manager/scripts", "run_odoo_watcher.py"),
      args: "--vault " + VAULT_PATH + " --interval 300",
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
        // ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
      }
    },

    {
      name: "filesystem-watcher",
      script: path.join(PROJECT_ROOT, ".claude/skills/filesystem-manager/scripts", "run_filesystem_watcher.py"),
      args: "--vault " + VAULT_PATH + " --watch-folder Inbox",
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
      script: path.join(PROJECT_ROOT, ".claude/skills/whatsapp-manager/scripts", "run_whatsapp_watcher.py"),
      args: "--vault " + VAULT_PATH,
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": PROJECT_ROOT
      }
    },

    // ==================== APPROVAL MONITORS ====================
    {
      name: "email-approval-monitor",
      script: path.join(PROJECT_ROOT, ".claude", "skills", "email-manager", "scripts", "email_approval_monitor.py"),
      args: "--vault " + VAULT_PATH,
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": PROJECT_ROOT
      }
    },

    {
      name: "calendar-approval-monitor",
      script: path.join(PROJECT_ROOT, ".claude", "skills", "calendar-manager", "scripts", "calendar_approval_monitor.py"),
      args: "--vault " + VAULT_PATH,
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
      script: path.join(PROJECT_ROOT, ".claude", "skills", "slack-manager", "scripts", "slack_approval_monitor.py"),
      args: "--vault " + VAULT_PATH,
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
      script: path.join(PROJECT_ROOT, ".claude", "skills", "linkedin-manager", "scripts", "linkedin_approval_monitor.py"),
      args: "--vault " + VAULT_PATH,
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
      script: path.join(PROJECT_ROOT, ".claude", "skills", "twitter-manager", "scripts", "twitter_approval_monitor.py"),
      args: "--vault " + VAULT_PATH,
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
      script: path.join(PROJECT_ROOT, ".claude", "skills", "facebook-instagram-manager", "scripts", "facebook-approval-monitor.py"),
      args: "--vault " + VAULT_PATH,
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "FACEBOOK_DRY_RUN": "false"
      }
    },

    {
      name: "instagram-approval-monitor",
      script: path.join(PROJECT_ROOT, ".claude", "skills", "facebook-instagram-manager", "scripts", "instagram-approval-monitor.py"),
      args: "--vault " + VAULT_PATH,
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "INSTAGRAM_DRY_RUN": "false"
      }
    },

    {
      name: "whatsapp-approval-monitor",
      script: path.join(PROJECT_ROOT, ".claude", "skills", "whatsapp-manager", "scripts", "whatsapp_approval_monitor.py"),
      args: "--vault " + VAULT_PATH,
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "WHATSAPP_DRY_RUN": "false"
      }
    },

    // ==================== AUTO-APPROVER ====================
    {
      name: "auto-approver",
      script: path.join(PROJECT_ROOT, ".claude/skills/approval-manager/scripts", "auto_approver.py"),
      args: "--vault " + VAULT_PATH,
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "ANTHROPIC_API_KEY": process.env.ANTHROPIC_API_KEY || ""
      }
    },

    // ==================== A2A MESSAGE BROKER ====================
    {
      name: "a2a-message-broker",
      script: path.join(PROJECT_ROOT, "scripts", "a2a_message_broker.py"),
      args: "--vault " + VAULT_PATH,
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": PROJECT_ROOT,
        "BROKER_CHECK_INTERVAL": "5"
      }
    },

    // ==================== CRON JOBS ====================
    {
      name: "monday-ceo-briefing",
      script: path.join(PROJECT_ROOT, ".claude", "skills", "weekly-briefing", "scripts", "generate_ceo_briefing.py"),
      args: "--vault " + VAULT_PATH,
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
      script: path.join(PROJECT_ROOT, ".claude", "skills", "daily-review", "scripts", "generate_daily_plan.py"),
      args: "--vault " + VAULT_PATH,
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
      script: path.join(PROJECT_ROOT, ".claude", "skills", "social-media-manager", "scripts", "generate_linkedin_ai.py"),
      args: "--vault " + VAULT_PATH,
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
      script: path.join(PROJECT_ROOT, "scripts", "cleanup_old_logs.py"),
      args: "--vault " + VAULT_PATH + " --days 90",
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

    {
      name: "research-processor",
      script: path.join(PROJECT_ROOT, ".claude", "skills", "research-linkedin-generator", "scripts", "research.py"),
      args: "--vault " + VAULT_PATH + " --daily",
      interpreter: "python",
      exec_mode: "fork",
      autorestart: false,
      watch: false,
      max_restarts: 3,
      cron_schedule: "0 9 * * *",  // 9 AM daily
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": PROJECT_ROOT,
        "GLM_API_KEY": process.env.GLM_API_KEY || "",
        "GLM_API_URL": process.env.GLM_API_URL || "https://api.z.ai/api/coding/paas/v4",
        "USE_CDP": "false",  // Use headless mode for cloud VM
        "HEADLESS": "true"
      }
    },

    // ==================== AI ITEM PROCESSOR ====================
    // Processes items from Needs_Action/ using Claude API (AI-driven decisions)
    // This transforms the system from "automation" to "AI Employee"
    {
      name: "ai-item-processor",
      script: path.join(PROJECT_ROOT, "scripts", "ai_item_processor.py"),
      args: "--vault " + VAULT_PATH,
      interpreter: "python",
      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: "500M",
      env: {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": PROJECT_ROOT,
        "ANTHROPIC_API_KEY": process.env.ANTHROPIC_API_KEY || ""
      }
    },

    // ==================== DASHBOARD ====================
    {
      name: "ai-employee-dashboard",
      script: path.join(PROJECT_ROOT, "dashboard", "server.js"),
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
