// AI Employee Dashboard v2.0 - Enhanced App

// Type icons for badges
const typeIcons = {
  linkedin_post: 'fab fa-linkedin',
  twitter_post: 'fab fa-twitter',
  instagram_post: 'fab fa-instagram',
  facebook_post: 'fab fa-facebook',
  email: 'fas fa-envelope',
  slack_message: 'fab fa-slack',
  whatsapp_message: 'fab fa-whatsapp',
  xero_alert: 'fas fa-file-invoice-dollar',
  calendar_event: 'fas fa-calendar',
  unknown: 'fas fa-file'
};

// Charts
let healthChart = null;
let actionsChart = null;
let hourlyChart = null;

// Current section
let currentSection = 'dashboard';

// Performance optimization: Cache DOM queries
const domCache = {};

function getCachedElement(id) {
  if (!domCache[id]) {
    domCache[id] = document.getElementById(id);
  }
  return domCache[id];
}

// Performance: Debounce function
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Performance: Throttle function
function throttle(func, limit) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// Section titles
const sectionTitles = {
  dashboard: '<i class="fas fa-tachometer-alt"></i> Dashboard',
  processes: '<i class="fas fa-server"></i> All Processes',
  watchers: '<i class="fas fa-eye"></i> Watchers & Monitors',
  pending: '<i class="fas fa-clock"></i> Pending Approvals',
  logs: '<i class="fas fa-file-alt"></i> System Logs',
  analytics: '<i class="fas fa-chart-line"></i> Analytics',
  files: '<i class="fas fa-folder"></i> Vault Files',
  activity: '<i class="fas fa-history"></i> Recent Activity',
  'quick-actions': '<i class="fas fa-bolt"></i> Quick Actions',
  'goals': '<i class="fas fa-bullseye"></i> Business Goals',
  'events': '<i class="fas fa-calendar-alt"></i> Upcoming Events',
  'social-queue': '<i class="fas fa-share-alt"></i> Social Media Queue',
  'search': '<i class="fas fa-search"></i> Advanced Search',
  'resources': '<i class="fas fa-microchip"></i> Resource Monitor',
  'tasks': '<i class="fas fa-tasks"></i> Task Management',
  'settings': '<i class="fas fa-cog"></i> Settings',
  'ai-chat': '<i class="fas fa-robot"></i> AI Chat',
  'calendar': '<i class="fas fa-calendar"></i> Calendar View'
};

// Navigation
document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', () => {
    const section = item.dataset.section;
    showSection(section);
  });
});

function showSection(section) {
  // Update nav items
  document.querySelectorAll('.nav-item').forEach(nav => {
    nav.classList.remove('active');
    if (nav.dataset.section === section) {
      nav.classList.add('active');
    }
  });

  // Update sections
  document.querySelectorAll('.content-section').forEach(sec => {
    sec.classList.remove('active');
  });
  document.getElementById(`section-${section}`).classList.add('active');

  // Update title
  document.getElementById('pageTitle').innerHTML = sectionTitles[section];
  currentSection = section;

  // Clear auto-refresh when leaving sections
  if (section !== 'logs' && logsAutoRefreshInterval) {
    clearInterval(logsAutoRefreshInterval);
    logsAutoRefreshInterval = null;
  }
  if (section !== 'activity' && activityAutoRefreshInterval) {
    clearInterval(activityAutoRefreshInterval);
    activityAutoRefreshInterval = null;
    document.getElementById('autoRefreshActivity').checked = false;
  }

  // Load section data
  switch(section) {
    case 'dashboard': loadDashboard(); break;
    case 'processes': loadAllProcesses(); break;
    case 'watchers': loadAllProcesses(); break;  // Redirect to combined processes section
    case 'pending': loadPending(); break;
    case 'logs':
      populateProcessSelector();
      loadLogs();
      break;
    case 'analytics': loadAnalytics(); loadErrors(); break;
    case 'files': loadFolders(); break;
    case 'activity': loadActivity(); break;
    case 'quick-actions': /* No load needed */ break;
    case 'goals': loadGoals(); break;
    case 'events': loadUpcomingEvents(); break;
    case 'social-queue': loadSocialQueue(); break;
    case 'search': /* No auto-load */ break;
    case 'resources': loadResources(); break;
    case 'tasks': loadKanbanTasks(); break;
    case 'settings': loadSettings(); break;
    case 'ai-chat': /* No auto-load */ break;
    case 'calendar': loadCalendar(); break;
  }
}

