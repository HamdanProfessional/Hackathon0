#!/usr/bin/env node
/**
 * AI Employee Dashboard - Real-time monitoring
 *
 * Usage:
 *   node dashboard/server.js
 *
 * Access at: http://localhost:3000
 */

const express = require('express');
const path = require('path');
const fs = require('fs');
const { exec, spawn } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

const app = express();
const PORT = 3000;

// System health tracking
let healthHistory = [];
const MAX_HEALTH_HISTORY = 60; // Keep 60 data points (1 minute per point)

// Determine vault path (handles both direct and PM2 execution)
let VAULT_PATH;
// Check environment variable first (cross-platform)
if (process.env.VAULT_PATH && fs.existsSync(process.env.VAULT_PATH)) {
  VAULT_PATH = process.env.VAULT_PATH;
} else if (fs.existsSync(path.join(__dirname, '../AI_Employee_Vault'))) {
  // Dashboard is in dashboard/, vault is in ../AI_Employee_Vault
  VAULT_PATH = path.join(__dirname, '../AI_Employee_Vault');
} else if (fs.existsSync(path.join(__dirname, '../../AI_Employee_Vault'))) {
  // Dashboard might be in dashboard/public/
  VAULT_PATH = path.join(__dirname, '../../AI_Employee_Vault');
} else if (fs.existsSync(path.join(process.cwd(), 'AI_Employee_Vault'))) {
  // Running from project root
  VAULT_PATH = path.join(process.cwd(), 'AI_Employee_Vault');
} else {
  // Fallback to parent directory of dashboard
  VAULT_PATH = path.join(__dirname, '..', 'AI_Employee_Vault');
}

console.log('[Dashboard] Vault path:', VAULT_PATH);

app.use(express.static(path.join(__dirname, 'public'), {
  maxAge: 0,
  etag: false
}));
app.use(express.json());

// Cache PM2 data to reduce shell command frequency
let pm2Cache = {
  processes: null,
  lastUpdate: 0,
  cacheDuration: 5000 // 5 seconds cache
};

// Helper: Execute PM2 command silently on Windows
async function pm2List() {
  const now = Date.now();
  if (pm2Cache.processes && now - pm2Cache.lastUpdate < pm2Cache.cacheDuration) {
    return pm2Cache.processes;
  }

  return new Promise((resolve, reject) => {
    // Use full path to PM2 to avoid PATH issues
    let command, args, useShell;
    if (process.platform === 'win32') {
      // Windows: .cmd files require shell
      command = path.join(process.env.USERPROFILE || 'C:\\Users\\User', 'AppData', 'Roaming', 'npm', 'pm2.cmd');
      args = ['jlist'];
      useShell = true;
    } else {
      command = 'pm2';
      args = ['jlist'];
      useShell = false;
    }

    const child = spawn(command, args, {
      windowsHide: true,
      shell: useShell
    });

    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    child.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    child.on('close', (code) => {
      if (code !== 0) {
        return reject(new Error(stderr));
      }
      try {
        const processes = JSON.parse(stdout);
        pm2Cache.processes = processes;
        pm2Cache.lastUpdate = now;
        resolve(processes);
      } catch (e) {
        reject(e);
      }
    });
  });
}

// Helper to get logs (read from PM2 log files)
async function pm2Logs(name, lines) {
  return new Promise((resolve, reject) => {
    // Try to get PM2 home directory, or use defaults
    const getPM2Path = () => {
      // Windows default
      if (process.platform === 'win32') {
        const userProfile = process.env.USERPROFILE || 'C:\\Users\\User';
        return path.join(userProfile, '.pm2');
      }
      // Unix/Mac default
      return path.join(process.env.HOME || process.env.USERPROFILE || '~', '.pm2');
    };

    const pm2Root = getPM2Path();
    const logsPath = path.join(pm2Root, 'logs');

    // Find log files for the process
    const outFile = path.join(logsPath, `${name}-out.log`);
    const errFile = path.join(logsPath, `${name}-error.log`);

    try {
      const outLogs = readLastLines(outFile, lines);
      const errLogs = readLastLines(errFile, lines);

      resolve({
        out: outLogs.map(line => ({
          message: line,
          timestamp: Date.now(),
          level: 'info'
        })),
        err: errLogs.map(line => ({
          message: line,
          timestamp: Date.now(),
          level: 'error'
        }))
      });
    } catch (e) {
      console.error(`Error reading logs for ${name}:`, e.message);
      resolve({ out: [], err: [] });
    }
  });
}

