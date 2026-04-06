cat > frontend / script.js << 'EOF'
/**
 * AI VARANI - Incident Response System
 * Frontend JavaScript for the Incident Response Dashboard
 */

let currentStep = 0;
let totalReward = 0;
let episodeActive = false;
let actionHistoryList = [];

const statusColors = {
    'healthy': '#10b981',
    'degraded': '#f59e0b',
    'critical': '#ef4444',
    'failed': '#6b7280'
};

const statusIcons = {
    'healthy': '✓',
    'degraded': '⚠',
    'critical': '🔴',
    'failed': '💀'
};

let demoMode = true;
let demoIncident = {
    active: true,
    name: 'Database Connection Pool Exhaustion',
    severity: 'high',
    symptoms: [
        'High database connection wait times',
        'API Gateway latency increased by 300%',
        'Payment service error rate at 15%',
        'Connection timeout errors in user service'
    ],
    services: {
        'api_gateway': { status: 'degraded', health: 0.65, error_rate: 0.08, latency: 450, cpu: 65, memory: 55 },
        'auth_service': { status: 'healthy', health: 0.95, error_rate: 0.01, latency: 45, cpu: 35, memory: 40 },
        'user_service': { status: 'degraded', health: 0.55, error_rate: 0.12, latency: 320, cpu: 70, memory: 60 },
        'payment_service': { status: 'critical', health: 0.35, error_rate: 0.15, latency: 580, cpu: 85, memory: 75 },
        'database': { status: 'critical', health: 0.25, error_rate: 0.20, latency: 1200, cpu: 92, memory: 88 },
        'cache': { status: 'healthy', health: 0.90, error_rate: 0.02, latency: 25, cpu: 30, memory: 35 },
        'notification_service': { status: 'healthy', health: 0.92, error_rate: 0.01, latency: 65, cpu: 28, memory: 32 }
    },
    metrics: { avg_error_rate: 0.085, avg_latency: 412, total_throughput: 3450, degraded_count: 2, failed_count: 0 },
    logs: [
        '[ERROR] [database] Connection pool exhausted - new connections waiting',
        '[WARNING] [user_service] Timeout connecting to database after 5000ms',
        '[ERROR] [payment_service] Database query failed: connection refused',
        '[INFO] [api_gateway] Detected increased latency to downstream services',
        '[ERROR] [database] Connection timeout for pool-1-thread-45'
    ]
};

const scenarioSelect = document.getElementById('scenarioSelect');
const difficultySelect = document.getElementById('difficultySelect');
const initBtn = document.getElementById('initBtn');
const resetBtn = document.getElementById('resetBtn');
const actionBtn = document.getElementById('actionBtn');
const actionType = document.getElementById('actionType');
const targetService = document.getElementById('targetService');
const scaleFactor = document.getElementById('scaleFactor');
const logCount = document.getElementById('logCount');

const systemStatus = document.getElementById('systemStatus');
const stepCount = document.getElementById('stepCount');
const totalRewardDisplay = document.getElementById('totalReward');
const lastRewardDisplay = document.getElementById('lastReward');
const totalRewardDisplayBottom = document.getElementById('totalRewardDisplay');
const statusMessageDiv = document.getElementById('statusMessage');
const incidentTitle = document.querySelector('.incident-title');
const incidentSeverity = document.querySelector('.incident-severity');
const incidentDetails = document.getElementById('incidentDetails');
const symptomsList = document.getElementById('symptomsList');
const serviceCards = document.getElementById('serviceCards');
const logsContent = document.getElementById('logsContent');
const actionHistory = document.getElementById('actionHistory');
const avgErrorRate = document.getElementById('avgErrorRate');
const avgLatency = document.getElementById('avgLatency');
const totalThroughput = document.getElementById('totalThroughput');
const degradedCount = document.getElementById('degradedCount');
const failedCount = document.getElementById('failedCount');

const scaleParams = document.getElementById('scaleParams');
const logCountParams = document.getElementById('logCountParams');

