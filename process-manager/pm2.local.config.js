/**
 * PM2 Configuration for LOCAL MACHINE (Platinum Tier)
 *
 * Local runs ONLY:
 * - WhatsApp Watcher (session required)
 * - Filesystem Watcher (Inbox monitoring)
 * - Approval Monitors (execute approved actions)
 * - Dashboard (single writer rule)
 * - Vault Sync (push to cloud)
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
      script: './watchers/whatsapp_watcher_playwright.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault',
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
      script: './watchers/filesystem_watcher.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault',
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
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --live-mode',
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
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --live-mode',
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
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --live-mode',
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
      script: './scripts/social-media/linkedin_approval_monitor.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --live-mode',
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
      script: './scripts/social-media/twitter_approval_monitor.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --live-mode',
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
      script: './scripts/social-media/facebook_approval_monitor.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --live-mode',
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
      script: './scripts/social-media/instagram_approval_monitor.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --live-mode',
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
    // VAULT SYNC (Push to Cloud)
    // ============================================================

    {
      name: 'vault-sync-push',
      script: './scripts/vault_sync_push.sh',
      interpreter: '/bin/bash',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      cron_restart: '*/2 * * * *',  // Every 2 minutes
      error_file: './logs/vault-sync-push-error.log',
      out_file: './logs/vault-sync-push-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ============================================================
    // DASHBOARD UPDATE MERGER (Cloud Updates -> Local Dashboard)
    // ============================================================

    {
      name: 'dashboard-update-merger-local',
      script: './scripts/merge_dashboard_updates.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault --local-mode',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      cron_restart: '*/1 * * * *',  // Every 1 minute
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/dashboard-merger-local-error.log',
      out_file: './logs/dashboard-merger-local-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // ============================================================
    // SCHEDULED TASKS (Local Only)
    // ============================================================

    {
      name: 'daily-review',
      script: './scripts/scheduled_tasks/daily_review.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault',
      cwd: './',
      instances: 1,
      autorestart: false,
      cron_restart: '0 6 * * 1-5',  // Mon-Fri 6 AM
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/daily-review-error.log',
      out_file: './logs/daily-review-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    {
      name: 'monday-ceo-briefing',
      script: './scripts/scheduled_tasks/monday_ceo_briefing.py',
      interpreter: 'python3',
      args: '--vault AI_Employee_Vault',
      cwd: './',
      instances: 1,
      autorestart: false,
      cron_restart: '0 7 * * 1',  // Monday 7 AM
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/monday-briefing-error.log',
      out_file: './logs/monday-briefing-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
  ]
};
