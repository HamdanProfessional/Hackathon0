/**
 * PM2 Configuration for LOCAL MACHINE (Platinum Tier)
 *
 * Local runs ONLY:
 * - WhatsApp Watcher (session required)
 * - Filesystem Watcher (Inbox monitoring)
 * - Approval Monitors (execute approved actions via MCP)
 * - Dashboard (single writer rule)
 * - Git sync pull
 * - Dashboard merger (merges /Updates/ into Dashboard.md)
 *
 * Local NEVER runs:
 * - Gmail/Calendar/Slack watchers (cloud handles these)
 * - Odoo watcher (cloud handles this)
 * - AI Auto-Approver (cloud handles triage)
 *
 * Environment: Windows Local Machine
 * Project Root: C:\Users\User\Desktop\AI_EMPLOYEE_APP
 */

const path = require('path');

const PROJECT_ROOT = 'C:\\Users\\User\\Desktop\\AI_EMPLOYEE_APP';
const VAULT_PATH = path.join(PROJECT_ROOT, 'AI_Employee_Vault');

module.exports = {
  apps: [
    // ============================================================
    // LOCAL-ONLY WATCHERS (Requires Local Resources)
    // ============================================================

    {
      name: 'whatsapp-watcher',
      script: 'python',
      args: '-m watchers.whatsapp_watcher_playwright --vault ' + VAULT_PATH + ' --session ./whatsapp_session',
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'utf-8',
        'PYTHONPATH': PROJECT_ROOT
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'whatsapp-watcher-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'whatsapp-watcher-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'filesystem-watcher',
      script: 'python',
      args: '-m watchers.filesystem_watcher --vault ' + VAULT_PATH + ' --watch-folder ' + path.join(VAULT_PATH, 'Inbox'),
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      env: {
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'utf-8',
        'PYTHONPATH': PROJECT_ROOT
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'filesystem-watcher-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'filesystem-watcher-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ============================================================
    // LOCAL APPROVAL MONITORS (Execute Approved Actions)
    // ============================================================

    {
      name: 'email-approval-monitor',
      script: path.join(PROJECT_ROOT, '.claude', 'skills', 'email-manager', 'scripts', 'email_approval_monitor.py'),
      interpreter: 'python',
      args: '--vault ' + VAULT_PATH,
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        'EMAIL_DRY_RUN': 'false',  // LIVE MODE
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'utf-8',
        'PYTHONPATH': PROJECT_ROOT
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'email-approval-monitor-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'email-approval-monitor-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'calendar-approval-monitor',
      script: path.join(PROJECT_ROOT, '.claude', 'skills', 'calendar-manager', 'scripts', 'calendar_approval_monitor.py'),
      interpreter: 'python',
      args: '--vault ' + VAULT_PATH,
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'utf-8',
        'PYTHONPATH': PROJECT_ROOT
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'calendar-approval-monitor-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'calendar-approval-monitor-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'slack-approval-monitor',
      script: path.join(PROJECT_ROOT, '.claude', 'skills', 'slack-manager', 'scripts', 'slack_approval_monitor.py'),
      interpreter: 'python',
      args: '--vault ' + VAULT_PATH,
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'utf-8',
        'PYTHONPATH': PROJECT_ROOT
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'slack-approval-monitor-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'slack-approval-monitor-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ============================================================
    // SOCIAL MEDIA APPROVAL MONITORS (LIVE MODE)
    // ============================================================

    {
      name: 'linkedin-approval-monitor',
      script: path.join(PROJECT_ROOT, '.claude', 'skills', 'linkedin-manager', 'scripts', 'linkedin_approval_monitor.py'),
      interpreter: 'python',
      args: '--vault ' + VAULT_PATH,
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        'LINKEDIN_DRY_RUN': 'false',  // LIVE MODE
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'utf-8',
        'PYTHONPATH': PROJECT_ROOT
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'linkedin-approval-monitor-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'linkedin-approval-monitor-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'twitter-approval-monitor',
      script: path.join(PROJECT_ROOT, '.claude', 'skills', 'twitter-manager', 'scripts', 'twitter_approval_monitor.py'),
      interpreter: 'python',
      args: '--vault ' + VAULT_PATH,
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        'TWITTER_DRY_RUN': 'false',  // LIVE MODE
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'utf-8',
        'PYTHONPATH': PROJECT_ROOT
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'twitter-approval-monitor-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'twitter-approval-monitor-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'facebook-approval-monitor',
      script: path.join(PROJECT_ROOT, '.claude', 'skills', 'facebook-instagram-manager', 'scripts', 'facebook-approval-monitor.py'),
      interpreter: 'python',
      args: '--vault ' + VAULT_PATH,
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        'FACEBOOK_DRY_RUN': 'false',  // LIVE MODE
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'utf-8',
        'PYTHONPATH': PROJECT_ROOT
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'facebook-approval-monitor-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'facebook-approval-monitor-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'instagram-approval-monitor',
      script: path.join(PROJECT_ROOT, '.claude', 'skills', 'facebook-instagram-manager', 'scripts', 'instagram-approval-monitor.py'),
      interpreter: 'python',
      args: '--vault ' + VAULT_PATH,
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        'INSTAGRAM_DRY_RUN': 'false',  // LIVE MODE
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'utf-8',
        'PYTHONPATH': PROJECT_ROOT
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'instagram-approval-monitor-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'instagram-approval-monitor-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ============================================================
    // LOCAL DASHBOARD (Single Writer Rule)
    // ============================================================

    {
      name: 'ai-employee-dashboard',
      script: path.join(PROJECT_ROOT, 'dashboard', 'server.js'),
      interpreter: 'node',
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        'PORT': '3000',
        'NODE_ENV': 'production'
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'dashboard-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'dashboard-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ============================================================
    // GIT SYNC PULL (Every 5 minutes)
    // ============================================================

    {
      name: 'git-sync-pull',
      script: path.join(PROJECT_ROOT, 'scripts', 'git_sync_pull.bat'),
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: false,
      cron_restart: '*/5 * * * *',
      watch: false,
      env: {
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'utf-8',
        'PYTHONPATH': PROJECT_ROOT
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'git-sync-pull-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'git-sync-pull-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ============================================================
    // DASHBOARD MERGER (Merges /Updates/ into Dashboard.md)
    // ============================================================

    {
      name: 'dashboard-merger',
      script: path.join(PROJECT_ROOT, 'scripts', 'dashboard_merger.py'),
      args: '--vault ' + VAULT_PATH,
      interpreter: 'python',
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: false,  // Cron job - no auto-restart
      watch: false,
      max_memory_restart: '200M',
      cron_restart: '*/2 * * * *',  // Every 2 minutes
      env: {
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'utf-8',
        'PYTHONPATH': PROJECT_ROOT
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'dashboard-merger-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'dashboard-merger-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ============================================================
    // SCHEDULED TASKS (Local Only)
    // ============================================================

    {
      name: 'daily-review',
      script: path.join(PROJECT_ROOT, '.claude', 'skills', 'daily-review', 'invoke.py'),
      args: '"generate daily plan"',
      interpreter: 'python',
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: false,
      cron_restart: '0 6 * * 1-5',  // 6 AM weekdays
      watch: false,
      max_memory_restart: '300M',
      env: {
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'utf-8',
        'PYTHONPATH': PROJECT_ROOT
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'daily-review-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'daily-review-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'monday-ceo-briefing',
      script: path.join(PROJECT_ROOT, '.claude', 'skills', 'weekly-briefing', 'invoke.py'),
      args: '"generate ceo briefing"',
      interpreter: 'python',
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: false,
      cron_restart: '0 7 * * 1',  // 7 AM every Monday
      watch: false,
      max_memory_restart: '300M',
      env: {
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'utf-8',
        'PYTHONPATH': PROJECT_ROOT
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'monday-briefing-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'monday-briefing-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'audit-log-cleanup',
      script: path.join(PROJECT_ROOT, 'scripts', 'cleanup_old_logs.py'),
      args: '--vault ' + VAULT_PATH + ' --days 30',
      interpreter: 'python',
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: false,
      cron_restart: '0 3 * * 0',  // 3 AM every Sunday
      watch: false,
      max_memory_restart: '200M',
      env: {
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'utf-8',
        'PYTHONPATH': PROJECT_ROOT
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'audit-log-cleanup-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'audit-log-cleanup-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ============================================================
    // RESEARCH PROCESSOR (Daily LinkedIn Research Posts)
    // ============================================================

    {
      name: 'research-processor',
      script: path.join(PROJECT_ROOT, '.claude', 'skills', 'research-linkedin-generator', 'scripts', 'run_research_processor.py'),
      interpreter: 'python',
      args: '--vault ' + VAULT_PATH,
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: false,
      watch: false,
      max_memory_restart: '500M',
      cron_restart: '0 9 * * 1-5',  // 9 AM weekdays
      env: {
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'utf-8',
        'PYTHONPATH': PROJECT_ROOT,
        'GLM_API_KEY': 'c414057ceccd4e8dae4ae3198f760c7a.BW9M3G4m8ers9woM',
        'GLM_API_URL': 'https://api.z.ai/api/coding/paas/v4'
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'research-processor-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'research-processor-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ============================================================
    // SOCIAL MEDIA SCHEDULER
    // ============================================================

    {
      name: 'social-media-scheduler',
      script: path.join(PROJECT_ROOT, 'scripts', 'social_media_scheduler.py'),
      args: '--vault ' + VAULT_PATH,
      interpreter: 'python',
      cwd: PROJECT_ROOT,
      instances: 1,
      autorestart: false,
      watch: false,
      max_memory_restart: '300M',
      cron_restart: '0 8,12,16 * * 1-5',  // 8 AM, 12 PM, 4 PM weekdays
      env: {
        'PYTHONUNBUFFERED': '1',
        'PYTHONIOENCODING': 'utf-8',
        'PYTHONPATH': PROJECT_ROOT
      },
      error_file: path.join(PROJECT_ROOT, 'logs', 'social-media-scheduler-error.log'),
      out_file: path.join(PROJECT_ROOT, 'logs', 'social-media-scheduler-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
  ]
};