function updateStatusMessage(message, isError = false) {
    if (statusMessageDiv) {
        statusMessageDiv.textContent = message;
        statusMessageDiv.className = isError ? 'error' : 'success';
        setTimeout(() => { if (statusMessageDiv.textContent === message) statusMessageDiv.className = ''; }, 5000);
    }
}

function updateSystemStatus(status) { if (systemStatus) systemStatus.textContent = status; }
function updateStepCount(step) { currentStep = step; if (stepCount) stepCount.textContent = step; }

function updateRewards(lastReward, total) {
    totalReward = total;
    if (totalRewardDisplay) totalRewardDisplay.textContent = total.toFixed(2);
    if (totalRewardDisplayBottom) totalRewardDisplayBottom.textContent = total.toFixed(2);
    if (lastRewardDisplay) {
        lastRewardDisplay.textContent = lastReward.toFixed(2);
        lastRewardDisplay.className = lastReward >= 0 ? 'reward-value positive' : 'reward-value negative';
    }
}

function updateIncidentSummary() {
    if (!incidentTitle || !incidentSeverity || !incidentDetails) return;
    if (!demoIncident.active) {
        incidentTitle.textContent = 'No Active Incident';
        incidentSeverity.textContent = 'None';
        incidentSeverity.className = 'incident-severity severity-none';
        incidentDetails.innerHTML = '<p>System is operating normally. No incidents detected.</p>';
        return;
    }
    incidentTitle.textContent = demoIncident.name;
    incidentSeverity.textContent = demoIncident.severity.toUpperCase();
    let severityClass = '';
    switch (demoIncident.severity) {
        case 'critical': severityClass = 'severity-critical'; break;
        case 'high': severityClass = 'severity-high'; break;
        case 'medium': severityClass = 'severity-medium'; break;
        case 'low': severityClass = 'severity-low'; break;
        default: severityClass = 'severity-none';
    }
    incidentSeverity.className = `incident-severity ${severityClass}`;
    incidentDetails.innerHTML = `<p><strong>Root Cause:</strong> Database connection pool exhausted</p><p><strong>Current Step:</strong> ${currentStep}</p>`;
}

function updateSymptoms() {
    if (!symptomsList) return;
    if (!demoIncident.active || demoIncident.symptoms.length === 0) {
        symptomsList.innerHTML = '<div class="symptom-item">No symptoms detected</div>';
        return;
    }
    symptomsList.innerHTML = demoIncident.symptoms.map(s => `<div class="symptom-item">⚠️ ${s}</div>`).join('');
}

function updateServiceCards() {
    if (!serviceCards) return;
    const entries = Object.entries(demoIncident.services);
    serviceCards.innerHTML = entries.map(([name, data]) => {
        const status = data.status;
        return `<div class="service-card" style="border-left-color: ${statusColors[status]}" onclick="selectService('${name}')">
            <div class="service-header"><span class="service-name">${statusIcons[status]} ${name.replace(/_/g, ' ').toUpperCase()}</span>
            <span class="service-status status-${status}">${status}</span></div>
            <div class="service-metrics"><span>💚 ${(data.health * 100).toFixed(0)}%</span>
            <span>📊 ${(data.error_rate * 100).toFixed(1)}% err</span>
            <span>⏱️ ${data.latency}ms</span><span>💻 ${data.cpu}% CPU</span></div></div>`;
    }).join('');
}

function updateMetrics() {
    if (!avgErrorRate || !avgLatency || !totalThroughput || !degradedCount || !failedCount) return;
    const m = demoIncident.metrics;
    avgErrorRate.textContent = `${(m.avg_error_rate * 100).toFixed(1)}%`;
    avgLatency.textContent = `${m.avg_latency}ms`;
    totalThroughput.textContent = `${m.total_throughput} req/s`;
    degradedCount.textContent = m.degraded_count;
    failedCount.textContent = m.failed_count;
}

function updateLogs() {
    if (!logsContent) return;
    const logs = demoIncident.logs;
    logsContent.innerHTML = logs.slice(-10).map(log => {
        let logClass = '';
        if (log.includes('ERROR')) logClass = 'error';
        else if (log.includes('WARNING')) logClass = 'warning';
        return `<div class="log-entry ${logClass}">${log}</div>`;
    }).join('');
}