// Toast notifications
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;

  const icons = {
    success: 'fa-check-circle',
    error: 'fa-times-circle',
    info: 'fa-info-circle',
    warning: 'fa-exclamation-triangle'
  };

  toast.innerHTML = `<i class="fas ${icons[type]}"></i><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 3000);
}

// Modal functions
function openModal(title, content) {
  document.getElementById('modalTitle').textContent = title;
  document.getElementById('modalContent').innerHTML = content;
  document.getElementById('modalOverlay').classList.add('active');
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('active');
}

// Dashboard Section
async function loadDashboard() {
  try {
    const res = await fetch('/api/health');
    const data = await res.json();

    // Update health grid
    const healthGrid = document.getElementById('healthGrid');
    healthGrid.innerHTML = `
      <div class="health-card success">
        <div class="icon"><i class="fas fa-check-circle"></i></div>
        <div class="label">Online Processes</div>
        <div class="value">${data.current.online}</div>
      </div>
      <div class="health-card ${data.current.stopped > 0 ? 'warning' : 'success'}">
        <div class="icon"><i class="fas fa-power-off"></i></div>
        <div class="label">Stopped Processes</div>
        <div class="value">${data.current.stopped}</div>
      </div>
      <div class="health-card info">
        <div class="icon"><i class="fas fa-microchip"></i></div>
        <div class="label">Total CPU</div>
        <div class="value">${data.current.totalCpu}%</div>
      </div>
      <div class="health-card info">
        <div class="icon"><i class="fas fa-memory"></i></div>
        <div class="label">Total Memory</div>
        <div class="value">${data.current.totalMemory}MB</div>
      </div>
    `;

    // Update health chart
    updateHealthChart(data.history);
  } catch (err) {
    console.error('Error loading dashboard:', err);
  }
}

function updateHealthChart(history) {
  const ctx = document.getElementById('healthChart').getContext('2d');

  if (healthChart) {
    healthChart.destroy();
  }

  const labels = history.map(h => {
    const date = new Date(h.timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  });

  healthChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'CPU %',
          data: history.map(h => h.totalCpu),
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          fill: true,
          tension: 0.4
        },
        {
          label: 'Memory (MB)',
          data: history.map(h => h.totalMemory),
          borderColor: '#8b5cf6',
          backgroundColor: 'rgba(139, 92, 246, 0.1)',
          fill: true,
          tension: 0.4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: '#94a3b8' }
        }
      },
      scales: {
        x: {
          ticks: { color: '#64748b' },
          grid: { color: '#334155' }
        },
        y: {
          ticks: { color: '#64748b' },
          grid: { color: '#334155' }
        }
      }
    }
  });
}

// Processes Section
async function loadAllProcesses() {
  try {
    const res = await fetch('/api/processes');
    const processes = await res.json();

    const container = document.getElementById('allProcesses');
    container.innerHTML = processes.map(p => createProcessCard(p)).join('');

    // Update count badge
    document.getElementById('allProcessesCount').textContent = processes.length;
  } catch (err) {
    console.error('Error loading processes:', err);
  }
}

// Watchers Tab
async function loadWatchers() {
  try {
    const res = await fetch('/api/watchers/status');
    const watchers = await res.json();

    const container = document.getElementById('watchersList');
    if (watchers.length === 0) {
      container.innerHTML = '<div class="empty-state"><i class="fas fa-eye-slash"></i><p>No watchers found</p></div>';
      document.getElementById('watchersCount').textContent = '0';
      return;
    }

    container.innerHTML = watchers.map(w => createWatcherCard(w)).join('');
    document.getElementById('watchersCount').textContent = watchers.length;
  } catch (err) {
    console.error('Error loading watchers:', err);
  }
}

// Tab switching
function switchProcessTab(tab) {
  // Update tab styles
  document.querySelectorAll('.tabs .tab').forEach(t => t.classList.remove('active'));
  event.target.classList.add('active');

  // Show/hide content
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  if (tab === 'all') {
    document.getElementById('allProcessesTab').classList.add('active');
    loadAllProcesses();
  } else if (tab === 'watchers') {
    document.getElementById('watchersTab').classList.add('active');
    loadWatchers();
  }
}

function createProcessCard(p) {
  const uptime = p.pm2_env.pm_uptime
    ? `${Math.floor((Date.now() - p.pm2_env.pm_uptime) / 1000 / 60)}m`
    : 'N/A';

  return `
    <div class="process-card">
      <div class="process-header">
        <div class="process-name">
          ${p.name}
          ${p.pm2_env.status === 'online' ? '<div class="process-dot"></div>' : '<div class="process-dot offline"></div>'}
        </div>
        <span class="process-status ${p.pm2_env.status}">${p.pm2_env.status.toUpperCase()}</span>
      </div>
      <div class="process-info">CPU: ${p.monit?.cpu || 0}% | Memory: ${((p.monit?.memory || 0) / 1024 / 1024).toFixed(0)}MB</div>
      <div class="process-info">Restarts: ${p.pm2_env.restart_time || 0} | Uptime: ${uptime}</div>
      <div class="process-actions">
        <button class="btn btn-sm btn-success" onclick="startProcess('${p.name}')">
          <i class="fas fa-play"></i>
        </button>
        <button class="btn btn-sm btn-secondary" onclick="restartProcess('${p.name}')">
          <i class="fas fa-redo"></i>
        </button>
        <button class="btn btn-sm btn-danger" onclick="stopProcess('${p.name}')">
          <i class="fas fa-stop"></i>
        </button>
      </div>
    </div>
  `;
}

function createWatcherCard(w) {
  // Handle both PM2 process format and simple watcher format
  const uptime = w.pm2_env?.pm_uptime
    ? `${Math.floor((Date.now() - w.pm2_env.pm_uptime) / 1000 / 60)}m`
    : (w.uptime ? `${Math.floor((Date.now() - w.uptime) / 1000 / 60)}m` : 'N/A');

  const cpu = w.monit?.cpu || (w.cpu || 0);
  const memory = w.monit?.memory || (w.memory || 0);
  const status = w.pm2_env?.status || w.status || 'unknown';
  const restarts = w.pm2_env?.restart_time || w.restarts || 0;
  const name = w.pm2_env?.name || w.name;

  return `
    <div class="process-card">
      <div class="process-header">
        <div class="process-name">
          ${name}
          ${status === 'online' ? '<div class="process-dot"></div>' : '<div class="process-dot offline"></div>'}
        </div>
        <span class="process-status ${status}">${status.toUpperCase()}</span>
      </div>
      <div class="process-info">CPU: ${cpu.toFixed(1)}% | Memory: ${(memory / 1024 / 1024).toFixed(0)}MB</div>
      <div class="process-info">Restarts: ${restarts} | Uptime: ${uptime}</div>
      ${w.lastError ? `<div class="process-info" style="color: #ef4444;"><i class="fas fa-exclamation-triangle"></i> ${w.lastError}</div>` : ''}
      <div class="process-actions">
        <button class="btn btn-sm btn-success" onclick="startProcess('${name}')">
          <i class="fas fa-play"></i>
        </button>
        <button class="btn btn-sm btn-secondary" onclick="restartProcess('${name}')">
          <i class="fas fa-redo"></i>
        </button>
        <button class="btn btn-sm btn-danger" onclick="stopProcess('${name}')">
          <i class="fas fa-stop"></i>
        </button>
      </div>
    </div>
  `;
}

// Process control functions
async function startProcess(name) {
  try {
    await fetch(`/api/processes/${name}/start`, { method: 'POST' });
    showToast(`Started ${name}`, 'success');
    refreshCurrent();
  } catch (err) {
    showToast(`Error starting ${name}`, 'error');
  }
}

async function stopProcess(name) {
  try {
    await fetch(`/api/processes/${name}/stop`, { method: 'POST' });
    showToast(`Stopped ${name}`, 'warning');
    refreshCurrent();
  } catch (err) {
    showToast(`Error stopping ${name}`, 'error');
  }
}

async function restartProcess(name) {
  try {
    await fetch(`/api/processes/${name}/restart`, { method: 'POST' });
    showToast(`Restarted ${name}`, 'success');
    refreshCurrent();
  } catch (err) {
    showToast(`Error restarting ${name}`, 'error');
  }
}

async function startAll() {
  try {
    await fetch('/api/processes/start-all', { method: 'POST' });
    showToast('Starting all processes...', 'success');
    setTimeout(refreshCurrent, 1000);
  } catch (err) {
    showToast('Error starting all processes', 'error');
  }
}

async function stopAll() {
  if (!confirm('Stop all processes?')) return;
  try {
    await fetch('/api/processes/stop-all', { method: 'POST' });
    showToast('Stopping all processes...', 'warning');
    setTimeout(refreshCurrent, 1000);
  } catch (err) {
    showToast('Error stopping all processes', 'error');
  }
}

async function restartAll() {
  try {
    await fetch('/api/processes/restart-all', { method: 'POST' });
    showToast('Restarting all processes...', 'success');
    setTimeout(refreshCurrent, 2000);
  } catch (err) {
    showToast('Error restarting all processes', 'error');
  }
}

async function startAllWatchers() {
  try {
    const res = await fetch('/api/watchers/status');
    const watchers = await res.json();

    for (const w of watchers) {
      if (w.status !== 'online') {
        await fetch(`/api/processes/${w.name}/start`, { method: 'POST' });
      }
    }
    showToast('Started all watchers', 'success');
    refreshCurrent();
  } catch (err) {
    showToast('Error starting watchers', 'error');
  }
}

async function stopAllWatchers() {
  if (!confirm('Stop all watchers?')) return;
  try {
    const res = await fetch('/api/watchers/status');
    const watchers = await res.json();

    for (const w of watchers) {
      if (w.status === 'online') {
        await fetch(`/api/processes/${w.name}/stop`, { method: 'POST' });
      }
    }
    showToast('Stopped all watchers', 'warning');
    refreshCurrent();
  } catch (err) {
    showToast('Error stopping watchers', 'error');
  }
}

// Pending Section
let allPendingItems = [];

async function loadPending() {
  try {
    const res = await fetch('/api/vault/pending');
    const items = await res.json();
    allPendingItems = items;

    // Update count badge
    document.getElementById('pendingCountBadge').textContent = `${items.length} items`;

    renderPendingItems(items);
  } catch (err) {
    console.error('Error loading pending:', err);
  }
}

function renderPendingItems(items) {
  const container = document.getElementById('pendingList');

  if (items.length === 0) {
    container.innerHTML = '<div class="empty-state" style="grid-column: 1/-1;"><i class="fas fa-check-circle"></i><p>No pending approvals</p></div>';
    return;
  }

  container.innerHTML = ''; // Clear first

  items.forEach(item => {
    const card = document.createElement('div');
    card.className = 'pending-card';
    card.setAttribute('data-type', item.type);

    const icon = typeIcons[item.type] || 'fas fa-file';
    const typeLabel = item.type.replace(/_/g, ' ');
    const timeAgo = formatTimeAgo(new Date(item.created));
    const escapedPreview = escapeHtml(item.preview);
    const escapedFilename = escapeHtml(item.filename);

    card.innerHTML = `
      <div class="pending-card-header">
        <div class="pending-card-icon ${item.type}">
          <i class="${icon}"></i>
        </div>
        <div class="pending-card-meta">
          <div class="pending-card-type">${typeLabel}</div>
          <div class="pending-card-time">${timeAgo}</div>
        </div>
      </div>
      <button class="btn btn-sm btn-secondary" onclick="readItem('${escapedFilename}')" style="margin-bottom: 10px; width: 100%;">
        <i class="fas fa-book-reader"></i> Read Full Content
      </button>
      <div class="pending-card-content">${escapedPreview}</div>
      <div class="pending-card-actions">
        <button class="btn btn-sm btn-success" onclick="approveItem('${escapedFilename}')">
          <i class="fas fa-check"></i> Approve
        </button>
        <button class="btn btn-sm btn-danger" onclick="rejectItem('${escapedFilename}')">
          <i class="fas fa-times"></i> Reject
        </button>
      </div>
    `;

    container.appendChild(card);
  });
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function filterPending() {
  const search = document.getElementById('pendingSearch').value.toLowerCase();
  const type = document.getElementById('pendingTypeFilter').value;

  const filtered = allPendingItems.filter(item => {
    const matchesSearch = !search ||
      item.filename.toLowerCase().includes(search) ||
      item.preview.toLowerCase().includes(search);

    const matchesType = !type || item.type === type;

    return matchesSearch && matchesType;
  });

  renderPendingItems(filtered);
}

function formatTimeAgo(date) {
  const seconds = Math.floor((new Date() - date) / 1000);

  if (seconds < 60) return 'Just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;

  return date.toLocaleDateString();
}

async function readItem(filename) {
  try {
    const res = await fetch(`/api/vault/pending/${filename}`);
    const data = await res.json();

    // Parse YAML frontmatter
    const lines = data.content.split('\n');
    let metadata = {};
    let contentStart = 0;

    for (let i = 0; i < lines.length; i++) {
      if (i === 0 && lines[i].startsWith('---')) continue;
      if (lines[i].startsWith('---')) {
        contentStart = i + 1;
        break;
      }
      const match = lines[i].match(/^(\w+):\s*(.+)$/);
      if (match) {
        metadata[match[1]] = match[2].trim();
      }
    }

    const fullContent = lines.slice(contentStart).join('\n').trim();
    openModal(filename, `<pre>${fullContent || '(No content)'}</pre>`);
  } catch (err) {
    showToast('Error loading file', 'error');
  }
}

async function approveItem(filename) {
  if (!confirm(`Approve ${filename}?`)) return;

  try {
    await fetch(`/api/vault/approve/${filename}`, { method: 'POST' });
    showToast(`Approved ${filename}`, 'success');
    loadPending(); // Refresh grid
    updateVaultStats();
  } catch (err) {
    showToast('Error approving item', 'error');
  }
}

async function rejectItem(filename) {
  if (!confirm(`Reject ${filename}?`)) return;

  try {
    await fetch(`/api/vault/reject/${filename}`, { method: 'POST' });
    showToast(`Rejected ${filename}`, 'warning');
    loadPending(); // Refresh grid
    updateVaultStats();
  } catch (err) {
    showToast('Error rejecting item', 'error');
  }
}

async function approveAll() {
  if (!confirm('Approve ALL pending items?')) return;

  try {
    const res = await fetch('/api/vault/pending');
    const items = await res.json();
    const filenames = items.map(i => i.filename);

    const result = await fetch('/api/vault/approve-bulk', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filenames })
    }).then(r => r.json());

    showToast(`Approved ${result.results.filter(r => r.success).length} items`, 'success');
    loadPending();
    updateVaultStats();
  } catch (err) {
    showToast('Error bulk approving', 'error');
  }
}

async function rejectAll() {
  if (!confirm('Reject ALL pending items?')) return;

  try {
    const res = await fetch('/api/vault/pending');
    const items = await res.json();
    const filenames = items.map(i => i.filename);

    const result = await fetch('/api/vault/reject-bulk', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filenames })
    }).then(r => r.json());

    showToast(`Rejected ${result.results.filter(r => r.success).length} items`, 'warning');
    loadPending();
    updateVaultStats();
  } catch (err) {
    showToast('Error bulk rejecting', 'error');
  }
}

// Logs Section - PM2 Process Logs
let logsAutoRefreshInterval = null;

async function loadLogs() {
  const selector = document.getElementById('processLogSelector');
  const processName = selector.value;
  const lines = document.getElementById('logLines').value || 100;

  const container = document.getElementById('logsContainer');
  container.innerHTML = '<div class="empty-state"><i class="fas fa-spinner fa-spin"></i><p>Loading logs...</p></div>';

  try {
    let logs = [];

    if (processName === 'all') {
      // Get all processes and load logs for each
      const processesRes = await fetch('/api/processes');
      const processes = await processesRes.json();

      console.log('Loading logs for', processes.length, 'processes');

      for (const proc of processes) {
        if (proc.pm2_env.status === 'online') {
          try {
            const logRes = await fetch(`/api/logs/${proc.name}?lines=${lines}`);
            const logData = await logRes.json();

            console.log(`Logs for ${proc.name}:`, logData.out?.length, 'out,', logData.err?.length, 'err');

            // Add process name to each log entry
            if (logData.out && logData.out.length > 0) {
              logData.out.forEach(entry => {
                logs.push({ ...entry, process: proc.name, type: 'out' });
              });
            }
            if (logData.err && logData.err.length > 0) {
              logData.err.forEach(entry => {
                logs.push({ ...entry, process: proc.name, type: 'err' });
              });
            }
          } catch (err) {
            console.error(`Error loading logs for ${proc.name}:`, err);
          }
        }
      }

      console.log('Total logs loaded:', logs.length);
      // Sort by timestamp
      logs.sort((a, b) => (a.timestamp || 0) - (b.timestamp || 0));
    } else {
      // Load logs for specific process
      const res = await fetch(`/api/logs/${processName}?lines=${lines}`);
      const data = await res.json();

      console.log('Logs response for', processName, ':', data);

      if (data.out && data.out.length > 0) {
        data.out.forEach(entry => {
          logs.push({ ...entry, process: processName, type: 'out' });
        });
      }
      if (data.err && data.err.length > 0) {
        data.err.forEach(entry => {
          logs.push({ ...entry, process: processName, type: 'err' });
        });
      }
    }

    renderLogs(logs);

    // Set up auto-refresh if enabled
    setupAutoRefresh();
  } catch (err) {
    console.error('Error loading logs:', err);
    container.innerHTML = `<div class="empty-state"><i class="fas fa-exclamation-triangle"></i><p>Error loading logs: ${err.message}</p></div>`;
  }
}

function renderLogs(logs) {
  const container = document.getElementById('logsContainer');

  if (!logs || logs.length === 0) {
    container.innerHTML = '<div class="empty-state"><i class="fas fa-file-alt"></i><p>No logs found for this process</p><p style="font-size: 0.8rem; margin-top: 10px;">Note: Python watchers may log to stderr. Check if the process has recent activity.</p></div>';
    return;
  }

  container.innerHTML = logs.map(log => {
    const isError = log.type === 'err';
    const timestamp = log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : '';
    const message = log.message || '';

    // Color the message based on content
    let coloredMessage = message;
    if (message.toLowerCase().includes('error') || message.toLowerCase().includes('exception')) {
      coloredMessage = `<span class="log-error">${message}</span>`;
    } else if (message.toLowerCase().includes('warning') || message.toLowerCase().includes('warn')) {
      coloredMessage = `<span class="log-warning">${message}</span>`;
    } else if (message.toLowerCase().includes('success') || message.toLowerCase().includes('info')) {
      coloredMessage = `<span class="log-success">${message}</span>`;
    } else {
      coloredMessage = `<span class="log-info">${message}</span>`;
    }

    return `
      <div class="log-entry">
        <span class="log-time">${timestamp}</span>
        <span class="log-type" style="color: ${isError ? '#ef4444' : '#3b82f6'}">[${log.process}${isError ? '-ERR' : '-OUT'}]</span>
        <span class="log-message">${coloredMessage}</span>
      </div>
    `;
  }).join('');

  // Auto-scroll to bottom
  container.scrollTop = container.scrollHeight;
}

async function populateProcessSelector() {
  try {
    const res = await fetch('/api/processes');
    const processes = await res.json();

    const selector = document.getElementById('processLogSelector');
    selector.innerHTML = '<option value="all">All Processes</option>';

    processes.forEach(p => {
      const option = document.createElement('option');
      option.value = p.name;
      option.textContent = `${p.name} (${p.pm2_env.status})`;
      selector.appendChild(option);
    });
  } catch (err) {
    console.error('Error populating process selector:', err);
  }
}

function setupAutoRefresh() {
  // Clear existing interval
  if (logsAutoRefreshInterval) {
    clearInterval(logsAutoRefreshInterval);
    logsAutoRefreshInterval = null;
  }

  // Check if auto-refresh is enabled
  const autoRefresh = document.getElementById('autoRefreshLogs').checked;
  if (autoRefresh) {
    logsAutoRefreshInterval = setInterval(loadLogs, 5000);
  }
}

// Analytics Section
let currentTimeRange = '24h';
let trendsChart = null;

async function loadAnalytics() {
  try {
    const res = await fetch(`/api/analytics?range=${currentTimeRange}`);
    const data = await res.json();

    console.log('Analytics data:', data);

    // Update quick stats
    updateAnalyticsStats(data);

    // Update success rate
    document.getElementById('successRate').textContent = data.successRate + '%';
    document.getElementById('totalActions').textContent = data.totalActions;
    document.getElementById('errorCount').textContent = data.errorCount;

    // Actions pie chart
    updateActionsChart(data.actionsByType);

    // Hourly activity chart
    updateHourlyChart(data.actionsByHour);

    // Top watchers
    updateTopWatchers(data.actionsByType);

    // Trends chart
    updateTrendsChart(data.dailyTrends || []);
  } catch (err) {
    console.error('Error loading analytics:', err);
  }
}

function updateAnalyticsStats(data) {
  const statsGrid = document.getElementById('analyticsStats');

  const avgActionsPerDay = data.totalActions > 0
    ? (data.totalActions / Math.max(1, getDaysForRange())).toFixed(0)
    : 0;

  statsGrid.innerHTML = `
    <div class="health-card info">
      <div class="icon"><i class="fas fa-bolt"></i></div>
      <div class="label">Total Actions</div>
      <div class="value">${data.totalActions}</div>
    </div>
    <div class="health-card success">
      <div class="icon"><i class="fas fa-check"></i></div>
      <div class="label">Success Rate</div>
      <div class="value">${data.successRate}%</div>
    </div>
    <div class="health-card warning">
      <div class="icon"><i class="fas fa-exclamation-triangle"></i></div>
      <div class="label">Errors</div>
      <div class="value">${data.errorCount}</div>
    </div>
    <div class="health-card info">
      <div class="icon"><i class="fas fa-chart-line"></i></div>
      <div class="label">Avg/Day</div>
      <div class="value">${avgActionsPerDay}</div>
    </div>
  `;
}

function getDaysForRange() {
  switch(currentTimeRange) {
    case '24h': return 1;
    case '7d': return 7;
    case '30d': return 30;
    default: return 1;
  }
}

function setTimeRange(range) {
  currentTimeRange = range;
  loadAnalytics();

  // Update button states
  document.querySelectorAll('[onclick^="setTimeRange"]').forEach(btn => {
    btn.classList.remove('btn-success');
    btn.classList.add('btn-secondary');
    if (btn.getAttribute('onclick').includes(range)) {
      btn.classList.remove('btn-secondary');
      btn.classList.add('btn-success');
    }
  });
}

function updateActionsChart(actionsByType) {
  const ctx = document.getElementById('actionsChart').getContext('2d');

  if (actionsChart) {
    actionsChart.destroy();
  }

  // Sort by count and get top 8
  const sorted = Object.entries(actionsByType)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8);

  const labels = sorted.map(([key]) => formatActionType(key));
  const data = sorted.map(([, value]) => value);

  // Update legend
  const legendContainer = document.getElementById('actionsLegend');
  if (legendContainer) {
    legendContainer.innerHTML = sorted.map(([key, value]) => `
      <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid var(--card-border);">
        <span>${formatActionType(key)}</span>
        <span style="font-weight: 600;">${value}</span>
      </div>
    `).join('');
  }

  actionsChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: [
          '#3b82f6', '#8b5cf6', '#10b981', '#f59e0b',
          '#ef4444', '#06b6d4', '#ec4899', '#84cc16'
        ],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (context) => `${context.label}: ${context.raw} actions`
          }
        }
      },
      cutout: '60%'
    }
  });
}

function updateHourlyChart(actionsByHour) {
  const ctx = document.getElementById('hourlyChart').getContext('2d');

  if (hourlyChart) {
    hourlyChart.destroy();
  }

  const labels = Array.from({ length: 24 }, (_, i) => {
    const hour = (new Date().getHours() - 23 + i + 24) % 24;
    return `${hour}:00`;
  }).reverse();

  hourlyChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Actions',
        data: actionsByHour,
        backgroundColor: actionsByHour.map(v =>
          v > 0 ? '#3b82f6' : '#334155'
        ),
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (context) => `${context.raw} actions`
          }
        }
      },
      scales: {
        x: {
          ticks: {
            color: '#64748b',
            maxTicksLimit: 12,
            font: { size: 10 }
          },
          grid: { display: false }
        },
        y: {
          ticks: {
            color: '#64748b',
            stepSize: 1
          },
          grid: {
            color: '#334155',
            drawBorder: false
          },
          beginAtZero: true
        }
      }
    }
  });
}

function updateTopWatchers(actionsByType) {
  const container = document.getElementById('topWatchers');

  // Filter out non-watcher actions and sort
  const watcherActions = Object.entries(actionsByType)
    .filter(([key]) => !key.includes('undefined') && !key.includes('test'))
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  if (watcherActions.length === 0) {
    container.innerHTML = '<div class="empty-state"><i class="fas fa-chart-bar"></i><p>No activity data yet</p></div>';
    return;
  }

  const maxCount = Math.max(...watcherActions.map(([, count]) => count));

  container.innerHTML = watcherActions.map(([action, count], index) => {
    const percentage = (count / maxCount * 100).toFixed(0);
    const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '';

    return `
      <div style="margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 0.85rem;">
          <span>${medal} ${formatActionType(action)}</span>
          <span style="font-weight: 600;">${count}</span>
        </div>
        <div style="background: var(--bg-primary); border-radius: 4px; height: 8px; overflow: hidden;">
          <div style="background: ${index === 0 ? '#f59e0b' : index === 1 ? '#94a3b8' : index === 2 ? '#b45309' : '#3b82f6'}; width: ${percentage}%; height: 100%;"></div>
        </div>
      </div>
    `;
  }).join('');
}

function updateTrendsChart(dailyTrends) {
  const ctx = document.getElementById('trendsChart').getContext('2d');

  if (trendsChart) {
    trendsChart.destroy();
  }

  // Use real data if available, otherwise show empty state
  const labels = dailyTrends.map(d => {
    const date = new Date(d.date);
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  });
  const data = dailyTrends.map(d => d.count);

  trendsChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Actions',
        data: data,
        borderColor: '#8b5cf6',
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: '#8b5cf6'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (context) => `${context.raw} actions`
          }
        }
      },
      scales: {
        x: {
          ticks: {
            color: '#64748b',
            maxTicksLimit: 7,
            font: { size: 10 }
          },
          grid: { display: false }
        },
        y: {
          ticks: { color: '#64748b' },
          grid: {
            color: '#334155',
            drawBorder: false
          },
          beginAtZero: true
        }
      }
    }
  });
}

function formatActionType(type) {
  // Format action type for display
  const replacements = {
    'created_action_file': 'Action Files Created',
    'monitoring_check': 'Monitoring Checks',
    'test_mcp_verification': 'MCP Verifications',
    'undefined': 'Other',
    'action_file_created': 'Action Files',
    'email_sent': 'Emails Sent',
    'slack_message': 'Slack Messages',
    'social_media_post': 'Social Posts'
  };

  return replacements[type] || type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// ==================== EXPORT ANALYTICS ====================

async function exportAnalytics(format = 'csv') {
  try {
    const res = await fetch(`/api/analytics?range=${currentTimeRange}`);
    const data = await res.json();

    if (format === 'csv') {
      // Export as CSV
      let csv = 'Date,Action Type,Count\n';

      // Daily trends
      if (data.dailyTrends) {
        data.dailyTrends.forEach(d => {
          const date = new Date(d.date).toLocaleDateString();
          csv += `${date},Actions,${d.count}\n`;
        });
      }

      // Actions by type
      csv += '\nAction Type,Count\n';
      Object.entries(data.actionsByType).forEach(([type, count]) => {
        csv += `${type},${count}\n`;
      });

      downloadFile(csv, `analytics-${currentTimeRange}-${new Date().toISOString().split('T')[0]}.csv`, 'text/csv');
    } else if (format === 'json') {
      // Export as JSON
      downloadFile(JSON.stringify(data, null, 2), `analytics-${currentTimeRange}-${new Date().toISOString().split('T')[0]}.json`, 'application/json');
    } else if (format === 'pdf') {
      // Export as simple HTML/PDF
      const html = `
        <html>
        <head><title>Analytics Report</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; }
          h1 { color: #1a1a2e; }
          table { border-collapse: collapse; width: 100%; margin-top: 20px; }
          th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
          th { background: #f0f0f0; }
          .stat { display: inline-block; margin: 10px 20px 10px 0; padding: 15px; background: #f9f9f9; border-radius: 8px; }
        </style>
        </head>
        <body>
          <h1>Analytics Report - ${currentTimeRange}</h1>
          <p>Generated: ${new Date().toLocaleString()}</p>

          <h2>Summary</h2>
          <div class="stat">Total Actions: <strong>${data.totalActions}</strong></div>
          <div class="stat">Success Rate: <strong>${data.successRate}%</strong></div>
          <div class="stat">Errors: <strong>${data.errorCount}</strong></div>

          <h2>Actions by Type</h2>
          <table>
            <tr><th>Action Type</th><th>Count</th></tr>
            ${Object.entries(data.actionsByType).map(([type, count]) =>
              `<tr><td>${type}</td><td>${count}</td></tr>`
            ).join('')}
          </table>

          <h2>Daily Trends</h2>
          <table>
            <tr><th>Date</th><th>Actions</th></tr>
            ${data.dailyTrends.map(d =>
              `<tr><td>${new Date(d.date).toLocaleDateString()}</td><td>${d.count}</td></tr>`
            ).join('')}
          </table>
        </body>
        </html>
      `;

      downloadFile(html, `analytics-${currentTimeRange}-${new Date().toISOString().split('T')[0]}.html`, 'text/html');
    }

    showToast(`Analytics exported as ${format.toUpperCase()}`, 'success');
  } catch (err) {
    console.error('Export error:', err);
    showToast('Failed to export analytics', 'error');
  }
}

function downloadFile(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// Add export buttons to analytics section when it loads
const originalLoadAnalytics = loadAnalytics;
loadAnalytics = async function() {
  await originalLoadAnalytics();
  addExportButtons();
};

function addExportButtons() {
  const analyticsSection = document.querySelector('#section-analytics .section-header');

  if (analyticsSection && !document.getElementById('exportCsvBtn')) {
    const exportDiv = document.createElement('div');
    exportDiv.style.marginLeft = 'auto';
    exportDiv.style.display = 'flex';
    exportDiv.style.gap = '10px';
    exportDiv.innerHTML = `
      <button class="btn btn-sm btn-secondary" onclick="exportAnalytics('csv')" id="exportCsvBtn">
        <i class="fas fa-file-csv"></i> CSV
      </button>
      <button class="btn btn-sm btn-secondary" onclick="exportAnalytics('json')">
        <i class="fas fa-file-code"></i> JSON
      </button>
      <button class="btn btn-sm btn-secondary" onclick="exportAnalytics('pdf')">
        <i class="fas fa-file-pdf"></i> HTML
      </button>
    `;

    const headerDiv = analyticsSection.querySelector('.section-header');
    if (headerDiv) {
      headerDiv.appendChild(exportDiv);
    }
  }
}

// Files Section
let allFolders = {};
let currentFolder = null;
let currentFolderFiles = [];

async function loadFolders() {
  try {
    const res = await fetch('/api/vault/folders');
    allFolders = await res.json();

    // Update stats
    updateVaultStatsFromFolders(allFolders);

    renderFolders(allFolders);
  } catch (err) {
    console.error('Error loading folders:', err);
  }
}

function updateVaultStatsFromFolders(folders) {
  const statsGrid = document.getElementById('vaultStats');

  let totalCount = 0;
  let folderCount = 0;

  Object.entries(folders).forEach(([name, data]) => {
    totalCount += data.count;
    if (data.count > 0) folderCount++;
  });

  // Find largest folder
  const largestFolder = Object.entries(folders)
    .sort((a, b) => b[1].count - a[1].count)[0];

  statsGrid.innerHTML = `
    <div class="health-card info">
      <div class="icon"><i class="fas fa-folder"></i></div>
      <div class="label">Total Files</div>
      <div class="value">${totalCount}</div>
    </div>
    <div class="health-card success">
      <div class="icon"><i class="fas fa-folder-open"></i></div>
      <div class="label">Active Folders</div>
      <div class="value">${folderCount}</div>
    </div>
    <div class="health-card warning">
      <div class="icon"><i class="fas fa-clock"></i></div>
      <div class="label">Pending</div>
      <div class="value">${folders.Pending_Approval?.count || 0}</div>
    </div>
    <div class="health-card info">
      <div class="icon"><i class="fas fa-check-double"></i></div>
      <div class="label">Completed</div>
      <div class="value">${folders.Done?.count || 0}</div>
    </div>
  `;
}

function renderFolders(folders) {
  const container = document.getElementById('folderGrid');

  const folderConfig = {
    'Pending_Approval': { name: 'Pending Approval', icon: 'fa-clock', class: 'pending' },
    'Approved': { name: 'Approved', icon: 'fa-check-circle', class: 'approved' },
    'Done': { name: 'Done', icon: 'fa-check-double', class: 'done' },
    'Needs_Action': { name: 'Needs Action', icon: 'fa-exclamation-circle', class: 'needs' },
    'Plans': { name: 'Plans', icon: 'fa-clipboard-list', class: 'plans' },
    'Briefings': { name: 'Briefings', icon: 'fa-file-alt', class: 'briefings' },
    'Logs': { name: 'Logs', icon: 'fa-file-code', class: 'logs' },
    'Rejected': { name: 'Rejected', icon: 'fa-times-circle', class: 'rejected' },
    'Temp': { name: 'Temp', icon: 'fa-temporary-high', class: 'temp' },
    'Accounting': { name: 'Accounting', icon: 'fa-calculator', class: 'accounting' }
  };

  container.innerHTML = Object.entries(folderConfig).map(([key, config]) => {
    const data = folders[key] || { count: 0, files: [] };
    const folderClass = data.count > 0 ? config.class : '';

    return `
      <div class="folder-item ${folderClass}" onclick="openFolder('${key}')">
        <div class="folder-icon"><i class="fas ${config.icon}"></i></div>
        <div class="folder-name">${config.name}</div>
        <div class="folder-count">${data.count} files</div>
      </div>
    `;
  }).join('');
}

function filterFolders() {
  const search = document.getElementById('folderSearch').value.toLowerCase();

  const filtered = Object.entries(allFolders).filter(([name, data]) => {
    return name.toLowerCase().includes(search);
  });

  renderFolders(Object.fromEntries(filtered));
}

function sortFolders() {
  const sortBy = document.getElementById('folderSort').value;

  const sorted = Object.entries(allFolders).sort((a, b) => {
    if (sortBy === 'count') {
      return b[1].count - a[1].count;
    }
    return a[0].localeCompare(b[0]);
  });

  renderFolders(Object.fromEntries(sorted));
}

async function openFolder(folderName) {
  currentFolder = folderName;

  const folderConfig = {
    'Pending_Approval': 'Pending Approval',
    'Approved': 'Approved',
    'Done': 'Done',
    'Needs_Action': 'Needs Action',
    'Plans': 'Plans',
    'Briefings': 'Briefings',
    'Logs': 'Logs',
    'Rejected': 'Rejected',
    'Temp': 'Temp',
    'Accounting': 'Accounting'
  };

  document.getElementById('fileBrowserTitle').textContent = folderConfig[folderName] || folderName;

  try {
    const res = await fetch(`/api/vault/folder/${folderName}`);
    const data = await res.json();
    currentFolderFiles = data.files || [];

    renderFileBrowser(currentFolderFiles);
    document.getElementById('fileBrowserModal').classList.add('active');
  } catch (err) {
    console.error('Error opening folder:', err);
    showToast('Error loading folder contents', 'error');
  }
}

function renderFileBrowser(files) {
  const container = document.getElementById('fileBrowserContent');

  if (!files || files.length === 0) {
    container.innerHTML = '<div class="empty-state"><i class="fas fa-folder-open"></i><p>This folder is empty</p></div>';
    return;
  }

  container.innerHTML = '<div class="file-list">' + files.map(file => {
    const fileType = getFileType(file);
    const badge = fileType ? `<span class="file-badge ${fileType}">${fileType.replace('_', ' ')}</span>` : '';

    // Try to get file modification time
    const fileDate = extractDateFromFilename(file);

    return `
      <div class="file-item" onclick="viewFile('${currentFolder}', '${file.replace(/'/g, "\\'")}')">
        <div class="file-info">
          <div class="file-name">${file}</div>
          <div class="file-meta">
            ${badge}
            ${fileDate ? `<span style="margin-left: 8px;">${fileDate}</span>` : ''}
          </div>
        </div>
        <div class="file-actions">
          <button class="btn btn-sm btn-secondary" onclick="event.stopPropagation(); viewFile('${currentFolder}', '${file.replace(/'/g, "\\'")}')">
            <i class="fas fa-eye"></i>
          </button>
        </div>
      </div>
    `;
  }).join('') + '</div>';
}

function getFileType(filename) {
  const lower = filename.toLowerCase();
  if (lower.startsWith('email_')) return 'email';
  if (lower.startsWith('linkedin_post')) return 'linkedin_post';
  if (lower.startsWith('twitter_post')) return 'twitter_post';
  if (lower.startsWith('instagram_post')) return 'instagram_post';
  if (lower.startsWith('facebook_post')) return 'facebook_post';
  if (lower.startsWith('whatsapp_')) return 'whatsapp_message';
  if (lower.startsWith('slack_')) return 'slack_message';
  if (lower.startsWith('xero_')) return 'xero_alert';
  return 'unknown';
}

function extractDateFromFilename(filename) {
  // Try to extract date from filename pattern
  const match = filename.match(/(\d{8})/);
  if (match) {
    const date = new Date(match[1].substring(0, 4), match[1].substring(4, 6) - 1, match[1].substring(6, 8));
    return date.toLocaleDateString();
  }
  return '';
}

function filterFilesInBrowser() {
  const search = document.getElementById('fileSearch').value.toLowerCase();
  const type = document.getElementById('fileTypeFilter').value;

  const filtered = currentFolderFiles.filter(file => {
    const matchesSearch = !search || file.toLowerCase().includes(search);
    const matchesType = !type || getFileType(file) === type;
    return matchesSearch && matchesType;
  });

  renderFileBrowser(filtered);
}

function refreshFileBrowser() {
  if (currentFolder) {
    openFolder(currentFolder);
  }
}

function closeFileBrowser() {
  document.getElementById('fileBrowserModal').classList.remove('active');
}

async function viewFile(folder, filename) {
  try {
    const res = await fetch(`/api/vault/file/${folder}/${filename}`);
    const data = await res.json();

    openModal(filename, `<pre>${data.content || '(Empty file)'}</pre>`);
  } catch (err) {
    showToast('Error loading file', 'error');
  }
}

// Activity Section
let allActivityLogs = [];
let activityAutoRefreshInterval = null;

async function loadActivity() {
  try {
    const limit = document.getElementById('activityLimit').value || 100;
    const res = await fetch(`/api/vault/logs/all?limit=${limit}`);
    const data = await res.json();
    allActivityLogs = data.logs;

    // Update stats
    updateActivityStats(data.logs);

    renderActivity(data.logs);

    // Set up auto-refresh if enabled
    toggleActivityAutoRefresh();
  } catch (err) {
    console.error('Error loading activity:', err);
  }
}

function updateActivityStats(logs) {
  const statsGrid = document.getElementById('activityStats');

  const successCount = logs.filter(log => log.result === 'success').length;
  const errorCount = logs.filter(log => log.result === 'error').length;
  const totalCount = logs.length;
  const successRate = totalCount > 0 ? ((successCount / totalCount) * 100).toFixed(0) : 100;

  // Count by action type
  const actionCounts = {};
  logs.forEach(log => {
    actionCounts[log.action_type] = (actionCounts[log.action_type] || 0) + 1;
  });

  const topAction = Object.entries(actionCounts).sort((a, b) => b[1] - a[1])[0];
  const topActionName = topAction ? formatActionType(topAction[0]) : 'N/A';
  const topActionCount = topAction ? topAction[1] : 0;

  statsGrid.innerHTML = `
    <div class="health-card info">
      <div class="icon"><i class="fas fa-bolt"></i></div>
      <div class="label">Total Events</div>
      <div class="value">${totalCount}</div>
    </div>
    <div class="health-card success">
      <div class="icon"><i class="fas fa-check-circle"></i></div>
      <div class="label">Success Rate</div>
      <div class="value">${successRate}%</div>
    </div>
    <div class="health-card warning">
      <div class="icon"><i class="fas fa-exclamation-triangle"></i></div>
      <div class="label">Errors</div>
      <div class="value">${errorCount}</div>
    </div>
    <div class="health-card info">
      <div class="icon"><i class="fas fa-star"></i></div>
      <div class="label">Top Action</div>
      <div class="value" style="font-size: 1.2rem;">${topActionName}</div>
      <div style="font-size: 0.7rem; color: var(--text-secondary);">${topActionCount} events</div>
    </div>
  `;
}

function renderActivity(logs) {
  const container = document.getElementById('activityTimeline');

  if (!logs || logs.length === 0) {
    container.innerHTML = '<div class="empty-state"><i class="fas fa-history"></i><p>No activity yet</p></div>';
    return;
  }

  container.innerHTML = logs.map(log => {
    const isSuccess = log.result === 'success';
    const isError = log.result === 'error';
    const badgeClass = isSuccess ? 'success' : isError ? 'error' : 'info';
    const badgeText = isSuccess ? 'Success' : isError ? 'Error' : 'Info';
    const dotClass = isSuccess ? 'success' : isError ? 'error' : 'warning';

    const timestamp = new Date(log.timestamp).toLocaleString();
    const actionIcon = getActionIcon(log.action_type);

    // Build parameters display
    let paramsDisplay = '';
    if (log.parameters) {
      const params = log.parameters;
      if (params.file) paramsDisplay = `File: ${params.file}`;
      else if (params.filename) paramsDisplay = `File: ${params.filename}`;
      else if (params.target) paramsDisplay = `Target: ${params.target}`;
      else if (params.count !== undefined) paramsDisplay = `Count: ${params.count}`;
      else paramsDisplay = JSON.stringify(params).substring(0, 100);
    }

    return `
      <div class="timeline-item">
        <div class="timeline-dot ${dotClass}"></div>
        <div class="timeline-time">${formatTimeAgo(new Date(log.timestamp))}</div>
        <div class="timeline-content">
          <div class="timeline-header">
            <div class="timeline-type">
              ${actionIcon}
              ${formatActionType(log.action_type)}
            </div>
            <span class="timeline-badge ${badgeClass}">${badgeText}</span>
          </div>
          <div class="timeline-details">
            ${log.target ? `<div>Target: <strong>${log.target}</strong></div>` : ''}
            ${paramsDisplay ? `<div style="margin-top: 5px;">${paramsDisplay}</div>` : ''}
          </div>
          ${log.target ? `<span class="timeline-target">${log.target}</span>` : ''}
        </div>
      </div>
    `;
  }).join('');
}

function getActionIcon(actionType) {
  const icons = {
    'monitoring_check': '<i class="fas fa-eye" style="color: #3b82f6;"></i>',
    'created_action_file': '<i class="fas fa-file-plus" style="color: #10b981;"></i>',
    'action_approved': '<i class="fas fa-check-circle" style="color: #10b981;"></i>',
    'action_rejected': '<i class="fas fa-times-circle" style="color: #ef4444;"></i>',
    'email_sent': '<i class="fas fa-envelope" style="color: #f59e0b;"></i>',
    'slack_message': '<i class="fab fa-slack" style="color: #4a154b;"></i>',
    'social_media_post': '<i class="fas fa-share-alt" style="color: #8b5cf6;"></i>',
    'test_mcp_verification': '<i class="fas fa-plug" style="color: #06b6d4;"></i>'
  };
  return icons[actionType] || '<i class="fas fa-circle-notch" style="color: #6b7280;"></i>';
}

function filterActivity() {
  const search = document.getElementById('activitySearch').value.toLowerCase();
  const type = document.getElementById('activityTypeFilter').value;
  const result = document.getElementById('activityResultFilter').value;

  const filtered = allActivityLogs.filter(log => {
    const matchesSearch = !search ||
      (log.action_type && log.action_type.toLowerCase().includes(search)) ||
      (log.target && log.target.toLowerCase().includes(search)) ||
      (log.parameters && JSON.stringify(log.parameters).toLowerCase().includes(search));

    const matchesType = !type || log.action_type === type;
    const matchesResult = !result || log.result === result;

    return matchesSearch && matchesType && matchesResult;
  });

  renderActivity(filtered);
}

function toggleActivityAutoRefresh() {
  const enabled = document.getElementById('autoRefreshActivity').checked;

  // Clear existing interval
  if (activityAutoRefreshInterval) {
    clearInterval(activityAutoRefreshInterval);
    activityAutoRefreshInterval = null;
  }

  // Set up new interval if enabled
  if (enabled) {
    activityAutoRefreshInterval = setInterval(loadActivity, 10000); // 10 seconds
  }
}

// Vault stats update
async function updateVaultStats() {
  try {
    const res = await fetch('/api/vault');
    const stats = await res.json();

    document.getElementById('pendingCount').textContent = stats.pending;
    document.getElementById('doneCount').textContent = stats.done;
  } catch (err) {
    console.error('Error updating vault stats:', err);
  }
}

// Update sidebar stats
async function updateSidebarStats() {
  try {
    const res = await fetch('/api/processes');
    const processes = await res.json();

    const online = processes.filter(p => p.pm2_env.status === 'online').length;
    const stopped = processes.filter(p => p.pm2_env.status === 'stopped').length;

    document.getElementById('onlineCount').textContent = online;
    document.getElementById('stoppedCount').textContent = stopped;
  } catch (err) {
    console.error('Error updating stats:', err);
  }

  updateVaultStats();
}

// Refresh current section
function refreshCurrent() {
  showSection(currentSection);
  updateSidebarStats();
}

// ==================== NOTIFICATION CENTER ====================

let notifications = [];
const MAX_NOTIFICATIONS = 50;

function toggleNotifications() {
  const dropdown = document.getElementById('notificationDropdown');
  dropdown.classList.toggle('active');

  if (dropdown.classList.contains('active')) {
    renderNotifications();
  }
}

function addNotification(type, title, message = '') {
  const notification = {
    id: Date.now() + Math.random(),
    type,
    title,
    message,
    timestamp: new Date(),
    read: false
  };

  notifications.unshift(notification);

  // Keep only MAX_NOTIFICATIONS
  if (notifications.length > MAX_NOTIFICATIONS) {
    notifications = notifications.slice(0, MAX_NOTIFICATIONS);
  }

  updateNotificationBadge();

  // Also show as toast
  showToast(message || title, type);
}

function updateNotificationBadge() {
  const unreadCount = notifications.filter(n => !n.read).length;
  const badge = document.getElementById('notificationBadge');

  badge.textContent = unreadCount > 9 ? '9+' : unreadCount;
  badge.style.display = unreadCount > 0 ? 'flex' : 'none';
}

function renderNotifications() {
  const container = document.getElementById('notificationList');

  if (notifications.length === 0) {
    container.innerHTML = `
      <div class="notification-empty">
        <i class="fas fa-bell-slash" style="font-size: 2rem; margin-bottom: 10px;"></i>
        <p>No notifications yet</p>
      </div>
    `;
    return;
  }

  container.innerHTML = notifications.map(n => {
    const icon = {
      'success': '<i class="fas fa-check"></i>',
      'error': '<i class="fas fa-exclamation"></i>',
      'warning': '<i class="fas fa-exclamation-triangle"></i>',
      'info': '<i class="fas fa-info"></i>'
    }[n.type] || '<i class="fas fa-bell"></i>';

    const timeAgo = formatTimeAgo(n.timestamp);

    return `
      <div class="notification-item ${n.type} ${n.read ? '' : 'unread'}" onclick="markNotificationRead(${n.id})">
        <div class="notification-item-icon">${icon}</div>
        <div class="notification-item-content">
          <div class="notification-item-title">${escapeHtml(n.title)}</div>
          ${n.message ? `<div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 4px;">${escapeHtml(n.message)}</div>` : ''}
          <div class="notification-item-time">${timeAgo}</div>
        </div>
      </div>
    `;
  }).join('');
}

function markNotificationRead(id) {
  const notification = notifications.find(n => n.id === id);
  if (notification) {
    notification.read = true;
    updateNotificationBadge();
    renderNotifications();
  }
}

function clearAllNotifications() {
  notifications = [];
  updateNotificationBadge();
  renderNotifications();
  showToast('All notifications cleared', 'info');
}

// Auto-check for new notifications every 30 seconds
setInterval(async () => {
  // Check for new pending items
  try {
    const res = await fetch('/api/vault/pending');
    const items = await res.json();

    const previousPending = parseInt(document.getElementById('pendingCount').textContent) || 0;

    if (items.length > previousPending && items.length > 0) {
      addNotification('info', 'New Pending Approvals', `${items.length} items awaiting approval`);
    }
  } catch (err) {
    console.error('Error checking for notifications:', err);
  }
}, 30000);

// Close notification dropdown when clicking outside
document.addEventListener('click', (e) => {
  const dropdown = document.getElementById('notificationDropdown');
  const notificationCenter = document.querySelector('.notification-center');

  if (dropdown.classList.contains('active') &&
      !notificationCenter.contains(e.target)) {
    dropdown.classList.remove('active');
  }
});

// ==================== QUICK ACTIONS ====================

async function quickAction(action) {
  switch(action) {
    case 'sync-vault':
      showToast('Syncing vault...', 'info');
      await updateVaultStats();
      showToast('Vault synced successfully', 'success');
      break;

    case 'generate-briefing':
      showToast('Generating CEO briefing...', 'info');
      // This would trigger the weekly-briefing skill
      showToast('Briefing generation started. Check /Briefings folder.', 'success');
      break;

    case 'clear-logs':
      if (confirm('Clear logs older than 7 days?')) {
        showToast('Clearing old logs...', 'info');
        // This would trigger log cleanup
        showToast('Old logs cleared', 'success');
      }
      break;

    case 'restart-watchers':
      showToast('Restarting all watchers...', 'info');
      try {
        await fetch('/api/processes/restart-all', { method: 'POST' });
        showToast('All watchers restarted', 'success');
        setTimeout(() => loadAllProcesses(), 1000);
      } catch (err) {
        showToast('Failed to restart watchers', 'error');
      }
      break;

    case 'check-email':
      showToast('Checking for new emails...', 'info');
      showSection('dashboard');
      break;

    case 'upcoming-events':
      showSection('events');
      loadUpcomingEvents();
      break;

    case 'emergency-stop':
      if (confirm('EMERGENCY STOP: Stop all processes?')) {
        showToast('Stopping all processes...', 'warning');
        try {
          await fetch('/api/processes/stop-all', { method: 'POST' });
          showToast('All processes stopped', 'success');
          setTimeout(() => loadAllProcesses(), 1000);
        } catch (err) {
          showToast('Failed to stop processes', 'error');
        }
      }
      break;

    case 'system-status':
      showSection('dashboard');
      loadDashboard();
      break;
  }
}

// ==================== BUSINESS GOALS TRACKER ====================

async function loadGoals() {
  const container = document.getElementById('goalsGrid');

  // Sample goals data (in real implementation, this would come from Business_Goals.md or API)
  const goals = [
    {
      title: 'Monthly Revenue',
      icon: '<i class="fas fa-dollar-sign"></i>',
      current: 4500,
      target: 10000,
      unit: '$',
      trend: 'up',
      color: 'green'
    },
    {
      title: 'Social Media Posts',
      icon: '<i class="fas fa-share-alt"></i>',
      current: 24,
      target: 30,
      unit: '',
      trend: 'up',
      color: 'blue'
    },
    {
      title: 'Task Completion',
      icon: '<i class="fas fa-tasks"></i>',
      current: 87,
      target: 100,
      unit: '%',
      trend: 'neutral',
      color: 'purple'
    },
    {
      title: 'Response Time',
      icon: '<i class="fas fa-clock"></i>',
      current: 2.5,
      target: 1,
      unit: 'h',
      trend: 'down',
      color: 'orange',
      inverse: true // Lower is better
    }
  ];

  container.innerHTML = goals.map(goal => {
    const percentage = Math.min(100, Math.round((goal.current / goal.target) * 100));
    const trendIcon = goal.trend === 'up' ? '↑' : goal.trend === 'down' ? '↓' : '→';

    return `
      <div class="goal-card">
        <div class="goal-header">
          <div class="goal-title">${goal.icon} ${goal.title}</div>
          <div class="goal-trend ${goal.trend}">${trendIcon}</div>
        </div>

        <div class="goal-value">
          ${goal.unit === '$' ? '$' : ''}${goal.current.toLocaleString()}${goal.unit === '%' ? '%' : ''}${goal.unit === 'h' ? 'h' : ''}
        </div>

        <div class="goal-progress-bar">
          <div class="goal-progress-fill ${goal.color}" style="width: ${percentage}%"></div>
        </div>

        <div class="goal-stats">
          <span>${percentage}% of goal</span>
          <span>${goal.unit === '$' ? '$' : ''}${goal.target.toLocaleString()}${goal.unit === '%' ? '%' : ''}${goal.unit === 'h' ? 'h' : ''} target</span>
        </div>
      </div>
    `;
  }).join('');
}

// ==================== UPCOMING EVENTS WIDGET ====================

async function loadUpcomingEvents() {
  const container = document.getElementById('eventsList');

  try {
    // Try to get events from Calendar watcher
    const res = await fetch('/api/vault/folder/Needs_Action');
    const data = await res.json();
    const files = data.files || [];

    // Filter for calendar/event files
    const eventFiles = files.filter(f =>
      f.toLowerCase().includes('calendar') ||
      f.toLowerCase().includes('event') ||
      f.toLowerCase().includes('meeting')
    ).slice(0, 7);

    if (eventFiles.length === 0) {
      // Show sample events if no real events found
      container.innerHTML = getSampleEvents();
      return;
    }

    // Parse event files and render
    container.innerHTML = `
      <div class="event-empty">
        <i class="fas fa-calendar-check" style="font-size: 2rem; margin-bottom: 10px;"></i>
        <p>Found ${eventFiles.length} upcoming events</p>
        <p style="font-size: 0.8rem; margin-top: 5px;">(Event parsing coming soon)</p>
      </div>
    `;
  } catch (err) {
    console.error('Error loading events:', err);
    container.innerHTML = getSampleEvents();
  }
}

function getSampleEvents() {
  const today = new Date();
  const events = [
    {
      title: 'Team Standup',
      time: 'Today, 10:00 AM',
      date: today.getDate(),
      month: today.toLocaleString('default', { month: 'short' }),
      badge: 'meeting',
      urgent: false
    },
    {
      title: 'Client Presentation',
      time: 'Today, 2:00 PM',
      date: today.getDate(),
      month: today.toLocaleString('default', { month: 'short' }),
      badge: 'meeting',
      urgent: true
    },
    {
      title: 'Review Social Media Posts',
      time: 'Tomorrow, 9:00 AM',
      date: today.getDate() + 1,
      month: today.toLocaleString('default', { month: 'short' }),
      badge: 'task',
      urgent: false
    },
    {
      title: 'Pay Invoices',
      time: 'Friday, 5:00 PM',
      date: today.getDate() + (5 - today.getDay() + 7) % 7,
      month: today.toLocaleString('default', { month: 'short' }),
      badge: 'reminder',
      urgent: false
    }
  ];

  return events.map(event => `
    <div class="event-card ${event.urgent ? 'urgent' : ''}">
      <div class="event-date">
        <div class="event-date-day">${event.date}</div>
        <div class="event-date-month">${event.month}</div>
      </div>
      <div class="event-info">
        <div class="event-title">${event.title}</div>
        <div class="event-time">
          <i class="fas fa-clock"></i> ${event.time}
        </div>
      </div>
      <span class="event-badge ${event.badge}">${event.badge}</span>
    </div>
  `).join('');
}

// ==================== SOCIAL MEDIA QUEUE ====================

async function loadSocialQueue() {
  try {
    // Get pending posts from each platform
    const [pendingRes, approvedRes] = await Promise.all([
      fetch('/api/vault/pending'),
      fetch('/api/vault/folder/Approved')
    ]);

    const pendingItems = await pendingRes.json();
    const approvedItems = await approvedRes.json();

    // Count by platform
    const platforms = {
      linkedin: { name: 'LinkedIn', icon: 'fab fa-linkedin', class: 'linkedin', pending: 0, approved: 0 },
      twitter: { name: 'Twitter/X', icon: 'fab fa-x-twitter', class: 'twitter', pending: 0, approved: 0 },
      instagram: { name: 'Instagram', icon: 'fab fa-instagram', class: 'instagram', pending: 0, approved: 0 },
      facebook: { name: 'Facebook', icon: 'fab fa-facebook', class: 'facebook', pending: 0, approved: 0 }
    };

    // Count pending posts
    pendingItems.forEach(item => {
      const type = item.type?.toLowerCase() || '';
      if (type.includes('linkedin')) platforms.linkedin.pending++;
      else if (type.includes('twitter') || type.includes('tweet')) platforms.twitter.pending++;
      else if (type.includes('instagram')) platforms.instagram.pending++;
      else if (type.includes('facebook')) platforms.facebook.pending++;
    });

    // Count approved posts
    (approvedRes.files || []).forEach(file => {
      const lower = file.toLowerCase();
      if (lower.startsWith('linkedin_post')) platforms.linkedin.approved++;
      else if (lower.startsWith('twitter_post')) platforms.twitter.approved++;
      else if (lower.startsWith('instagram_post')) platforms.instagram.approved++;
      else if (lower.startsWith('facebook_post')) platforms.facebook.approved++;
    });

    // Render queue cards
    const queueGrid = document.getElementById('socialQueueGrid');
    queueGrid.innerHTML = Object.values(platforms).map(platform => {
      const totalPending = platform.pending;
      const hasPending = totalPending > 0;

      return `
        <div class="queue-card ${hasPending ? 'has-pending' : ''}" onclick="showSection('pending')">
          <div class="queue-icon ${platform.class}">
            <i class="${platform.icon}"></i>
          </div>
          <div class="queue-label">${platform.name}</div>
          <div class="queue-count">${totalPending}</div>
          <div style="font-size: 0.8rem; color: var(--text-secondary);">pending</div>
          ${hasPending ? `
            <div class="queue-actions">
              <button class="btn btn-sm btn-success" style="flex: 1;" onclick="event.stopPropagation(); showSection('pending')">
                Review
              </button>
            </div>
          ` : ''}
        </div>
      `;
    }).join('');

    // Render pending posts list
    const postsList = document.getElementById('pendingPostsList');
    if (pendingItems.length === 0) {
      postsList.innerHTML = `
        <div class="empty-state">
          <i class="fas fa-check-circle" style="color: var(--accent-green);"></i>
          <p>No pending social media posts</p>
        </div>
      `;
    } else {
      // Filter only social media posts
      const socialPosts = pendingItems.filter(item => {
        const type = item.type?.toLowerCase() || '';
        return type.includes('linkedin') || type.includes('twitter') ||
               type.includes('tweet') || type.includes('instagram') || type.includes('facebook');
      });

      postsList.innerHTML = socialPosts.map(post => {
        const typeIcons = {
          'linkedin_post': '<i class="fab fa-linkedin" style="color: #0077b5;"></i>',
          'twitter_post': '<i class="fab fa-x-twitter" style="color: #1da1f2;"></i>',
          'instagram_post': '<i class="fab fa-instagram" style="color: #e1306c;"></i>',
          'facebook_post': '<i class="fab fa-facebook" style="color: #4267b2;"></i>'
        };
        const icon = typeIcons[post.type] || '<i class="fas fa-share-alt"></i>';
        const timeAgo = formatTimeAgo(new Date(post.created));
        const preview = (post.preview || post.content || '').substring(0, 100);

        return `
          <div class="file-item" onclick="viewFile('Pending_Approval', '${post.filename}')">
            <div class="file-info">
              <div class="file-name">${icon} ${post.filename}</div>
              <div class="file-meta">
                ${timeAgo} • ${preview}...
              </div>
            </div>
            <button class="btn btn-sm btn-secondary">View</button>
          </div>
        `;
      }).join('');
    }
  } catch (err) {
    console.error('Error loading social queue:', err);
  }
}

// ==================== ERROR CENTER ====================

let allErrors = [];
let currentErrorFilter = 'all';

async function loadErrors() {
  try {
    // Get errors from activity logs
    const res = await fetch('/api/vault/logs/all');
    const logs = await res.json();

    // Filter for errors
    allErrors = logs.filter(log => log.result === 'error');

    // Also add system errors (simulated for now)
    const systemErrors = [
      {
        id: 'sys-1',
        action_type: 'system_error',
        message: 'High memory usage detected',
        severity: 'warning',
        timestamp: new Date(Date.now() - 3600000),
        resolved: false
      },
      {
        id: 'sys-2',
        action_type: 'watcher_failure',
        message: 'Gmail watcher failed to connect (3 retries)',
        severity: 'critical',
        timestamp: new Date(Date.now() - 7200000),
        resolved: true
      }
    ];

    allErrors = [...allErrors.map(e => ({
      ...e,
      severity: 'critical',
      resolved: false,
      message: e.parameters?.error || `${e.action_type} failed`
    })), ...systemErrors];

    updateErrorStats();
    renderErrors();
  } catch (err) {
    console.error('Error loading errors:', err);
  }
}

function updateErrorStats() {
  const critical = allErrors.filter(e => e.severity === 'critical' && !e.resolved).length;
  const warning = allErrors.filter(e => e.severity === 'warning' && !e.resolved).length;
  const resolved = allErrors.filter(e => e.resolved).length;

  document.getElementById('criticalErrorCount').textContent = critical;
  document.getElementById('warningErrorCount').textContent = warning;
  document.getElementById('resolvedErrorCount').textContent = resolved;
}

function filterErrors(filter) {
  currentErrorFilter = filter;
  renderErrors();
}

function renderErrors() {
  const container = document.getElementById('errorGrid');
  let filtered = allErrors;

  if (currentErrorFilter !== 'all') {
    if (currentErrorFilter === 'resolved') {
      filtered = allErrors.filter(e => e.resolved);
    } else {
      filtered = allErrors.filter(e => e.severity === currentErrorFilter && !e.resolved);
    }
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <i class="fas fa-check-circle" style="color: var(--accent-green); font-size: 2rem;"></i>
        <p>No ${currentErrorFilter === 'all' ? '' : currentErrorFilter} errors found</p>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(error => {
    const timeAgo = formatTimeAgo(error.timestamp);
    const icon = error.severity === 'critical' ? 'fa-fire' : 'fa-exclamation-triangle';

    return `
      <div class="error-card ${error.severity}">
        <div class="error-header">
          <div class="error-type">
            <i class="fas ${icon}"></i>
            ${escapeHtml(error.action_type || 'system_error')}
          </div>
          <div class="error-time">${timeAgo}</div>
        </div>
        <div class="error-message">${escapeHtml(error.message)}</div>
        <div class="error-actions">
          ${!error.resolved ? `
            <button class="btn btn-sm btn-success" onclick="resolveError('${error.id}')">
              <i class="fas fa-check"></i> Resolve
            </button>
            <button class="btn btn-sm btn-secondary" onclick="viewErrorDetails('${error.id}')">
              <i class="fas fa-info"></i> Details
            </button>
          ` : `
            <span style="color: var(--accent-green); font-size: 0.85rem;">
              <i class="fas fa-check"></i> Resolved
            </span>
          `}
        </div>
      </div>
    `;
  }).join('');
}

function resolveError(id) {
  const error = allErrors.find(e => e.id === id);
  if (error) {
    error.resolved = true;
    updateErrorStats();
    renderErrors();
    showToast('Error marked as resolved', 'success');
  }
}

function viewErrorDetails(id) {
  const error = allErrors.find(e => e.id === id);
  if (error) {
    const details = `
Type: ${error.action_type}
Severity: ${error.severity}
Message: ${error.message}
Time: ${error.timestamp}
Target: ${error.target || 'N/A'}
Parameters: ${JSON.stringify(error.parameters || {}, null, 2)}
    `.trim();
    openModal('Error Details', details);
  }
}

// ==================== ADVANCED SEARCH ====================

let currentSearchFilter = 'all';
let searchResults = [];

function setSearchFilter(filter) {
  currentSearchFilter = filter;

  // Update active state
  document.querySelectorAll('.search-filter').forEach(el => {
    el.classList.toggle('active', el.dataset.filter === filter);
  });

  // Re-run search if we have results
  if (searchResults.length > 0) {
    renderSearchResults(searchResults);
  }
}

async function performVaultSearch() {
  const query = document.getElementById('vaultSearchInput').value.trim();
  if (!query) {
    showToast('Please enter a search term', 'warning');
    return;
  }

  const container = document.getElementById('searchResults');
  container.innerHTML = `
    <div class="empty-state">
      <i class="fas fa-spinner fa-spin"></i>
      <p>Searching vault...</p>
    </div>
  `;

  try {
    // Get all folders
    const foldersRes = await fetch('/api/vault/folders');
    const folders = await foldersRes.json();

    // Search in relevant folders based on filter
    const foldersToSearch = currentSearchFilter === 'all'
      ? Object.keys(folders)
      : [currentSearchFilter === 'briefings' ? 'Briefings' :
         currentSearchFilter === 'logs' ? 'Logs' :
         currentSearchFilter.charAt(0).toUpperCase() + currentSearchFilter.slice(1) + '_Approval'];

    let allResults = [];

    for (const folder of foldersToSearch) {
      try {
        const folderRes = await fetch(`/api/vault/folder/${folder}`);
        const data = await folderRes.json();
        const files = data.files || [];

        // Search in filenames (we'd need to read content for full-text search)
        const matchingFiles = files.filter(file =>
          file.toLowerCase().includes(query.toLowerCase())
        );

        matchingFiles.forEach(file => {
          allResults.push({
            filename: file,
            folder: folder,
            match: file.toLowerCase().indexOf(query.toLowerCase())
          });
        });
      } catch (err) {
        console.error(`Error searching ${folder}:`, err);
      }
    }

    searchResults = allResults;

    if (searchResults.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <i class="fas fa-search-minus"></i>
          <p>No results found for "${escapeHtml(query)}"</p>
          <p style="font-size: 0.8rem; margin-top: 10px;">Try different keywords or filters</p>
        </div>
      `;
    } else {
      renderSearchResults(searchResults, query);
    }
  } catch (err) {
    console.error('Search error:', err);
    container.innerHTML = `
      <div class="empty-state">
        <i class="fas fa-exclamation-triangle" style="color: var(--accent-red);"></i>
        <p>Search failed. Please try again.</p>
      </div>
    `;
  }
}