// Helper to read last N lines from a file
function readLastLines(filePath, lines) {
  try {
    if (!fs.existsSync(filePath)) {
      return [];
    }

    const content = fs.readFileSync(filePath, 'utf-8');
    const allLines = content.split('\n').filter(line => line.trim());

    // Return last N lines
    return allLines.slice(-lines);
  } catch (e) {
    return [];
  }
}

// API: Get logs for a process
app.get('/api/logs/:name', async (req, res) => {
  try {
    const lines = parseInt(req.query.lines) || 50;
    const logs = await pm2Logs(req.params.name, lines);

    // Debug logging
    console.log(`[Logs] Fetching logs for ${req.params.name}:`,
                `${logs.out.length} out, ${logs.err.length} err`);

    res.json(logs);
  } catch (err) {
    console.error('[Logs] Error:', err.message);
    res.status(500).json({ error: err.message, out: [], err: [] });
  }
});

// API: Get vault status
app.get('/api/vault', (req, res) => {
  const status = {
    pending: fs.readdirSync(path.join(VAULT_PATH, 'Pending_Approval')).filter(f => f.endsWith('.md')).length,
    approved: fs.readdirSync(path.join(VAULT_PATH, 'Approved')).filter(f => f.endsWith('.md')).length,
    done: fs.readdirSync(path.join(VAULT_PATH, 'Done')).filter(f => f.endsWith('.md')).length,
    needsAction: fs.readdirSync(path.join(VAULT_PATH, 'Needs_Action')).filter(f => f.endsWith('.md')).length,
  };

  res.json(status);
});