function updateActionHistory() {
    if (!actionHistory) return;
    if (actionHistoryList.length === 0) {
        actionHistory.innerHTML = '<div class="history-entry">No actions taken yet</div>';
        return;
    }
    actionHistory.innerHTML = actionHistoryList.slice(-8).map(a => {
        const rewardClass = a.reward >= 0 ? 'positive' : 'negative';
        const rewardSymbol = a.reward >= 0 ? '+' : '';
        return `<div class="history-entry ${rewardClass}">Step ${a.step}: ${a.action} on ${a.target} → Reward: ${rewardSymbol}${a.reward.toFixed(1)}</div>`;
    }).join('');
}

function selectService(serviceName) { if (targetService) targetService.value = serviceName; updateStatusMessage(`Selected service: ${serviceName}`); }

function toggleActionParams() {
    if (!actionType) return;
    const action = actionType.value;
    if (scaleParams) scaleParams.style.display = action === 'scale_service' ? 'block' : 'none';
    if (logCountParams) logCountParams.style.display = action === 'inspect_logs' ? 'block' : 'none';
}

function executeAction() {
    if (!episodeActive) { updateStatusMessage('Please initialize environment first!', true); return; }
    const action = actionType ? actionType.value : 'inspect_logs';
    const target = targetService ? targetService.value : 'api_gateway';
    let reward = 0, resultMessage = '';

    if (action === 'inspect_logs' || action === 'inspect_metrics' || action === 'inspect_traces') {
        reward = 5;
        resultMessage = `Diagnostic info retrieved from ${target}`;
        updateStatusMessage(`📊 ${resultMessage} (+${reward})`);
    } else if (action === 'restart_service') {
        if (target === 'database') {
            reward = 50;
            resultMessage = `Restarted ${target} - Service recovering!`;
            updateStatusMessage(`✅ ${resultMessage} (+${reward})`);
            if (demoIncident.services[target]) {
                demoIncident.services[target].status = 'degraded';
                demoIncident.services[target].health = 0.55;
                demoIncident.services[target].error_rate = 0.10;
            }
        } else { reward = -10; resultMessage = `Restarted ${target} but it wasn't the root cause`; updateStatusMessage(`⚠️ ${resultMessage} (${reward})`, true); }
    } else if (action === 'mark_resolved') {
        reward = 200;
        episodeActive = false;
        resultMessage = `Incident marked as RESOLVED!`;
        updateStatusMessage(`🎉 ${resultMessage} (+${reward})`);
        updateSystemStatus('Resolved');
    } else if (action === 'scale_service') {
        let scaleVal = scaleFactor ? parseFloat(scaleFactor.value) : 1.5;
        if (target === 'database') { reward = 75; resultMessage = `Scaled ${target} by ${scaleVal}x - Performance improving!`; updateStatusMessage(`✅ ${resultMessage} (+${reward})`); if (demoIncident.services[target]) { demoIncident.services[target].status = 'degraded'; demoIncident.services[target].health = 0.60; } }
        else { reward = -5; resultMessage = `Scaled ${target} but minimal effect`; updateStatusMessage(`ℹ️ ${resultMessage} (${reward})`); }
    } else { reward = -5; resultMessage = `Action ${action} on ${target} had minimal effect`; updateStatusMessage(`ℹ️ ${resultMessage} (${reward})`); }

    currentStep++; totalReward += reward;
    actionHistoryList.unshift({ step: currentStep, action: action, target: target, reward: reward });
    updateStepCount(currentStep); updateRewards(reward, totalReward); updateActionHistory(); updateServiceCards(); updateMetrics(); updateLogs();
    demoIncident.logs.unshift(`[INFO] [system] Action: ${action} on ${target} - Reward: ${reward}`);
    if (demoIncident.logs.length > 20) demoIncident.logs.pop(); updateLogs();
    if (currentStep >= 50) { episodeActive = false; updateStatusMessage('Episode ended - Max steps reached'); updateSystemStatus('Episode Complete'); }
}

