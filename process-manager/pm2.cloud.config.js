/**
 * PM2 Configuration for CLOUD VM (Platinum Tier)
 *
 * Cloud runs ONLY:
 * - Watchers (Gmail, Calendar, Slack, Odoo)
 * - AI Auto-Approver (Claude 3 Haiku)
 * - Health Monitor
 * - Vault Sync (pull from local)
 *
 * Cloud NEVER runs:
 * - WhatsApp (local session required)
 * - Banking/payment actions
 * - Final send/post actions
 *
 * Environment: CLOUD_MODE=true, DRAFT_ONLY=true
 */

module.exports = {
  apps: [
    // ============================================================
    // CLOUD WATCHERS (Perception Layer)
    // ============================================================

    {
      name: 'gmail-watcher-cloud',
      script: './venv/bin/python',
      args: '-m watchers.gmail_watcher --vault AI_Employee_Vault --cloud-mode --draft-only',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        CLOUD_MODE: 'true',
        DRAFT_ONLY: 'true',
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/cloud-gmail-watcher-error.log',
      out_file: './logs/cloud-gmail-watcher-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'calendar-watcher-cloud',
      script: './venv/bin/python',
      args: '-m watchers.calendar_watcher --vault AI_Employee_Vault --cloud-mode',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        CLOUD_MODE: 'true',
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/cloud-calendar-watcher-error.log',
      out_file: './logs/cloud-calendar-watcher-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'slack-watcher-cloud',
      script: './venv/bin/python',
      args: '-m watchers.slack_watcher --vault AI_Employee_Vault --cloud-mode',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        CLOUD_MODE: 'true',
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/cloud-slack-watcher-error.log',
      out_file: './logs/cloud-slack-watcher-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'odoo-watcher-cloud',
      script: './venv/bin/python',
      args: '-m watchers.odoo_watcher --vault AI_Employee_Vault --dry-run',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/cloud-odoo-watcher-error.log',
      out_file: './logs/cloud-odoo-watcher-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ============================================================
    // CLOUD AI AUTO-APPROVER
    // ============================================================

    {
      name: 'auto-approver-cloud',
      script: './scripts/auto_approver_glm.py',
      interpreter: '/home/aiemployee/AI_EMPLOYEE_APP/venv/bin/python',
      args: '--vault AI_Employee_Vault',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        GLM_API_KEY: process.env.GLM_API_KEY,
        GLM_API_URL: process.env.GLM_API_URL || 'https://api.z.ai/api/paas/v4',
        CLOUD_MODE: 'true',
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/cloud-auto-approver-error.log',
      out_file: './logs/cloud-auto-approver-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ============================================================
    // CLOUD HEALTH MONITOR
    // ============================================================

    {
      name: 'cloud-health-monitor',
      script: './scripts/cloud_health_monitor.py',
      interpreter: '/home/aiemployee/AI_EMPLOYEE_APP/venv/bin/python',
      args: '--vault AI_Employee_Vault --interval 300',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/cloud-health-monitor-error.log',
      out_file: './logs/cloud-health-monitor-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ============================================================
    // VAULT SYNC (Pull from Local)
    // ============================================================

    // Vault sync and dashboard merger disabled for now
    // Re-enable after setting up GitHub repo for vault sync
  ]
};
