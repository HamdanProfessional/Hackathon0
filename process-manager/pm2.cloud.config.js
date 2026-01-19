/**
 * PM2 Configuration for CLOUD VM (Platinum Tier)
 *
 * Cloud runs ONLY (24/7 Always-On):
 * - Email triage + draft replies
 * - Social post drafts/scheduling
 * - Watchers (Gmail, Calendar, Slack, Odoo)
 * - AI Auto-Approver (draft-only mode)
 * - Git sync push
 *
 * Cloud NEVER runs:
 * - WhatsApp Watcher (local session required)
 * - Email/Calendar/Slack senders (approval needed)
 * - Social media posters (approval needed)
 * - WhatsApp/banking/payment actions
 *
 * Environment: Cloud VM (Ubuntu 22.04)
 * Project Root: /root/AI_EMPLOYEE_APP
 */

const path = require('path');

const PROJECT_ROOT = '/root/AI_EMPLOYEE_APP';
const VAULT_PATH = path.join(PROJECT_ROOT, 'AI_Employee_Vault');

module.exports = {
  apps: [
    // ============================================================
    // CLOUD WATCHERS (Detection Only - Draft Replies)
    // ============================================================

    {
      name: 'gmail-watcher',
      script: path.join(PROJECT_ROOT, 'venv', 'bin', 'python'),
      args: '-m watchers.gmail_watcher --vault ' + VAULT_PATH + ' --credentials ' + path.join(PROJECT_ROOT, 'mcp-servers', 'email-mcp', 'credentials.json'),
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: '500M',
      env: {
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'utf-8',
        'CLOUD_MODE': 'true'
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'gmail-watcher-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'gmail-watcher-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'calendar-watcher',
      script: path.join(PROJECT_ROOT, 'venv', 'bin', 'python'),
      args: '-m watchers.calendar_watcher --vault ' + VAULT_PATH,
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: '300M',
      env: {
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'utf-8',
        'CLOUD_MODE': 'true'
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'calendar-watcher-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'calendar-watcher-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'slack-watcher',
      script: path.join(PROJECT_ROOT, 'venv', 'bin', 'python'),
      args: '-m watchers.slack_watcher --vault ' + VAULT_PATH,
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: '300M',
      env: {
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'utf-8',
        'CLOUD_MODE': 'true'
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'slack-watcher-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'slack-watcher-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'odoo-watcher',
      script: path.join(PROJECT_ROOT, 'venv', 'bin', 'python'),
      args: '-m watchers.odoo_watcher --vault ' + VAULT_PATH,
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: '300M',
      env: {
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'utf-8',
        'CLOUD_MODE': 'true'
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'odoo-watcher-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'odoo-watcher-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ============================================================
    // CLOUD AI AUTO-APPROVER (Draft-Only Mode)
    // ============================================================

    {
      name: 'auto-approver',
      script: path.join(PROJECT_ROOT, '.claude', 'skills', 'approval-manager', 'scripts', 'auto_approver.py'),
      args: '--vault ' + VAULT_PATH + ' --mode cloud-draft',
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: true,
      watch: false,
      max_restarts: 10,
      max_memory_restart: '500M',
      env: {
        'ANTHROPIC_API_KEY': process.env.ANTHROPIC_API_KEY,
        'PYTHONPATH': PROJECT_ROOT,
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'utf-8',
        'CLOUD_MODE': 'true'
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'auto-approver-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'auto-approver-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ============================================================
    // GIT SYNC PUSH (Every 5 minutes)
    // ============================================================

    {
      name: 'git-sync-push',
      script: './scripts/git_sync_push.sh',
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: false,
      cron_restart: '*/5 * * * *',
      watch: false,
      env: {
        'PYTHONUNBUFFERED': '1'
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'git-sync-push-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'git-sync-push-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ============================================================
    // CLOUD HEALTH MONITOR
    // ============================================================

    {
      name: 'cloud-health-monitor',
      script: path.join(PROJECT_ROOT, 'scripts', 'cloud_health_monitor.py'),
      args: '--vault ' + VAULT_PATH + ' --interval 300',
      interpreter: path.join(PROJECT_ROOT, 'venv', 'bin', 'python'),
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      env: {
        'PYTHONUNBUFFERED': '1'
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'health-monitor-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'health-monitor-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
  ]
};