function initializeEnvironment() {
    const scenario = scenarioSelect ? scenarioSelect.value : 'random';
    const difficulty = difficultySelect ? difficultySelect.value : 'medium';
    updateStatusMessage(`Initializing environment with ${scenario} (${difficulty} difficulty)...`);
    currentStep = 0; totalReward = 0; episodeActive = true; actionHistoryList = [];

    if (scenario === 'database_slowdown') { demoIncident.name = 'Database Connection Pool Exhaustion'; demoIncident.severity = 'high'; demoIncident.symptoms = ['High database connection wait times', 'API Gateway latency increased by 300%', 'Payment service error rate at 15%']; }
    else if (scenario === 'auth_crash') { demoIncident.name = 'Authentication Service Memory Leak'; demoIncident.severity = 'critical'; demoIncident.symptoms = ['Auth service health check failing', 'Memory usage at 98%', 'OutOfMemoryError in session manager']; }
    else if (scenario === 'cache_failure') { demoIncident.name = 'Redis Cache Cluster Failure'; demoIncident.severity = 'medium'; demoIncident.symptoms = ['Cache hit rate dropped to 0%', 'User service latency increased by 150%', 'Split-brain detected in cache cluster']; }
    else { demoIncident.name = 'Network Congestion Incident'; demoIncident.severity = 'high'; demoIncident.symptoms = ['API Gateway response time > 5s', 'Packet loss detected', 'Connection timeouts to upstream services']; }
    demoIncident.active = true;

    for (const [name, service] of Object.entries(demoIncident.services)) {
        if (name === 'database' || name === 'payment_service') { service.status = 'critical'; service.health = 0.30; service.error_rate = 0.18; service.latency = 1200; }
        else if (name === 'api_gateway' || name === 'user_service') { service.status = 'degraded'; service.health = 0.60; service.error_rate = 0.08; service.latency = 450; }
        else { service.status = 'healthy'; service.health = 0.90; service.error_rate = 0.01; service.latency = 45; }
    }
    demoIncident.metrics = { avg_error_rate: 0.085, avg_latency: 412, total_throughput: 3450, degraded_count: 2, failed_count: 0 };
    demoIncident.logs.unshift(`[INFO] [system] Environment initialized with scenario: ${scenario} (${difficulty})`);
    demoIncident.logs.unshift(`[INFO] [system] Incident: ${demoIncident.name} - Severity: ${demoIncident.severity}`);
    if (demoIncident.logs.length > 20) demoIncident.logs = demoIncident.logs.slice(0, 20);
    updateIncidentSummary(); updateSymptoms(); updateServiceCards(); updateMetrics(); updateLogs(); updateActionHistory();
    updateStepCount(0); updateRewards(0, 0); updateSystemStatus('Active');
    updateStatusMessage(`✅ Environment ready! Incident active: ${demoIncident.name}`);
}

function resetEpisode() {
    if (!episodeActive && currentStep > 0) { initializeEnvironment(); }
    else { currentStep = 0; totalReward = 0; actionHistoryList = []; episodeActive = true; updateStepCount(0); updateRewards(0, 0); updateActionHistory(); updateStatusMessage('Episode reset. Ready for incident response!'); updateSystemStatus('Active'); }
}

function bindEvents() {
    if (initBtn) initBtn.addEventListener('click', initializeEnvironment);
    if (resetBtn) resetBtn.addEventListener('click', resetEpisode);
    if (actionBtn) actionBtn.addEventListener('click', executeAction);
    if (actionType) actionType.addEventListener('change', toggleActionParams);
}

function init() {
    bindEvents(); toggleActionParams();
    updateStatusMessage('Welcome to AI VARANI Incident Response System! Click Initialize to start.');
    updateSystemStatus('Ready');
    episodeActive = false;
    updateIncidentSummary(); updateSymptoms(); updateServiceCards(); updateMetrics(); updateLogs();
}

document.addEventListener('DOMContentLoaded', init);
EOF