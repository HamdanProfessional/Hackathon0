/**
 * PM2 Configuration for LOCAL MACHINE (Platinum Tier) - Windows Compatible
 *
 * Local runs ONLY:
 * - WhatsApp Watcher (session required)
 * - Filesystem Watcher (Inbox monitoring)
 * - Approval Monitors (execute approved actions)
 * - Dashboard (single writer rule)
 *
 * Local NEVER runs:
 * - Gmail/Calendar/Slack watchers (cloud handles these)
 * - Odoo watcher (cloud handles this)
 *
 * Environment: LIVE_MODE for all approval monitors
 */

module.exports = {
  apps: [
    // ============================================================
    // LOCAL-ONLY WATCHERS
    // ============================================================

    {
      name: 'whatsapp-watcher',
      script: 'python',
      interpreter: 'none',
      args: '-m watchers.whatsapp_watcher_playwright --vault AI_Employee_Vault',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/whatsapp-watcher-error.log',
      out_file: './logs/whatsapp-watcher-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'filesystem-watcher',
      script: 'python',
      interpreter: 'none',
      args: '-m watchers.filesystem_watcher --vault AI_Employee_Vault --watch-folder AI_Employee_Vault/Inbox',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/filesystem-watcher-error.log',
      out_file: './logs/filesystem-watcher-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ============================================================
    // LOCAL APPROVAL MONITORS (Execute Approved Actions)
    // ============================================================

    {
      name: 'email-approval-monitor',
      script: './scripts/monitors/email_approval_monitor.py',
      interpreter: 'python',
      args: '--vault AI_Employee_Vault',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        EMAIL_DRY_RUN: 'false',  // LIVE MODE
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/email-approval-monitor-error.log',
      out_file: './logs/email-approval-monitor-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'calendar-approval-monitor',
      script: './scripts/monitors/calendar_approval_monitor.py',
      interpreter: 'python',
      args: '--vault AI_Employee_Vault',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/calendar-approval-monitor-error.log',
      out_file: './logs/calendar-approval-monitor-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'slack-approval-monitor',
      script: './scripts/monitors/slack_approval_monitor.py',
      interpreter: 'python',
      args: '--vault AI_Employee_Vault',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/slack-approval-monitor-error.log',
      out_file: './logs/slack-approval-monitor-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ============================================================
    // SOCIAL MEDIA APPROVAL MONITORS (LIVE MODE)
    // ============================================================

    {
      name: 'linkedin-approval-monitor',
      script: './.claude/skills/linkedin-manager/scripts/linkedin_approval_monitor.py',
      interpreter: 'python',
      args: '--vault AI_Employee_Vault',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        LINKEDIN_DRY_RUN: 'false',  // LIVE MODE
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/linkedin-approval-monitor-error.log',
      out_file: './logs/linkedin-approval-monitor-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'twitter-approval-monitor',
      script: './.claude/skills/twitter-manager/scripts/twitter_approval_monitor.py',
      interpreter: 'python',
      args: '--vault AI_Employee_Vault',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        TWITTER_DRY_RUN: 'false',  // LIVE MODE
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/twitter-approval-monitor-error.log',
      out_file: './logs/twitter-approval-monitor-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'facebook-approval-monitor',
      script: './.claude/skills/facebook-instagram-manager/scripts/facebook-approval-monitor.py',
      interpreter: 'python',
      args: '--vault AI_Employee_Vault',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        FACEBOOK_DRY_RUN: 'false',  // LIVE MODE
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/facebook-approval-monitor-error.log',
      out_file: './logs/facebook-approval-monitor-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'instagram-approval-monitor',
      script: './.claude/skills/facebook-instagram-manager/scripts/instagram-approval-monitor.py',
      interpreter: 'python',
      args: '--vault AI_Employee_Vault',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        INSTAGRAM_DRY_RUN: 'false',  // LIVE MODE
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/instagram-approval-monitor-error.log',
      out_file: './logs/instagram-approval-monitor-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ============================================================
    // LOCAL DASHBOARD (Single Writer Rule)
    // ============================================================

    {
      name: 'ai-employee-dashboard',
      script: './dashboard/server.js',
      interpreter: 'node',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        PORT: '3000',
        NODE_ENV: 'production'
      },
      error_file: './logs/dashboard-error.log',
      out_file: './logs/dashboard-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ============================================================
    // SCHEDULED TASKS (Local Only) - Disabled for now
    // ============================================================

    // Daily review and Monday briefing can be added later
  ]
};