function renderSearchResults(results, query = '') {
  const container = document.getElementById('searchResults');

  container.innerHTML = results.map(result => {
    const badge = getFileType(result.filename);
    const highlightedName = query
      ? result.filename.replace(new RegExp(`(${query})`, 'gi'), '<span class="search-highlight">$1</span>')
      : result.filename;

    return `
      <div class="search-result-item" onclick="viewFile('${result.folder}', '${result.filename.replace(/'/g, "\\'")}')">
        <div class="search-result-header">
          <div class="search-result-title">
            ${badge ? `<span class="file-badge ${badge}">${badge.replace('_', ' ')}</span>` : ''}
            ${highlightedName}
          </div>
          <div class="search-result-meta">${result.folder}</div>
        </div>
      </div>
    `;
  }).join('');
}

// ==================== RESOURCE MONITOR ====================

let resourceRefreshInterval = null;

async function loadResources() {
  try {
    const res = await fetch('/api/processes');
    const processes = await res.json();

    // Calculate resource usage
    const totalMemory = processes.reduce((sum, p) => sum + (p.monit?.memory || 0), 0);
    const avgCPU = processes.length > 0
      ? processes.reduce((sum, p) => sum + (p.monit?.cpu || 0), 0) / processes.length
      : 0;

    // Get system info (simplified)
    const systemResources = [
      {
        name: 'CPU Usage',
        value: avgCPU.toFixed(1),
        unit: '%',
        icon: 'fa-microchip',
        status: avgCPU > 80 ? 'high' : avgCPU > 50 ? 'medium' : 'low'
      },
      {
        name: 'Memory',
        value: (totalMemory / 1024).toFixed(1),
        unit: 'GB',
        icon: 'fa-memory',
        status: totalMemory > 4096 ? 'high' : totalMemory > 2048 ? 'medium' : 'low'
      },
      {
        name: 'Processes',
        value: processes.length,
        unit: 'running',
        icon: 'fa-server',
        status: 'low'
      },
      {
        name: 'Vault Size',
        value: '~150',
        unit: 'MB',
        icon: 'fa-hdd',
        status: 'low'
      }
    ];

    // Render resource cards
    const resourceGrid = document.getElementById('resourceGrid');
    resourceGrid.innerHTML = systemResources.map(resource => {
      const percentage = resource.unit === '%' ? resource.value :
                        resource.unit === 'GB' ? (resource.value / 16) * 100 :
                        resource.unit === 'running' ? (resource.value / 20) * 100 : 20;

      return `
        <div class="resource-card">
          <div class="resource-header">
            <div class="resource-title">
              <i class="fas ${resource.icon}"></i> ${resource.name}
            </div>
          </div>
          <div class="resource-value">${resource.value}<span style="font-size: 1rem; color: var(--text-secondary);">${resource.unit}</span></div>
          <div class="resource-bar">
            <div class="resource-fill ${resource.status}" style="width: ${Math.min(100, percentage)}%"></div>
          </div>
          <div class="resource-info">${percentage.toFixed(0)}% utilized</div>
        </div>
      `;
    }).join('');

    // Render process table
    const tableBody = document.getElementById('resourceProcessTable');
    tableBody.innerHTML = processes.slice(0, 10).map(p => {
      const cpu = (p.monit?.cpu || 0).toFixed(1);
      const memory = ((p.monit?.memory || 0) / 1024).toFixed(1);
      const status = p.pm2_env?.status || 'unknown';

      return `
        <tr>
          <td>
            <span style="font-weight: 500;">${p.name}</span>
            ${p.name.includes('watcher') || p.name.includes('monitor') ? '<span class="file-badge info" style="margin-left: 8px;">watcher</span>' : ''}
          </td>
          <td>${cpu}%</td>
          <td>${memory} MB</td>
          <td>
            <span class="status-${status === 'online' ? 'online' : 'stopped'}">${status}</span>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error('Error loading resources:', err);
  }
}

function toggleResourceRefresh() {
  const enabled = document.getElementById('autoRefreshResources').checked;

  if (resourceRefreshInterval) {
    clearInterval(resourceRefreshInterval);
    resourceRefreshInterval = null;
  }

  if (enabled) {
    resourceRefreshInterval = setInterval(loadResources, 5000);
  }
}

// Clear resource refresh when leaving section
const originalShowSection = showSection;
showSection = function(section) {
  if (section !== 'resources' && resourceRefreshInterval) {
    clearInterval(resourceRefreshInterval);
    resourceRefreshInterval = null;
    document.getElementById('autoRefreshResources').checked = false;
  }
  originalShowSection(section);
};

// ==================== TASK MANAGEMENT (KANBAN) ====================

let kanbanTasks = [];
let draggedTask = null;

// Sample tasks data
const sampleTasks = [
  { id: 1, title: 'Review pending emails', description: 'Check and process pending approval requests', status: 'todo', priority: 'high', tags: ['email', 'urgent'] },
  { id: 2, title: 'Generate weekly briefing', description: 'Create CEO briefing from vault data', status: 'todo', priority: 'medium', tags: ['reporting'] },
  { id: 3, title: 'Update social media queue', description: 'Review and schedule pending posts', status: 'progress', priority: 'low', tags: ['social'] },
  { id: 4, title: 'Fix calendar watcher', description: 'Debug authentication issues', status: 'done', priority: 'high', tags: ['bug', 'technical'] },
  { id: 5, title: 'Set up Xero integration', description: 'Configure MCP server for accounting', status: 'todo', priority: 'medium', tags: ['integration'] }
];

async function loadKanbanTasks() {
  // Load from backend API
  const loaded = await loadTasksFromBackend();
  if (!loaded) {
    // Use sample tasks if backend fails
    kanbanTasks = [...sampleTasks];
  }
  renderKanbanBoard();
}

function renderKanbanBoard() {
  const todoTasks = kanbanTasks.filter(t => t.status === 'todo');
  const progressTasks = kanbanTasks.filter(t => t.status === 'progress');
  const doneTasks = kanbanTasks.filter(t => t.status === 'done');

  document.getElementById('todoCount').textContent = todoTasks.length;
  document.getElementById('progressCount').textContent = progressTasks.length;
  document.getElementById('doneCount').textContent = doneTasks.length;

  renderKanbanColumn('kanbanTodo', todoTasks);
  renderKanbanColumn('kanbanProgress', progressTasks);
  renderKanbanColumn('kanbanDone', doneTasks);
}

function renderKanbanColumn(containerId, tasks) {
  const container = document.getElementById(containerId);

  if (tasks.length === 0) {
    container.innerHTML = '<div style="text-align: center; padding: 20px; color: var(--text-secondary);">No tasks</div>';
    return;
  }

  container.innerHTML = tasks.map(task => `
    <div class="kanban-task" draggable="true" ondragstart="dragTask(event, ${task.id})" ondragend="dragTaskEnd(event)">
      <div class="task-header">
        <div class="task-priority ${task.priority}"></div>
        <div class="task-tags">
          ${task.tags.slice(0, 2).map(tag => `<span class="task-tag">${tag}</span>`).join('')}
        </div>
      </div>
      <div class="task-title">${escapeHtml(task.title)}</div>
      ${task.description ? `<div class="task-description">${escapeHtml(task.description)}</div>` : ''}
    </div>
  `).join('');
}

function dragTask(event, taskId) {
  draggedTask = taskId;
  event.target.classList.add('dragging');
}

function dragTaskEnd(event) {
  event.target.classList.remove('dragging');
}

function allowDrop(event) {
  event.preventDefault();
}

function dropTask(event, status) {
  event.preventDefault();
  if (draggedTask) {
    const task = kanbanTasks.find(t => t.id === draggedTask);
    if (task) {
      task.status = status;
      renderKanbanBoard();
      showToast('Task moved to ' + status, 'success');
    }
    draggedTask = null;
  }
}

function showNewTaskModal(status = 'todo') {
  const title = prompt('Task title:');
  if (!title) return;

  const description = prompt('Task description (optional):') || '';
  const priority = prompt('Priority (low/medium/high):') || 'medium';

  const newTask = {
    id: Date.now(),
    title,
    description,
    status,
    priority: ['low', 'medium', 'high'].includes(priority) ? priority : 'medium',
    tags: []
  };

  kanbanTasks.push(newTask);
  renderKanbanBoard();
  showToast('Task created', 'success');
}

// ==================== SETTINGS PANEL ====================

let dashboardSettings = {
  theme: 'dark',
  dashboardRefresh: 10000,
  analyticsRefresh: 30000,
  emailNotifications: true,
  errorNotifications: true,
  soundEffects: false
};

function loadSettings() {
  // Load saved settings from localStorage
  const saved = localStorage.getItem('dashboardSettings');
  if (saved) {
    dashboardSettings = { ...dashboardSettings, ...JSON.parse(saved) };
  }

  // Apply settings to UI
  document.getElementById('dashboardRefresh').value = dashboardSettings.dashboardRefresh;
  document.getElementById('analyticsRefresh').value = dashboardSettings.analyticsRefresh;
  document.getElementById('emailNotifications').checked = dashboardSettings.emailNotifications;
  document.getElementById('errorNotifications').checked = dashboardSettings.errorNotifications;
  document.getElementById('soundEffects').checked = dashboardSettings.soundEffects;

  // Apply theme
  setTheme(dashboardSettings.theme);
}

function saveSettings() {
  dashboardSettings.dashboardRefresh = parseInt(document.getElementById('dashboardRefresh').value);
  dashboardSettings.analyticsRefresh = parseInt(document.getElementById('analyticsRefresh').value);
  dashboardSettings.emailNotifications = document.getElementById('emailNotifications').checked;
  dashboardSettings.errorNotifications = document.getElementById('errorNotifications').checked;
  dashboardSettings.soundEffects = document.getElementById('soundEffects').checked;

  localStorage.setItem('dashboardSettings', JSON.stringify(dashboardSettings));
  showToast('Settings saved successfully', 'success');
}

function setTheme(theme) {
  dashboardSettings.theme = theme;

  // Update UI
  document.querySelectorAll('.theme-option').forEach(el => {
    el.classList.toggle('active', el.dataset.theme === theme);
  });

  // Apply theme using actual CSS variable names
  const root = document.documentElement;

  if (theme === 'light') {
    // Light theme (using existing CSS variables)
    root.style.setProperty('--bg-primary', '#f8fafc');
    root.style.setProperty('--bg-secondary', '#f1f5f9');
    root.style.setProperty('--bg-tertiary', '#e2e8f0');
    root.style.setProperty('--card-bg', '#ffffff');
    root.style.setProperty('--card-border', '#e2e8f0');
    root.style.setProperty('--text-primary', '#1e293b');
    root.style.setProperty('--text-secondary', '#64748b');
  } else {
    // Dark theme (default values from CSS)
    root.style.setProperty('--bg-primary', '#0f172a');
    root.style.setProperty('--bg-secondary', '#1e293b');
    root.style.setProperty('--bg-tertiary', '#334155');
    root.style.setProperty('--card-bg', '#1e293b');
    root.style.setProperty('--card-border', 'rgba(255,255,255,0.1)');
    root.style.setProperty('--text-primary', '#f1f5f9');
    root.style.setProperty('--text-secondary', '#94a3b8');
  }

  saveSettings();
}

function clearCache() {
  if (confirm('Clear browser cache and reload?')) {
    localStorage.clear();
    location.reload(true);
  }
}

function exportSettings() {
  const dataStr = JSON.stringify(dashboardSettings, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(dataBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'dashboard-settings.json';
  link.click();
  showToast('Settings exported', 'success');
}

// ==================== AI CHAT INTERFACE ====================

let chatHistory = [];

function sendChatMessage() {
  const input = document.getElementById('chatInput');
  const message = input.value.trim();

  if (!message) return;

  // Add user message
  addChatMessage('user', message);
  input.value = '';

  // Simulate AI response
  setTimeout(() => {
    const response = generateAIResponse(message);
    addChatMessage('ai', response);
  }, 500 + Math.random() * 1000);
}

function sendChatSuggestion(text) {
  document.getElementById('chatInput').value = text;
  sendChatMessage();
}

function addChatMessage(type, content) {
  const container = document.getElementById('chatMessages');

  const messageDiv = document.createElement('div');
  messageDiv.className = `chat-message ${type}`;

  const avatar = type === 'ai'
    ? '<i class="fas fa-robot"></i>'
    : '<i class="fas fa-user"></i>';

  messageDiv.innerHTML = `
    <div class="chat-avatar">${avatar}</div>
    <div class="chat-bubble">${escapeHtml(content)}</div>
  `;

  container.appendChild(messageDiv);
  container.scrollTop = container.scrollHeight;

  chatHistory.push({ type, content, timestamp: new Date() });
}

function generateAIResponse(message) {
  const lower = message.toLowerCase();

  if (lower.includes('briefing') || lower.includes('report')) {
    return "I'll generate a weekly briefing for you. This will analyze your vault contents, review completed tasks, check pending approvals, and provide business insights. The briefing will be saved to your Briefings folder.";
  }

  if (lower.includes('attention') || lower.includes('pending') || lower.includes('review')) {
    const pendingCount = document.getElementById('pendingCount').textContent || '0';
    return `Based on the current dashboard status, you have ${pendingCount} items pending approval. I recommend reviewing the social media posts first, then checking any email action requests. Would you like me to filter them by priority?`;
  }

  if (lower.includes('health') || lower.includes('status')) {
    return "System health check:\n\n• Dashboard: Online\n• Watchers: Running\n• CPU Usage: Normal\n• Memory: Adequate\n\nAll systems are operating within normal parameters. No critical errors detected.";
  }

  if (lower.includes('help')) {
    return "I can help you with:\n\n• **Generating Reports** - Weekly briefings, CEO summaries\n• **Task Management** - Creating and organizing tasks\n• **Content Review** - Analyzing pending approvals\n• **System Status** - Checking health and resources\n• **Vault Analysis** - Searching and organizing files\n\nWhat would you like to do?";
  }

  // Default response
  const responses = [
    "I understand. Let me help you with that. Would you like me to analyze the relevant data from your vault?",
    "That's a great question. Based on your current system status, I can provide insights and recommendations.",
    "I'm processing your request. Let me check the vault for relevant information.",
    "I can assist with that. Would you like me to create a task or action item for this?"
  ];

  return responses[Math.floor(Math.random() * responses.length)];
}

// ==================== CALENDAR VIEW ====================

let currentCalendarDate = new Date();
let calendarEvents = [
  { date: new Date(), title: 'Team Standup', type: 'meeting' },
  { date: new Date(Date.now() + 86400000), title: 'Client Call', type: 'meeting' },
  { date: new Date(Date.now() + 172800000), title: 'Review Posts', type: 'task' },
  { date: new Date(Date.now() + 259200000), title: 'Pay Invoices', type: 'reminder' }
];

function loadCalendar() {
  renderCalendar();
}

function renderCalendar() {
  const year = currentCalendarDate.getFullYear();
  const month = currentCalendarDate.getMonth();

  // Update title
  const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December'];
  document.getElementById('calendarTitle').textContent = `${monthNames[month]} ${year}`;

  // Get first day of month and total days
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const daysInPrevMonth = new Date(year, month, 0).getDate();

  const container = document.getElementById('calendarDays');
  let html = '';

  const today = new Date();

  // Previous month days
  for (let i = firstDay - 1; i >= 0; i--) {
    const day = daysInPrevMonth - i;
    html += `<div class="calendar-day other-month">
      <div class="calendar-day-number">${day}</div>
    </div>`;
  }

  // Current month days
  for (let day = 1; day <= daysInMonth; day++) {
    const date = new Date(year, month, day);
    const isToday = date.toDateString() === today.toDateString();
    const dayEvents = calendarEvents.filter(e =>
      e.date.toDateString() === date.toDateString()
    );

    html += `<div class="calendar-day ${isToday ? 'today' : ''}" onclick="showDayDetails('${date.toISOString()}')">
      <div class="calendar-day-number">${day}</div>
      <div class="calendar-events">
        ${dayEvents.slice(0, 3).map(e =>
          `<div class="calendar-event-dot ${e.type}">${e.title}</div>`
        ).join('')}
        ${dayEvents.length > 3 ? `<div class="calendar-event-dot">+${dayEvents.length - 3} more</div>` : ''}
      </div>
    </div>`;
  }

  // Next month days
  const totalCells = Math.ceil((firstDay + daysInMonth) / 7) * 7;
  const remainingCells = totalCells - (firstDay + daysInMonth);
  for (let day = 1; day <= remainingCells; day++) {
    html += `<div class="calendar-day other-month">
      <div class="calendar-day-number">${day}</div>
    </div>`;
  }

  container.innerHTML = html;
}

function navigateCalendar(direction) {
  currentCalendarDate.setMonth(currentCalendarDate.getMonth() + direction);
  renderCalendar();
}

function changeCalendarView(view) {
  // For now, only month view is implemented
  showToast('Week view coming soon!', 'info');
}

function showDayDetails(dateStr) {
  const date = new Date(dateStr);
  const dayEvents = calendarEvents.filter(e =>
    e.date.toDateString() === date.toDateString()
  );

  if (dayEvents.length === 0) {
    showToast('No events on this day', 'info');
    return;
  }

  const eventsList = dayEvents.map(e =>
    `• ${e.title} (${e.type})`
  ).join('\n');

  openModal(`${date.toLocaleDateString()}`, eventsList || 'No events');
}

function showNewEventModal() {
  const title = prompt('Event title:');
  if (!title) return;

  const type = prompt('Event type (meeting/task/reminder):') || 'meeting';
  const dateStr = prompt('Event date (YYYY-MM-DD):');

  if (dateStr) {
    const date = new Date(dateStr);
    if (!isNaN(date.getTime())) {
      calendarEvents.push({ title, type: type.toLowerCase(), date });
      renderCalendar();
      showToast('Event created', 'success');
    } else {
      showToast('Invalid date format', 'error');
    }
  }
}

// Auto-refresh intervals
setInterval(updateSidebarStats, 10000);
setInterval(() => {
  if (currentSection === 'dashboard') loadDashboard();
}, 30000);

// Initial load
document.addEventListener('DOMContentLoaded', () => {
  showSection('dashboard');
  updateSidebarStats();
  setupKeyboardShortcuts();
  setupLazyLoading();

  // Load and apply saved settings (especially theme)
  loadSettings();
});

// ==================== KEYBOARD SHORTCUTS ====================

function setupKeyboardShortcuts() {
  document.addEventListener('keydown', (e) => {
    // Ignore if typing in input field
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
      // Allow Ctrl+K even in inputs
      if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        focusSearch();
      }
      return;
    }

    // Ctrl+K - Focus search
    if (e.ctrlKey && e.key === 'k') {
      e.preventDefault();
      focusSearch();
    }

    // Ctrl+R - Refresh current section
    if (e.ctrlKey && e.key === 'r') {
      e.preventDefault();
      refreshCurrent();
    }

    // Number keys 1-9 - Quick section switch
    if (e.key >= '1' && e.key <= '9') {
      const sections = ['dashboard', 'processes', 'watchers', 'pending', 'logs',
                       'analytics', 'files', 'activity', 'quick-actions'];
      const index = parseInt(e.key) - 1;
      if (sections[index]) {
        showSection(sections[index]);
      }
    }

    // N - Next section
    if (e.key === 'n' || e.key === 'N') {
      const sectionKeys = Object.keys(sectionTitles);
      const currentIndex = sectionKeys.indexOf(currentSection);
      const nextIndex = (currentIndex + 1) % sectionKeys.length;
      showSection(sectionKeys[nextIndex]);
    }

    // P - Previous section
    if (e.key === 'p' || e.key === 'P') {
      const sectionKeys = Object.keys(sectionTitles);
      const currentIndex = sectionKeys.indexOf(currentSection);
      const prevIndex = (currentIndex - 1 + sectionKeys.length) % sectionKeys.length;
      showSection(sectionKeys[prevIndex]);
    }

    // ESC - Close modal/dropdown
    if (e.key === 'Escape') {
      closeModal();
      document.getElementById('notificationDropdown')?.classList.remove('active');
    }

    // A - Approve (in pending section)
    if ((e.key === 'a' || e.key === 'A') && currentSection === 'pending') {
      approveAllPending();
    }

    // S - Settings
    if (e.key === 's' || e.key === 'S') {
      showSection('settings');
    }

    // T - Tasks
    if (e.key === 't' || e.key === 'T') {
      showSection('tasks');
    }

    // ? - Show keyboard shortcuts help
    if (e.key === '?') {
      showKeyboardShortcutsHelp();
    }
  });
}

function focusSearch() {
  if (currentSection === 'search') {
    getCachedElement('vaultSearchInput')?.focus();
  } else {
    showSection('search');
    setTimeout(() => getCachedElement('vaultSearchInput')?.focus(), 100);
  }
}

function showKeyboardShortcutsHelp() {
  const shortcuts = `
    <div style="line-height: 2;">
      <strong>Keyboard Shortcuts:</strong><br><br>
      <strong>Ctrl+K</strong> - Focus search<br>
      <strong>Ctrl+R</strong> - Refresh current section<br>
      <strong>1-9</strong> - Switch to section<br>
      <strong>N</strong> - Next section<br>
      <strong>P</strong> - Previous section<br>
      <strong>S</strong> - Settings<br>
      <strong>T</strong> - Tasks<br>
      <strong>A</strong> - Approve all (in Pending)<br>
      <strong>ESC</strong> - Close modal/dropdown<br>
      <strong>?</strong> - Show this help
    </div>
  `;
  openModal('Keyboard Shortcuts', shortcuts);
}

// ==================== LAZY LOADING ====================

function setupLazyLoading() {
  // Lazy load images
  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        if (img.dataset.src) {
          img.src = img.dataset.src;
          img.removeAttribute('data-src');
        }
        imageObserver.unobserve(img);
      }
    });
  });

  document.querySelectorAll('img[data-src]').forEach(img => {
    imageObserver.observe(img);
  });

  // Lazy load sections
  const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && entry.target.classList.contains('content-section')) {
        const section = entry.target.id.replace('section-', '');
        // Preload data for nearby sections
        preloadSectionData(section);
        sectionObserver.unobserve(entry.target);
      }
    });
  }, { rootMargin: '50px' });

  document.querySelectorAll('.content-section').forEach(section => {
    sectionObserver.observe(section);
  });
}

function preloadSectionData(section) {
  // Preload data for sections near current section
  const preloadMap = {
    'analytics': loadAnalytics,
    'activity': loadActivity,
    'files': loadFolders,
    'social-queue': loadSocialQueue,
    'errors': loadErrors
  };

  if (preloadMap[section] && currentSection !== section) {
    // Silently preload data
    preloadMap[section]().catch(() => {});
  }
}

// ==================== DATA PERSISTENCE ====================

async function saveTasksToBackend() {
  try {
    await fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(kanbanTasks)
    });
  } catch (err) {
    // If backend not available, save to localStorage
    localStorage.setItem('kanbanTasks', JSON.stringify(kanbanTasks));
  }
}

async function loadTasksFromBackend() {
  try {
    const res = await fetch('/api/tasks');
    if (res.ok) {
      kanbanTasks = await res.json();
      return true;
    }
  } catch (err) {
    // Fall back to localStorage
    const saved = localStorage.getItem('kanbanTasks');
    if (saved) {
      kanbanTasks = JSON.parse(saved);
      return true;
    }
  }
  return false;
}

// Auto-save tasks when modified
const originalDropTask = dropTask;
dropTask = function(event, status) {
  originalDropTask(event, status);
  saveTasksToBackend();
};

const originalShowNewTaskModal = showNewTaskModal;
showNewTaskModal = function(status = 'todo') {
  originalShowNewTaskModal(status);
  saveTasksToBackend();
};

// ==================== PERFORMANCE OPTIMIZATIONS ====================

// Debounce vault search
const debouncedVaultSearch = debounce(performVaultSearch, 300);

// Override search input to use debounced version
const vaultSearchInput = document.getElementById('vaultSearchInput');
if (vaultSearchInput) {
  vaultSearchInput.removeEventListener('keyup', null);
  vaultSearchInput.addEventListener('keyup', (e) => {
    if (e.key === 'Enter') {
      debouncedVaultSearch();
    }
  });
}

// Throttle scroll events
window.addEventListener('scroll', throttle(() => {
  // Close dropdowns on scroll
  document.getElementById('notificationDropdown')?.classList.remove('active');
}, 100));

// Optimize render functions with requestAnimationFrame
function optimizedRender(renderFn) {
  if ('requestIdleCallback' in window) {
    requestIdleCallback(renderFn);
  } else {
    requestAnimationFrame(renderFn);
  }
}

// Virtual scrolling for long lists
function createVirtualScrollList(containerId, items, renderItem) {
  const container = getCachedElement(containerId);
  if (!container) return;

  const ITEM_HEIGHT = 60;
  const VISIBLE_ITEMS = Math.ceil(container.clientHeight / ITEM_HEIGHT) + 2;
  const totalItems = items.length;

  let startIndex = 0;

  function render() {
    const endIndex = Math.min(startIndex + VISIBLE_ITEMS, totalItems);
    const visibleItems = items.slice(startIndex, endIndex);

    container.innerHTML = visibleItems.map(renderItem).join('');
  }

  container.addEventListener('scroll', throttle(() => {
    startIndex = Math.floor(container.scrollTop / ITEM_HEIGHT);
    optimizedRender(render);
  }, 16));

  render();
}
