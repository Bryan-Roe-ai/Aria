// QAI Control Center JavaScript

// Same-origin: the static UI is served by the FastAPI app itself, so all API
// calls are relative. (Previously hardcoded http://localhost:8000, which broke
// whenever the service was reached via any other host/port.)
const API_BASE = '';

// Persisted UI preferences
const STORAGE_KEYS = {
    theme: 'qai.theme',
    tab: 'qai.activeTab',
    provider: 'qai.chatProvider',
};

// Global state
let currentProvider = 'auto';
let chatHistory = [];

// ----------------------------------------------------------------------------
// Initialization
// ----------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    initializeTheme();
    initializeTabs();
    initializeForms();
    restoreProvider();
    checkServiceStatus();

    // Restore last active tab (defaults to dashboard).
    const savedTab = localStorage.getItem(STORAGE_KEYS.tab) || 'dashboard';
    switchTab(savedTab);

    // Refresh service status every 30 seconds.
    setInterval(checkServiceStatus, 30000);
});

// ----------------------------------------------------------------------------
// Helpers
// ----------------------------------------------------------------------------

// Escape user/server-provided strings before injecting into innerHTML (XSS-safe).
function esc(value) {
    if (value === null || value === undefined) return '';
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// Robust JSON fetch with HTTP-status checking and clear errors.
async function fetchJSON(path, options) {
    const response = await fetch(`${API_BASE}${path}`, options);
    let data = null;
    const text = await response.text();
    if (text) {
        try {
            data = JSON.parse(text);
        } catch (e) {
            data = null;
        }
    }
    if (!response.ok) {
        const detail = (data && (data.detail || data.error)) || response.statusText;
        throw new Error(`HTTP ${response.status}: ${detail}`);
    }
    return data;
}

// Toggle a button's loading spinner + disabled state.
function setLoading(el, isLoading) {
    if (!el) return;
    if (isLoading) {
        el.classList.add('is-loading');
        el.disabled = true;
    } else {
        el.classList.remove('is-loading');
        el.disabled = false;
    }
}

const TOAST_ICONS = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };

function showToast(message, type = 'info', timeout = 4000) {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML =
        `<span class="toast-icon">${esc(TOAST_ICONS[type] || 'ℹ')}</span>` +
        `<span class="toast-message">${esc(message)}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 300);
    }, timeout);
}

function emptyState(text) {
    return `<div class="empty-state">${esc(text)}</div>`;
}

// ----------------------------------------------------------------------------
// Theme
// ----------------------------------------------------------------------------
function initializeTheme() {
    const saved = localStorage.getItem(STORAGE_KEYS.theme);
    const prefersDark = window.matchMedia &&
        window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = saved || (prefersDark ? 'dark' : 'light');
    applyTheme(theme);

    const toggle = document.getElementById('themeToggle');
    if (toggle) {
        toggle.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme');
            applyTheme(current === 'dark' ? 'light' : 'dark');
        });
    }
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEYS.theme, theme);
    const toggle = document.getElementById('themeToggle');
    if (toggle) {
        toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
        toggle.setAttribute('aria-label',
            theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    }
}

// ----------------------------------------------------------------------------
// Tab Management
// ----------------------------------------------------------------------------
function initializeTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
}

function switchTab(tabName) {
    const panel = document.getElementById(tabName);
    if (!panel) return;

    document.querySelectorAll('.tab-btn').forEach(btn => {
        const active = btn.dataset.tab === tabName;
        btn.classList.toggle('active', active);
        btn.setAttribute('aria-selected', active ? 'true' : 'false');
    });

    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    panel.classList.add('active');

    localStorage.setItem(STORAGE_KEYS.tab, tabName);
    loadTabData(tabName);
}

function loadTabData(tabName) {
    switch (tabName) {
        case 'dashboard': loadDashboard(); break;
        case 'quantum': loadQuantumData(); break;
        case 'chat': loadChatData(); break;
        case 'training': loadTrainingData(); break;
    }
}

// ----------------------------------------------------------------------------
// Service Status
// ----------------------------------------------------------------------------
async function checkServiceStatus() {
    const indicator = document.getElementById('serviceStatus');
    const dot = indicator.querySelector('.status-dot');
    const text = indicator.querySelector('.status-text');
    try {
        const data = await fetchJSON('/health');
        if (data && data.status === 'healthy') {
            dot.classList.add('online');
            dot.classList.remove('offline');
            text.textContent = 'Online';
        } else {
            dot.classList.remove('online');
            dot.classList.add('offline');
            text.textContent = 'Error';
        }
    } catch (error) {
        dot.classList.remove('online');
        dot.classList.add('offline');
        text.textContent = 'Offline';
    }
}

// ----------------------------------------------------------------------------
// Dashboard
// ----------------------------------------------------------------------------
async function loadDashboard() {
    try {
        const data = await fetchJSON('/status');

        const boolRow = (label, ok) => `
            <div class="status-item">
                <span class="status-label">${esc(label)}</span>
                <span class="status-value ${ok ? 'success' : 'error'}">
                    ${ok ? '✓ Yes' : '✗ No'}
                </span>
            </div>`;

        document.getElementById('systemStatus').innerHTML = `
            <div class="status-item">
                <span class="status-label">Service</span>
                <span class="status-value success">${esc(data.service)}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Version</span>
                <span class="status-value">${esc(data.version)}</span>
            </div>
            ${boolRow('Quantum Enabled', data.quantum && data.quantum.enabled)}
            ${boolRow('Chat Enabled', data.chat && data.chat.enabled)}
            ${boolRow('Training Enabled', data.training && data.training.enabled)}
        `;

        let activityHtml = emptyState('No recent activity');
        if (data.quantum && data.quantum.recent_results && data.quantum.recent_results.length > 0) {
            activityHtml = data.quantum.recent_results.map(result => `
                <div class="result-item">
                    <strong>Quantum:</strong> ${esc(result.dataset)} -
                    <span class="accuracy">${(Number(result.accuracy) * 100).toFixed(1)}%</span> accuracy
                    <br><small>${esc(result.backend)} - ${esc(result.timestamp)}</small>
                </div>
            `).join('');
        }
        document.getElementById('recentActivity').innerHTML = activityHtml;

        addLog('Dashboard loaded successfully', 'success');
    } catch (error) {
        document.getElementById('systemStatus').innerHTML = emptyState('Unable to load status');
        document.getElementById('recentActivity').innerHTML = emptyState('Unable to load activity');
        addLog(`Dashboard load error: ${error.message}`, 'error');
        showToast('Failed to load dashboard', 'error');
    }
}

// ----------------------------------------------------------------------------
// Quantum AI
// ----------------------------------------------------------------------------
async function loadQuantumData() {
    try {
        const datasets = await fetchJSON('/quantum/datasets');
        const datasetSelect = document.getElementById('quantumDataset');
        datasetSelect.innerHTML = '<option value="">Select dataset…</option>' +
            (datasets || []).map(d =>
                `<option value="${esc(d.name)}">${esc(d.name)}</option>`).join('');

        const status = await fetchJSON('/quantum/status');
        document.getElementById('quantumStatus').innerHTML = `
            <div class="status-item">
                <span class="status-label">Backend</span>
                <span class="status-value">${esc(status.backend)}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Azure Connected</span>
                <span class="status-value ${status.azure_connected ? 'success' : 'error'}">
                    ${status.azure_connected ? '✓ Yes' : '✗ No'}
                </span>
            </div>
            <div class="status-item">
                <span class="status-label">Available Backends</span>
                <span class="status-value">${esc((status.available_backends || []).length)}</span>
            </div>
        `;

        document.getElementById('quantumResults').innerHTML =
            (status.recent_results && status.recent_results.length > 0)
                ? status.recent_results.map(r => `
                    <div class="result-item">
                        <strong>${esc(r.dataset)}</strong><br>
                        Accuracy: <span class="accuracy">${(Number(r.accuracy) * 100).toFixed(1)}%</span><br>
                        <small>${esc(r.backend)} - ${esc(r.timestamp)}</small>
                    </div>
                `).join('')
                : emptyState('No results yet');

        document.getElementById('quantumAutorunJobs').innerHTML =
            emptyState('Available jobs will appear here');

        addLog('Quantum data loaded', 'info');
    } catch (error) {
        document.getElementById('quantumStatus').innerHTML = emptyState('Unable to load quantum status');
        addLog(`Quantum load error: ${error.message}`, 'error');
        showToast('Failed to load quantum data', 'error');
    }
}

// ----------------------------------------------------------------------------
// Chat
// ----------------------------------------------------------------------------
async function loadChatData() {
    try {
        const data = await fetchJSON('/chat/status');

        document.getElementById('chatProviders').innerHTML =
            Object.entries(data.providers || {}).map(([name, info]) => `
                <div class="status-item">
                    <span class="status-label">${esc(name.toUpperCase())}</span>
                    <span class="status-value ${info.available ? 'success' : 'error'}">
                        ${info.available ? '✓ Available' : '✗ Unavailable'}
                        ${info.cost ? ` (${esc(info.cost)})` : ''}
                    </span>
                </div>
            `).join('') || emptyState('No providers reported');

        document.getElementById('chatStatus').innerHTML = `
            <div class="status-item">
                <span class="status-label">Default Provider</span>
                <span class="status-value">${esc(data.default_provider)}</span>
            </div>
        `;

        document.getElementById('chatHistory').innerHTML =
            (data.recent_conversations && data.recent_conversations.length > 0)
                ? data.recent_conversations.map(conv => `
                    <div class="result-item">
                        <strong>${esc(conv.file)}</strong><br>
                        ${esc(conv.message_count)} messages<br>
                        <small>${esc(conv.preview)}</small>
                    </div>
                `).join('')
                : emptyState('No conversations yet');

        addLog('Chat data loaded', 'info');
    } catch (error) {
        document.getElementById('chatStatus').innerHTML = emptyState('Unable to load chat status');
        addLog(`Chat load error: ${error.message}`, 'error');
        showToast('Failed to load chat data', 'error');
    }
}

// ----------------------------------------------------------------------------
// Training
// ----------------------------------------------------------------------------
async function loadTrainingData() {
    try {
        const datasets = await fetchJSON('/training/datasets');

        const loraSelect = document.getElementById('loraDataset');
        loraSelect.innerHTML = '<option value="">Select dataset…</option>';
        if (datasets.chat && datasets.chat.length > 0) {
            datasets.chat.forEach(ds => {
                const opt = document.createElement('option');
                opt.value = `../../datasets/chat/${ds}`;
                opt.textContent = ds;
                loraSelect.appendChild(opt);
            });
        }

        const status = await fetchJSON('/training/status');

        document.getElementById('trainingStatus').innerHTML = `
            <div class="status-item">
                <span class="status-label">System</span>
                <span class="status-value success">Ready</span>
            </div>
        `;

        const adapter = status.lora_adapter || {};
        document.getElementById('loraAdapterStatus').innerHTML = adapter.available
            ? `
                <div class="status-item">
                    <span class="status-label">Status</span>
                    <span class="status-value success">✓ Available</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Model</span>
                    <span class="status-value">${esc(adapter.model || 'N/A')}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Rank</span>
                    <span class="status-value">${esc(adapter.rank || 'N/A')}</span>
                </div>
            `
            : emptyState('No adapter trained yet');

        const jobs = await fetchJSON('/training/autotrain/jobs');
        const jobSelect = document.getElementById('autotrainJob');
        jobSelect.innerHTML = '<option value="">Select job…</option>' +
            ((jobs.jobs || []).map(job =>
                `<option value="${esc(job)}">${esc(job)}</option>`).join(''));

        const atJobs = (status.orchestrators && status.orchestrators.autotrain &&
            status.orchestrators.autotrain.jobs) || {};
        document.getElementById('autotrainStatus').innerHTML =
            Object.keys(atJobs).length > 0
                ? Object.entries(atJobs).map(([name, job]) => `
                    <div class="job-item">
                        <span><strong>${esc(name)}</strong> - ${esc(job.status || 'unknown')}</span>
                    </div>
                `).join('')
                : emptyState('No jobs run yet');

        const dsSection = (label, items, cls) => `
            <h4>${esc(label)} (${(items || []).length})</h4>
            <div class="dataset-grid">
                ${(items || []).map(d =>
                    `<div class="dataset-item ${cls}">${esc(d)}</div>`).join('')}
            </div>`;
        document.getElementById('datasetList').innerHTML =
            dsSection('Quantum', datasets.quantum, 'quantum') +
            dsSection('Chat', datasets.chat, 'chat') +
            dsSection('Vision', datasets.vision, 'vision');

        addLog('Training data loaded', 'info');
    } catch (error) {
        document.getElementById('trainingStatus').innerHTML = emptyState('Unable to load training status');
        addLog(`Training load error: ${error.message}`, 'error');
        showToast('Failed to load training data', 'error');
    }
}

// ----------------------------------------------------------------------------
// Form Handlers
// ----------------------------------------------------------------------------
function initializeForms() {
    document.getElementById('quantumTrainForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await trainQuantumClassifier(e.submitter || e.target.querySelector('[type="submit"]'));
    });

    document.getElementById('loraTrainForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await trainLoRA(e.submitter || e.target.querySelector('[type="submit"]'));
    });

    document.getElementById('chatForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await sendChatMessage();
    });

    document.getElementById('chatProvider').addEventListener('change', (e) => {
        currentProvider = e.target.value;
        localStorage.setItem(STORAGE_KEYS.provider, currentProvider);
    });
}

function restoreProvider() {
    const saved = localStorage.getItem(STORAGE_KEYS.provider);
    if (saved) {
        const select = document.getElementById('chatProvider');
        if (select) {
            select.value = saved;
            currentProvider = saved;
        }
    }
}

async function trainQuantumClassifier(btn) {
    const dataset = document.getElementById('quantumDataset').value;
    const n_qubits = parseInt(document.getElementById('quantumQubits').value, 10);
    const n_layers = parseInt(document.getElementById('quantumLayers').value, 10);
    const epochs = parseInt(document.getElementById('quantumEpochs').value, 10);
    const backend = document.getElementById('quantumBackend').value;

    if (!dataset) {
        showToast('Please select a dataset', 'warning');
        addLog('Please select a dataset', 'error');
        return;
    }

    addLog(`Starting quantum training: ${dataset}`, 'info');
    setLoading(btn, true);
    try {
        const result = await fetchJSON('/quantum/train', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ dataset, n_qubits, n_layers, epochs, backend })
        });
        if (result.success) {
            addLog('Quantum training started successfully!', 'success');
            showToast('Quantum training started', 'success');
            setTimeout(() => loadQuantumData(), 2000);
        } else {
            const msg = result.stderr || result.error || 'Unknown error';
            addLog(`Training error: ${msg}`, 'error');
            showToast('Quantum training failed', 'error');
        }
    } catch (error) {
        addLog(`Request failed: ${error.message}`, 'error');
        showToast('Request failed', 'error');
    } finally {
        setLoading(btn, false);
    }
}

async function trainLoRA(btn) {
    const dataset = document.getElementById('loraDataset').value;
    const max_train_samples = parseInt(document.getElementById('loraTrainSamples').value, 10);
    const max_eval_samples = parseInt(document.getElementById('loraEvalSamples').value, 10);
    const epochs = parseInt(document.getElementById('loraEpochs').value, 10);

    if (!dataset) {
        showToast('Please select a dataset', 'warning');
        addLog('Please select a dataset', 'error');
        return;
    }

    addLog(`Starting LoRA training on ${dataset}`, 'info');
    setLoading(btn, true);
    try {
        const result = await fetchJSON('/training/lora', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ dataset, max_train_samples, max_eval_samples, epochs })
        });
        if (result.success) {
            addLog('LoRA training started successfully!', 'success');
            showToast('LoRA training started', 'success');
            setTimeout(() => loadTrainingData(), 2000);
        } else {
            const msg = result.stderr || result.error || 'Unknown error';
            addLog(`Training error: ${msg}`, 'error');
            showToast('LoRA training failed', 'error');
        }
    } catch (error) {
        addLog(`Request failed: ${error.message}`, 'error');
        showToast('Request failed', 'error');
    } finally {
        setLoading(btn, false);
    }
}

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const sendBtn = document.getElementById('chatSendBtn');
    const message = input.value.trim();
    if (!message) return;

    addChatMessage(message, 'user');
    input.value = '';
    setLoading(sendBtn, true);
    const typing = showTypingIndicator();

    try {
        const provider = currentProvider === 'auto' ? null : currentProvider;
        const result = await fetchJSON('/chat/message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, provider })
        });
        removeTypingIndicator(typing);
        if (result.success) {
            addChatMessage(result.response, 'assistant');
            addLog(`Chat response from ${result.provider}`, 'info');
        } else {
            const msg = result.error || 'Unknown error';
            addChatMessage('Error: ' + msg, 'system');
            addLog(`Chat error: ${msg}`, 'error');
            showToast('Chat request failed', 'error');
        }
    } catch (error) {
        removeTypingIndicator(typing);
        addChatMessage('Error: ' + error.message, 'system');
        addLog(`Chat request failed: ${error.message}`, 'error');
        showToast('Chat request failed', 'error');
    } finally {
        setLoading(sendBtn, false);
        input.focus();
    }
}

function addChatMessage(content, role) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;
    messageDiv.textContent = content; // textContent => XSS-safe
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function showTypingIndicator() {
    const messagesDiv = document.getElementById('chatMessages');
    const el = document.createElement('div');
    el.className = 'chat-message assistant typing';
    el.innerHTML = '<span class="typing-dot"></span>' +
        '<span class="typing-dot"></span><span class="typing-dot"></span>';
    messagesDiv.appendChild(el);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return el;
}

function removeTypingIndicator(el) {
    if (el && el.parentNode) el.parentNode.removeChild(el);
}

async function runAutoTrain(dryRun) {
    const job = document.getElementById('autotrainJob').value;
    if (!job) {
        showToast('Please select a job', 'warning');
        addLog('Please select a job', 'error');
        return;
    }

    addLog(`Running AutoTrain job: ${job} ${dryRun ? '(dry run)' : ''}`, 'info');
    try {
        const result = await fetchJSON('/training/autotrain', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ job_name: job, dry_run: dryRun })
        });
        if (result.success) {
            addLog('AutoTrain job completed successfully!', 'success');
            showToast(dryRun ? 'Dry run completed' : 'AutoTrain job completed', 'success');
            setTimeout(() => loadTrainingData(), 2000);
        } else {
            const msg = result.stderr || result.error || 'Unknown error';
            addLog(`AutoTrain error: ${msg}`, 'error');
            showToast('AutoTrain job failed', 'error');
        }
    } catch (error) {
        addLog(`Request failed: ${error.message}`, 'error');
        showToast('Request failed', 'error');
    }
}

// ----------------------------------------------------------------------------
// Quick Actions
// ----------------------------------------------------------------------------
function quickAction(action) {
    switch (action) {
        case 'quantum': switchTab('quantum'); break;
        case 'chat': switchTab('chat'); break;
        case 'training': switchTab('training'); break;
    }
}

function refreshStatus() {
    addLog('Refreshing status…', 'info');
    checkServiceStatus();
    loadDashboard();
    showToast('Status refreshed', 'info', 2000);
}

// ----------------------------------------------------------------------------
// Logging
// ----------------------------------------------------------------------------
function addLog(message, type = 'info') {
    const logOutput = document.getElementById('logOutput');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    const timestamp = new Date().toLocaleTimeString();
    entry.textContent = `[${timestamp}] ${message}`;
    logOutput.appendChild(entry);
    logOutput.scrollTop = logOutput.scrollHeight;
}

function clearLogs() {
    document.getElementById('logOutput').innerHTML = '';
    addLog('Logs cleared', 'info');
}

function refreshLogs() {
    addLog('Logs refreshed', 'info');
}