// API: Get pending approval items
app.get('/api/vault/pending', (req, res) => {
  const pendingPath = path.join(VAULT_PATH, 'Pending_Approval');

  try {
    const files = fs.readdirSync(pendingPath).filter(f => f.endsWith('.md'));
    const items = files.map(filename => {
      const filepath = path.join(pendingPath, filename);
      const content = fs.readFileSync(filepath, 'utf-8');

      // Extract type from filename or content
      let type = 'unknown';
      if (filename.startsWith('LINKEDIN_POST_')) type = 'linkedin_post';
      else if (filename.startsWith('TWITTER_POST_')) type = 'twitter_post';
      else if (filename.startsWith('INSTAGRAM_POST_')) type = 'instagram_post';
      else if (filename.startsWith('FACEBOOK_POST_')) type = 'facebook_post';
      else if (filename.startsWith('EMAIL_')) type = 'email';
      else if (filename.startsWith('SLACK_')) type = 'slack_message';
      else if (filename.startsWith('WHATSAPP_')) type = 'whatsapp_message';
      else if (filename.startsWith('XERO_')) type = 'xero_alert';
      else if (filename.startsWith('CALENDAR_')) type = 'calendar_event';

      // Extract preview from content (first 200 chars)
      const lines = content.split('\n');
      let preview = '';
      let inContent = false;
      for (const line of lines) {
        if (line.startsWith('---')) {
          if (inContent) break;
          continue;
        }
        inContent = true;
        if (line.trim() && !line.startsWith('#')) {
          preview += line + ' ';
          if (preview.length > 150) break;
        }
      }

      return {
        filename,
        type,
        preview: preview.trim().substring(0, 150) + '...',
        created: fs.statSync(filepath).mtime
      };
    });

    res.json(items);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: Get logs
app.get('/api/vault/logs', (req, res) => {
  const logsPath = path.join(VAULT_PATH, 'Logs');

  try {
    if (!fs.existsSync(logsPath)) {
      return res.json([]);
    }

    // Get all log files and sort by date (newest first)
    const logFiles = fs.readdirSync(logsPath)
      .filter(f => f.endsWith('.json'))
      .sort()
      .reverse();

    if (logFiles.length === 0) {
      return res.json([]);
    }

    // Read the most recent log file
    const logFile = path.join(logsPath, logFiles[0]);
    const content = fs.readFileSync(logFile, 'utf-8');
    const logs = content.split('\n')
      .filter(line => line.trim())
      .map(line => {
        try {
          return JSON.parse(line);
        } catch {
          return null;
        }
      })
      .filter(log => log);

    res.json(logs.slice(-50)); // Last 50 log entries
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: Get full content of a pending item
app.get('/api/vault/pending/:filename', (req, res) => {
  const filename = req.params.filename;

  try {
    const filePath = path.join(VAULT_PATH, 'Pending_Approval', filename);

    if (!fs.existsSync(filePath)) {
      return res.status(404).json({ error: 'File not found' });
    }

    const content = fs.readFileSync(filePath, 'utf-8');
    res.json({ filename, content });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: Approve item
app.post('/api/vault/approve/:filename', (req, res) => {
  const filename = req.params.filename;

  try {
    const srcPath = path.join(VAULT_PATH, 'Pending_Approval', filename);
    const dstPath = path.join(VAULT_PATH, 'Approved', filename);

    if (!fs.existsSync(srcPath)) {
      return res.status(404).json({ error: 'File not found' });
    }

    fs.renameSync(srcPath, dstPath);
    res.json({ success: true, message: `Approved ${filename}` });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: Reject item
app.post('/api/vault/reject/:filename', (req, res) => {
  const filename = req.params.filename;

  try {
    const srcPath = path.join(VAULT_PATH, 'Pending_Approval', filename);
    const dstPath = path.join(VAULT_PATH, 'Rejected', filename);

    // Ensure Rejected folder exists
    const rejectedPath = path.join(VAULT_PATH, 'Rejected');
    if (!fs.existsSync(rejectedPath)) {
      fs.mkdirSync(rejectedPath, { recursive: true });
    }

    if (!fs.existsSync(srcPath)) {
      return res.status(404).json({ error: 'File not found' });
    }

    fs.renameSync(srcPath, dstPath);
    res.json({ success: true, message: `Rejected ${filename}` });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: Restart process
app.post('/api/processes/:name/restart', async (req, res) => {
  try {
    await execAsync(`pm2 restart ${req.params.name}`, { windowsHide: true });
    pm2Cache.processes = null; // Clear cache
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: Stop process
app.post('/api/processes/:name/stop', async (req, res) => {
  try {
    await execAsync(`pm2 stop ${req.params.name}`, { windowsHide: true });
    pm2Cache.processes = null; // Clear cache
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: Start process
app.post('/api/processes/:name/start', async (req, res) => {
  try {
    await execAsync(`pm2 start ${req.params.name}`, { windowsHide: true });
    pm2Cache.processes = null; // Clear cache
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: Start all processes
app.post('/api/processes/start-all', async (req, res) => {
  try {
    await execAsync(`pm2 start all`, { windowsHide: true });
    pm2Cache.processes = null;
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: Stop all processes
app.post('/api/processes/stop-all', async (req, res) => {
  try {
    await execAsync(`pm2 stop all`, { windowsHide: true });
    pm2Cache.processes = null;
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: Restart all processes
app.post('/api/processes/restart-all', async (req, res) => {
  try {
    await execAsync(`pm2 restart all`, { windowsHide: true });
    pm2Cache.processes = null;
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: Get logs for a process (with filtering)
app.get('/api/logs/:name/filter', async (req, res) => {
  try {
    const { level, search, lines = 100 } = req.query;
    let logs = await pm2Logs(req.params.name, parseInt(lines));

    // Filter by log level if provided
    if (level) {
      logs = {
        out: logs.out.filter(log =>
          log.level === level || log.message.includes(`[${level.toUpperCase()}]`)
        ),
        err: logs.err.filter(log =>
          log.level === level || log.message.includes(`[${level.toUpperCase()}]`)
        )
      };
    }

    // Filter by search term if provided
    if (search) {
      const searchLower = search.toLowerCase();
      logs = {
        out: logs.out.filter(log => log.message.toLowerCase().includes(searchLower)),
        err: logs.err.filter(log => log.message.toLowerCase().includes(searchLower))
      };
    }

    res.json(logs);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: Get all vault logs with pagination and filtering
app.get('/api/vault/logs/all', (req, res) => {
  const { limit = 100, offset = 0, type, result } = req.query;
  const logsPath = path.join(VAULT_PATH, 'Logs');

  try {
    if (!fs.existsSync(logsPath)) {
      return res.json({ logs: [], total: 0 });
    }

    const logFiles = fs.readdirSync(logsPath)
      .filter(f => f.endsWith('.json'))
      .sort()
      .reverse();

    let allLogs = [];
    for (const logFile of logFiles) {
      const filePath = path.join(logsPath, logFile);
      const content = fs.readFileSync(filePath, 'utf-8');
      const logs = content.split('\n')
        .filter(line => line.trim())
        .map(line => {
          try {
            return JSON.parse(line);
          } catch {
            return null;
          }
        })
        .filter(log => log);

      allLogs = allLogs.concat(logs);
    }

    // Filter by type if provided
    let filteredLogs = allLogs;
    if (type) {
      filteredLogs = filteredLogs.filter(log => log.action_type === type);
    }

    // Filter by result if provided
    if (result) {
      filteredLogs = filteredLogs.filter(log => log.result === result);
    }

    // Sort by timestamp (newest first)
    filteredLogs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    const total = filteredLogs.length;
    const paginatedLogs = filteredLogs.slice(parseInt(offset), parseInt(offset) + parseInt(limit));

    res.json({ logs: paginatedLogs, total });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: Get analytics data
app.get('/api/analytics', (req, res) => {
  const range = req.query.range || '24h';
  const logsPath = path.join(VAULT_PATH, 'Logs');

  try {
    if (!fs.existsSync(logsPath)) {
      return res.json({
        actionsByType: {},
        actionsByHour: Array(24).fill(0),
        dailyTrends: [],
        successRate: 100,
        totalActions: 0,
        errorCount: 0
      });
    }

    // Determine how many days of logs to read
    let daysToRead = 1;
    if (range === '7d') daysToRead = 7;
    else if (range === '30d') daysToRead = 30;

    const logFiles = fs.readdirSync(logsPath)
      .filter(f => f.endsWith('.json'))
      .sort()
      .slice(-daysToRead); // Last N days

    let allLogs = [];
    for (const logFile of logFiles) {
      const filePath = path.join(logsPath, logFile);
      const content = fs.readFileSync(filePath, 'utf-8');
      const logs = content.split('\n')
        .filter(line => line.trim())
        .map(line => {
          try {
            return JSON.parse(line);
          } catch {
            return null;
          }
        })
        .filter(log => log);

      allLogs = allLogs.concat(logs);
    }

    // Actions by type
    const actionsByType = {};
    allLogs.forEach(log => {
      const type = log.action_type || 'undefined';
      actionsByType[type] = (actionsByType[type] || 0) + 1;
    });

    // Actions by hour (last 24 hours)
    const actionsByHour = Array(24).fill(0);
    const now = Date.now();
    allLogs.forEach(log => {
      const logTime = new Date(log.timestamp).getTime();
      const hoursAgo = Math.floor((now - logTime) / (1000 * 60 * 60));
      if (hoursAgo < 24) {
        actionsByHour[23 - hoursAgo]++;
      }
    });

    // Daily trends
    const dailyTrends = [];
    const dailyCounts = {};

    allLogs.forEach(log => {
      const date = new Date(log.timestamp).toISOString().split('T')[0];
      dailyCounts[date] = (dailyCounts[date] || 0) + 1;
    });

    // Fill in missing dates
    for (let i = daysToRead - 1; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      dailyTrends.push({
        date: dateStr,
        count: dailyCounts[dateStr] || 0
      });
    }

    // Success rate - count actual results
    const successCount = allLogs.filter(log => log.result === 'success').length;
    const errorCount = allLogs.filter(log => log.result === 'error').length;
    const totalActions = allLogs.length;

    // For logs without a result field, count as success (they're informational)
    const noResultCount = allLogs.filter(log => !log.result).length;
    const effectiveSuccess = successCount + noResultCount;
    const successRate = totalActions > 0 ? (effectiveSuccess / totalActions * 100).toFixed(1) : 100;

    res.json({
      actionsByType,
      actionsByHour,
      dailyTrends,
      successRate,
      totalActions,
      errorCount
    });
  } catch (err) {
    console.error('[Analytics] Error:', err.message);
    res.status(500).json({
      actionsByType: {},
      actionsByHour: Array(24).fill(0),
      dailyTrends: [],
      successRate: 100,
      totalActions: 0,
      errorCount: 0,
      error: err.message
    });
  }
});

// API: Get system health
app.get('/api/health', async (req, res) => {
  try {
    const processes = await pm2List();

    // Calculate totals
    const online = processes.filter(p => p.pm2_env.status === 'online').length;
    const stopped = processes.filter(p => p.pm2_env.status === 'stopped').length;
    const errored = processes.filter(p => p.pm2_env.restart_time > 0).length;
    const totalCpu = processes.reduce((sum, p) => sum + (p.monit?.cpu || 0), 0);
    const totalMemory = processes.reduce((sum, p) => sum + (p.monit?.memory || 0), 0);

    const health = {
      timestamp: Date.now(),
      online,
      stopped,
      errored,
      totalCpu: totalCpu.toFixed(1),
      totalMemory: (totalMemory / 1024 / 1024).toFixed(0),
      processes: processes.length
    };

    // Add to history
    healthHistory.push(health);
    if (healthHistory.length > MAX_HEALTH_HISTORY) {
      healthHistory.shift();
    }

    res.json({
      current: health,
      history: healthHistory
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: Get vault folders
app.get('/api/vault/folders', (req, res) => {
  try {
    const folders = ['Pending_Approval', 'Approved', 'Done', 'Needs_Action', 'Plans', 'Briefings', 'Logs', 'Rejected', 'Temp', 'Accounting'];
    const folderContents = {};

    folders.forEach(folder => {
      const folderPath = path.join(VAULT_PATH, folder);
      if (fs.existsSync(folderPath)) {
        const files = fs.readdirSync(folderPath).filter(f => f.endsWith('.md') || f.endsWith('.json'));
        folderContents[folder] = {
          count: files.length,
          files: files.slice(0, 20) // First 20 files
        };
      } else {
        folderContents[folder] = { count: 0, files: [] };
      }
    });

    res.json(folderContents);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: Get specific folder contents
app.get('/api/vault/folder/:folderName', (req, res) => {
  try {
    const folderName = req.params.folderName;

    // Security check - only allow known folder names
    const allowedFolders = ['Pending_Approval', 'Approved', 'Done', 'Needs_Action', 'Plans', 'Briefings', 'Logs', 'Rejected', 'Temp', 'Accounting', 'Inbox'];
    if (!allowedFolders.includes(folderName)) {
      return res.status(400).json({ error: 'Invalid folder name' });
    }

    const folderPath = path.join(VAULT_PATH, folderName);

    if (!fs.existsSync(folderPath)) {
      return res.json({ files: [] });
    }

    const files = fs.readdirSync(folderPath)
      .filter(f => f.endsWith('.md') || f.endsWith('.json'))
      .sort()
      .reverse(); // Most recent first

    res.json({ files: files });
  } catch (err) {
    console.error('[Folder] Error:', err.message);
    res.status(500).json({ error: err.message, files: [] });
  }
});

// API: Get file content
app.get('/api/vault/file/:folder/:filename', (req, res) => {
  try {
    const { folder, filename } = req.params;
    const filePath = path.join(VAULT_PATH, folder, filename);

    if (!fs.existsSync(filePath)) {
      return res.status(404).json({ error: 'File not found' });
    }

    const content = fs.readFileSync(filePath, 'utf-8');
    res.json({ content });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: Bulk approve
app.post('/api/vault/approve-bulk', (req, res) => {
  try {
    const { filenames } = req.body;
    const results = [];

    for (const filename of filenames) {
      const srcPath = path.join(VAULT_PATH, 'Pending_Approval', filename);
      const dstPath = path.join(VAULT_PATH, 'Approved', filename);

      if (fs.existsSync(srcPath)) {
        fs.renameSync(srcPath, dstPath);
        results.push({ filename, success: true });
      } else {
        results.push({ filename, success: false, error: 'File not found' });
      }
    }

    res.json({ results });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: Bulk reject
app.post('/api/vault/reject-bulk', (req, res) => {
  try {
    const { filenames } = req.body;
    const results = [];

    // Ensure Rejected folder exists
    const rejectedPath = path.join(VAULT_PATH, 'Rejected');
    if (!fs.existsSync(rejectedPath)) {
      fs.mkdirSync(rejectedPath, { recursive: true });
    }

    for (const filename of filenames) {
      const srcPath = path.join(VAULT_PATH, 'Pending_Approval', filename);
      const dstPath = path.join(VAULT_PATH, 'Rejected', filename);

      if (fs.existsSync(srcPath)) {
        fs.renameSync(srcPath, dstPath);
        results.push({ filename, success: true });
      } else {
        results.push({ filename, success: false, error: 'File not found' });
      }
    }

    res.json({ results });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ==================== SIMPLE PROCESS TRACKER (JSON-based) ====================

async function getRunningProcessesJSON() {
  return new Promise((resolve) => {
    fs.readFile(path.join(VAULT_PATH, '.running_processes.json'), (err, data) => {
      if (err) {
        resolve([]);
      } else {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          resolve([]);
        }
      }
    });
  });
}

// API: Update processes (called by process_tracker.py)
app.post('/api/processes/update', async (req, res) => {
  try {
    const { processes } = req.body;

    // Save to JSON file
    fs.writeFileSync(
      path.join(VAULT_PATH, '.running_processes.json'),
      JSON.stringify(processes, null, 2)
    );

    res.json({ success: true });
  } catch (err) {
    console.error('[Processes Update] Error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// ==================== PROCESS DETECTION (Alternative to PM2) ====================

const DETECTED_PROCESSES = [
  {name: 'gmail-watcher', module: 'watchers.gmail_watcher'},
  {name: 'calendar-watcher', module: 'watchers.calendar_watcher'},
  {name: 'slack-watcher', module: 'watchers.slack_watcher'},
  {name: 'odoo-watcher', module: 'watchers.odoo_watcher'},
  {name: 'filesystem-watcher', module: 'watchers.filesystem_watcher'},
  {name: 'whatsapp-watcher', module: 'watchers.whatsapp_watcher'},
  {name: 'email-approval-monitor', file: 'scripts/monitors/email_approval_monitor.py'},
  {name: 'calendar-approval-monitor', file: 'scripts/monitors/calendar_approval_monitor.py'},
  {name: 'slack-approval-monitor', file: 'scripts/monitors/slack_approval_monitor.py'},
  {name: 'linkedin-approval-monitor', file: 'scripts/social-media/linkedin_approval_monitor.py'},
  {name: 'twitter-approval-monitor', file: 'scripts/social-media/twitter_approval_monitor.py'},
  {name: 'facebook-approval-monitor', file: 'scripts/social-media/facebook-approval-monitor.py'},
  {name: 'instagram-approval-monitor', file: 'scripts/social-media/instagram-approval-monitor.py'}
];

let processCache = { data: [], timestamp: 0 };
const PROCESS_CACHE_DURATION = 10000; // 10 seconds

async function getDetectedProcesses() {
  const now = Date.now();
  if (processCache.data && now - processCache.timestamp < PROCESS_CACHE_DURATION) {
    return processCache.data;
  }

  return new Promise((resolve) => {
    // Use tasklist to find Python processes
    const child = spawn('tasklist', ['/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'], {
      windowsHide: true,
      shell: false  // Fixed deprecation warning - no shell needed for array args
    });

    let stdout = '';
    child.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    child.on('close', (code) => {
      if (code !== 0) {
        processCache = { data: [], timestamp: now };
        return resolve([]);
      }

      try {
        const lines = stdout.trim().split('\n');
        const processes = [];

        // Skip header
        for (let i = 1; i < lines.length; i++) {
          const line = lines[i];
          if (!line) continue;

          const parts = line.split(',');
          if (parts.length < 6) continue;

          const pid = parts[1].trim();
          const cmdline = parts.slice(5).join(',').trim();

          // Check if it matches our known processes
          for (const proc of DETECTED_PROCESSES) {
            const match = proc.module
              ? `python.exe -m ${proc.module}`
              : proc.file.replace(/\//g, '\\');

            if (cmdline.includes(match) || cmdline.includes(proc.name.replace(/-/g, '_'))) {
              // Parse memory (column 4)
              const memStr = parts[4].trim().replace(/,/g, '');
              const memory = parseInt(memStr) || 0;

              processes.push({
                name: proc.name,
                status: 'online',
                cpu: 0, // tasklist doesn't provide CPU
                memory: memory / 1024, // Convert KB to MB
                uptime: new Date().toISOString(), // tasklist doesn't provide uptime
                restarts: 0,
                pm2_env: { status: 'online', pm_uptime: new Date().toISOString() },
                monit: { cpu: 0, memory: memory * 1024 },
                pid: parseInt(pid)
              });
              break;
            }
          }
        }

        processCache = { data: processes, timestamp: now };
        resolve(processes);
      } catch (err) {
        console.error('[Process Detection] Error:', err.message);
        processCache = { data: [], timestamp: now };
        resolve([]);
      }
    });
  });
}

// API: Get watcher-specific status (with direct process detection)
app.get('/api/watchers/status', async (req, res) => {
  try {
    // Try PM2 first
    let watchers = [];

    try {
      const pm2Processes = await pm2List();
      watchers = pm2Processes.filter(p =>
        p.name.includes('watcher') ||
        p.name.includes('monitor')
      );
    } catch (e) {
      console.log('[Watchers] PM2 not available, using direct detection');
    }

    // If PM2 has no watchers, use direct process detection
    if (watchers.length === 0) {
      const detected = await getDetectedProcesses();
      watchers = detected.filter(p =>
        p.name.includes('watcher') ||
        p.name.includes('monitor')
      );
    }

    const watcherStatus = watchers.map(w => ({
      name: w.name,
      status: w.pm2_env?.status || w.status,
      cpu: w.monit?.cpu || w.cpu || 0,
      memory: (w.monit?.memory || w.memory * 1024 || 0) / 1024,
      uptime: w.pm2_env?.pm_uptime || w.uptime,
      restarts: w.pm2_env?.restart_time || w.restarts || 0,
      lastError: w.pm2_env?.axm_options?.km?.error || w.lastError || null
    }));

    res.json(watcherStatus);
  } catch (err) {
    console.error('[Watchers Status] Error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// API: Get all processes (with direct process detection fallback)
app.get('/api/processes', async (req, res) => {
  try {
    // Try PM2 first
    let processes = [];

    try {
      processes = await pm2List();
    } catch (e) {
      console.log('[Processes] PM2 not available, using direct detection');
    }

    // If PM2 has no processes, use direct process detection
    if (processes.length === 0) {
      processes = await getDetectedProcesses();
    }

    res.json(processes);
  } catch (err) {
    console.error('[Processes] Error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// ==================== TASKS API (Data Persistence) ====================

const TASKS_FILE = path.join(__dirname, 'tasks.json');

// Helper to load tasks
function loadTasksFromFile() {
  try {
    if (fs.existsSync(TASKS_FILE)) {
      const data = fs.readFileSync(TASKS_FILE, 'utf-8');
      return JSON.parse(data);
    }
  } catch (err) {
    console.error('Error loading tasks:', err.message);
  }
  // Return default tasks if file doesn't exist
  return [
    { id: 1, title: 'Review pending emails', description: 'Check and process pending approval requests', status: 'todo', priority: 'high', tags: ['email', 'urgent'], created: new Date().toISOString() },
    { id: 2, title: 'Generate weekly briefing', description: 'Create CEO briefing from vault data', status: 'todo', priority: 'medium', tags: ['reporting'], created: new Date().toISOString() },
    { id: 3, title: 'Update social media queue', description: 'Review and schedule pending posts', status: 'progress', priority: 'low', tags: ['social'], created: new Date().toISOString() },
    { id: 4, title: 'Fix calendar watcher', description: 'Debug authentication issues', status: 'done', priority: 'high', tags: ['bug', 'technical'], created: new Date().toISOString() },
    { id: 5, title: 'Set up Xero integration', description: 'Configure MCP server for accounting', status: 'todo', priority: 'medium', tags: ['integration'], created: new Date().toISOString() }
  ];
}

// Helper to save tasks
function saveTasksToFile(tasks) {
  try {
    fs.writeFileSync(TASKS_FILE, JSON.stringify(tasks, null, 2));
    return true;
  } catch (err) {
    console.error('Error saving tasks:', err.message);
    return false;
  }
}

// GET /api/tasks - Get all tasks
app.get('/api/tasks', (req, res) => {
  const tasks = loadTasksFromFile();
  res.json(tasks);
});

// POST /api/tasks - Save tasks (create/update)
app.post('/api/tasks', (req, res) => {
  try {
    const tasks = req.body;
    if (saveTasksToFile(tasks)) {
      res.json({ success: true, count: tasks.length });
    } else {
      res.status(500).json({ error: 'Failed to save tasks' });
    }
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// PUT /api/tasks/:id - Update single task
app.put('/api/tasks/:id', (req, res) => {
  try {
    const taskId = parseInt(req.params.id);
    const updates = req.body;

    let tasks = loadTasksFromFile();
    const taskIndex = tasks.findIndex(t => t.id === taskId);

    if (taskIndex === -1) {
      return res.status(404).json({ error: 'Task not found' });
    }

    tasks[taskIndex] = { ...tasks[taskIndex], ...updates };

    if (saveTasksToFile(tasks)) {
      res.json(tasks[taskIndex]);
    } else {
      res.status(500).json({ error: 'Failed to save tasks' });
    }
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// DELETE /api/tasks/:id - Delete task
app.delete('/api/tasks/:id', (req, res) => {
  try {
    const taskId = parseInt(req.params.id);
    let tasks = loadTasksFromFile();

    const initialLength = tasks.length;
    tasks = tasks.filter(t => t.id !== taskId);

    if (tasks.length === initialLength) {
      return res.status(404).json({ error: 'Task not found' });
    }

    if (saveTasksToFile(tasks)) {
      res.json({ success: true, remaining: tasks.length });
    } else {
      res.status(500).json({ error: 'Failed to save tasks' });
    }
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   🤖 AI EMPLOYEE DASHBOARD                              ║
║                                                          ║
║   Access: http://localhost:${PORT}                        ║
║                                                          ║
║   Features:                                              ║
║   • Real-time process monitoring                         ║
║   • Live logs viewer                                     ║
║   • Vault status (Pending/Approved/Done)                 ║
║   • Process control (restart/stop)                       ║
║                                                          ║
║   Press Ctrl+C to stop                                   ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    `);
});
