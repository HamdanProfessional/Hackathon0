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
      script: './run_gmail_watcher.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --cloud-mode --draft-only',
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
      script: './run_calendar_watcher.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --cloud-mode',
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
      script: './run_slack_watcher.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --cloud-mode',
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
      script: './run_odoo_watcher.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --draft-only',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        ODOO_DRAFT_ONLY: 'true',
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
      interpreter: 'python3',
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
      interpreter: 'python3',
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

    {
      name: 'vault-sync-pull',
      script: './scripts/vault_sync_pull.sh',
      interpreter: '/bin/bash',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      cron_restart: '*/2 * * * *',  // Every 2 minutes
      error_file: './logs/vault-sync-pull-error.log',
      out_file: './logs/vault-sync-pull-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ============================================================
    // DASHBOARD UPDATE MERGER (Cloud -> Local)
    // ============================================================

    {
      name: 'dashboard-update-merger',
      script: './scripts/merge_dashboard_updates.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      cron_restart: '*/5 * * * *',  // Every 5 minutes
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/dashboard-merger-error.log',
      out_file: './logs/dashboard-merger-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
  ]
};
