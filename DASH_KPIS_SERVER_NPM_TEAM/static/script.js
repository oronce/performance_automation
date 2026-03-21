/**
 * KPI Dashboard - Frontend JavaScript
 * Handles date filtering, API calls, and chart rendering
 */

// Global state
let config = null;
let charts = {};
let currentView = 'hourly'; // 'hourly' or 'daily'
let currentSection = 'kpi'; // 'kpi' or 'packet-loss'
let packetLossCharts = {};
const MAX_DAYS = 10; // Also enforced on backend

// =============================================================================
// INITIALIZATION
// =============================================================================

const APP_PASSWORD = '123123';

document.addEventListener('DOMContentLoaded', async () => {
    // Check if already logged in
    if (sessionStorage.getItem('kpi_auth') === 'true') {
        hideLogin();
        initDashboard();
    } else {
        setupLogin();
    }
});

function setupLogin() {
    const loginBtn = document.getElementById('login-btn');
    const passwordInput = document.getElementById('login-password');
    const loginError = document.getElementById('login-error');

    loginBtn.addEventListener('click', checkPassword);
    passwordInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') checkPassword();
    });

    function checkPassword() {
        const pwd = passwordInput.value;
        if (pwd === APP_PASSWORD) {
            sessionStorage.setItem('kpi_auth', 'true');
            hideLogin();
            initDashboard();
        } else {
            loginError.textContent = 'Wrong password';
            passwordInput.value = '';
            passwordInput.focus();
        }
    }
}

function hideLogin() {
    document.getElementById('login-overlay').classList.add('hidden');
}

async function initDashboard() {
    try {
        // Load config from backend
        config = await fetchConfig();

        // Setup date inputs
        setupDateInputs();

        // Setup event listeners
        setupEventListeners();

        // Load default data
        await loadDefaultData();
    } catch (error) {
        showError('Failed to initialize dashboard: ' + error.message);
    }
}

// =============================================================================
// API CALLS
// =============================================================================

async function fetchConfig() {
    const response = await fetch('/api/config');
    if (!response.ok) throw new Error('Failed to load config');
    return response.json();
}

async function fetchDefaultDates() {
    const response = await fetch('/api/default-dates');
    if (!response.ok) throw new Error('Failed to load default dates');
    return response.json();
}

async function fetchKPIData(startDate, endDate, view = 'hourly') {
    const url = `/api/kpi-data?start_date=${startDate}&end_date=${endDate}&view=${view}`;
    const response = await fetch(url);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || 'Failed to fetch data');
    }

    return data;
}

// =============================================================================
// DATE HANDLING
// =============================================================================

function setupDateInputs() {
    const today = new Date();
    const maxDate = today.toISOString().split('T')[0];

    document.getElementById('start-date').max = maxDate;
    document.getElementById('end-date').max = maxDate;
}

function validateDateRange(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);

    if (isNaN(start.getTime()) || isNaN(end.getTime())) {
        return { valid: false, error: 'Invalid date format' };
    }

    if (start > end) {
        return { valid: false, error: 'Start date must be before end date' };
    }

    // Calculate days difference
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;

    // CRITICAL: Enforce 7 day maximum on frontend
    if (diffDays > MAX_DAYS) {
        return {
            valid: false,
            error: `Maximum ${MAX_DAYS} days allowed. You selected ${diffDays} days.`
        };
    }

    return { valid: true, days: diffDays };
}

function getDateRangeFromDays(days) {
    const today = new Date();
    const start = new Date(today);
    start.setDate(today.getDate() - (days - 1));

    return {
        startDate: start.toISOString().split('T')[0],
        endDate: today.toISOString().split('T')[0]
    };
}

// =============================================================================
// EVENT LISTENERS
// =============================================================================

function setupEventListeners() {
    // Section navigation buttons (KPI Dashboard / Packet Loss)
    document.querySelectorAll('.btn-section').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const section = e.target.dataset.section;
            await switchSection(section);
        });
    });

    // View toggle buttons (Hourly / Daily)
    document.querySelectorAll('.btn-toggle').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const view = e.target.dataset.view;
            currentView = view;

            // Update toggle button states
            document.querySelectorAll('.btn-toggle').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');

            // Reload data with current date range
            const startDate = document.getElementById('start-date').value;
            const endDate = document.getElementById('end-date').value;

            if (startDate && endDate) {
                await loadCurrentSection(startDate, endDate);
            }
        });
    });

    // Quick select buttons
    document.querySelectorAll('.btn-quick').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const days = parseInt(e.target.dataset.days);

            // Validate days limit (should always be valid for these buttons, but double-check)
            if (days > MAX_DAYS) {
                showError(`Maximum ${MAX_DAYS} days allowed`);
                return;
            }

            const { startDate, endDate } = getDateRangeFromDays(days);

            // Update date inputs
            document.getElementById('start-date').value = startDate;
            document.getElementById('end-date').value = endDate;

            // Highlight active button
            document.querySelectorAll('.btn-quick').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');

            // Load data
            await loadCurrentSection(startDate, endDate);
        });
    });

    // Apply filter button
    document.getElementById('apply-filter').addEventListener('click', async () => {
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;

        if (!startDate || !endDate) {
            showError('Please select both start and end dates');
            return;
        }

        // Validate date range
        const validation = validateDateRange(startDate, endDate);
        if (!validation.valid) {
            showError(validation.error);
            return;
        }

        // Clear quick button highlights
        document.querySelectorAll('.btn-quick').forEach(b => b.classList.remove('active'));

        // Load data
        await loadCurrentSection(startDate, endDate);
    });

    // Date input change - validate in real-time
    ['start-date', 'end-date'].forEach(id => {
        document.getElementById(id).addEventListener('change', () => {
            const startDate = document.getElementById('start-date').value;
            const endDate = document.getElementById('end-date').value;

            if (startDate && endDate) {
                const validation = validateDateRange(startDate, endDate);
                if (!validation.valid) {
                    showError(validation.error);
                } else {
                    clearError();
                }
            }
        });
    });
}

// =============================================================================
// DATA LOADING
// =============================================================================

async function loadDefaultData() {
    try {
        const defaults = await fetchDefaultDates();

        document.getElementById('start-date').value = defaults.start_date;
        document.getElementById('end-date').value = defaults.end_date;

        // Highlight the default days button
        const defaultBtn = document.querySelector(`.btn-quick[data-days="${defaults.default_days}"]`);
        if (defaultBtn) defaultBtn.classList.add('active');

        await loadData(defaults.start_date, defaults.end_date);
    } catch (error) {
        showError('Failed to load default data: ' + error.message);
    }
}

async function loadData(startDate, endDate) {
    showLoading(true);
    clearError();

    try {
        const result = await fetchKPIData(startDate, endDate, currentView);

        if (result.success && result.data) {
            updateCurrentRange(startDate, endDate, result.total_records);
            renderCharts(result.data);
        } else {
            showError('No data returned from server');
        }
    } catch (error) {
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

// =============================================================================
// CHART RENDERING
// =============================================================================

function renderCharts(data) {
    const container = document.getElementById('charts-container');
    container.innerHTML = '';

    // Destroy existing charts
    Object.values(charts).forEach(chart => chart.destroy());
    charts = {};

    if (!data || data.length === 0) {
        container.innerHTML = '<p class="no-data">No data available for the selected date range</p>';
        return;
    }

    // Create labels with separate date and time info for better x-axis display
    const isDaily = currentView === 'daily';
    const labelData = data.map(row => ({
        date: row.date,
        time: row.time || '',
        full: isDaily ? row.date : (row.time ? `${row.date} ${row.time}` : row.date)
    }));

    // Create charts for each KPI group
    Object.entries(config.kpi_groups).forEach(([chartTitle, chartConfig], index) => {
        // Handle both old format (array) and new format (object with columns/threshold)
        const kpiColumns = Array.isArray(chartConfig) ? chartConfig : chartConfig.columns;
        const threshold = Array.isArray(chartConfig) ? null : chartConfig.threshold;

        // Check if any of the KPI columns exist in the data
        const availableColumns = kpiColumns.filter(col => data[0].hasOwnProperty(col));

        if (availableColumns.length === 0) {
            console.warn(`No data for chart: ${chartTitle}`);
            return;
        }

        // Create chart container
        const chartDiv = document.createElement('div');
        chartDiv.className = 'chart-card';
        const thresholdInfo = threshold !== null ? `<span class="threshold-info">Threshold: ${threshold}</span>` : '';
        chartDiv.innerHTML = `
            <h3 class="chart-title">${chartTitle} ${thresholdInfo}</h3>
            <div class="chart-wrapper">
                <canvas id="chart-${index}"></canvas>
            </div>
        `;
        container.appendChild(chartDiv);

        // Prepare datasets
        const datasets = availableColumns.map((col, colIndex) => ({
            label: col.replace(/_/g, ' '),
            data: data.map(row => row[col] !== null ? row[col] : null),
            borderColor: config.colors[colIndex % config.colors.length],
            backgroundColor: config.colors[colIndex % config.colors.length] + '20',
            borderWidth: 2,
            fill: false,
            tension: 0.1,
            pointRadius: 2,
            pointHoverRadius: 5
        }));

        // Add threshold line if defined
        if (threshold !== null) {
            datasets.push({
                label: `Threshold (${threshold})`,
                data: data.map(() => threshold),
                borderColor: '#FFB347',
                backgroundColor: 'transparent',
                borderWidth: 2,
                borderDash: [10, 5],
                fill: false,
                pointRadius: 0,
                pointHoverRadius: 0
            });
        }

        // Create chart
        const ctx = document.getElementById(`chart-${index}`).getContext('2d');
        charts[`chart-${index}`] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labelData.map(l => l.full),
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 15
                        }
                    },
                    tooltip: {
                        callbacks: {
                            title: function(tooltipItems) {
                                // Show full date and time in tooltip
                                return tooltipItems[0].label;
                            },
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) label += ': ';
                                if (context.parsed.y !== null) {
                                    label += context.parsed.y.toFixed(2);
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: isDaily ? 'Date' : 'Date / Time'
                        },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45,
                            autoSkip: true,
                            maxTicksLimit: isDaily ? 10 : 24,
                            callback: function(value, idx) {
                                const current = labelData[idx];
                                if (!current) return '';

                                // For daily view, just show the date
                                if (isDaily) {
                                    return current.date;
                                }

                                // For hourly view, show date only when it changes
                                const prev = idx > 0 ? labelData[idx - 1] : null;

                                if (!prev || prev.date !== current.date) {
                                    // New date - show date and time
                                    return [current.date, current.time];
                                } else {
                                    // Same date - show only time
                                    return current.time;
                                }
                            }
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: chartTitle
                        },
                        beginAtZero: false
                    }
                }
            }
        });
    });
}

// =============================================================================
// UI HELPERS
// =============================================================================

function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'flex' : 'none';
    // Only toggle charts-container when on KPI section
    if (currentSection === 'kpi') {
        document.getElementById('charts-container').style.display = show ? 'none' : 'grid';
    }
}

function showError(message) {
    const errorEl = document.getElementById('error-message');
    errorEl.textContent = message;
    errorEl.style.display = 'inline';
}

function clearError() {
    const errorEl = document.getElementById('error-message');
    errorEl.textContent = '';
    errorEl.style.display = 'none';
}

function updateCurrentRange(startDate, endDate, totalRecords) {
    const rangeEl = document.getElementById('current-range');
    rangeEl.textContent = `Showing: ${startDate} to ${endDate} (${totalRecords} records)`;
}

// =============================================================================
// SECTION SWITCHING
// =============================================================================

async function switchSection(section) {
    currentSection = section;

    // Update section button states
    document.querySelectorAll('.btn-section').forEach(b => b.classList.remove('active'));
    document.querySelector(`.btn-section[data-section="${section}"]`).classList.add('active');

    // Show / hide sections
    document.getElementById('kpi-section').style.display          = section === 'kpi'           ? '' : 'none';
    document.getElementById('packet-loss-section').style.display  = section === 'packet-loss'   ? '' : 'none';
    document.getElementById('cssr-section').style.display         = section === 'cssr-analysis' ? '' : 'none';

    // Hide the shared filter (View Mode / Quick Select / Date Range) for CSSR Analysis
    // — it has its own independent filter inside the section
    document.querySelector('.filter-section').style.display = section === 'cssr-analysis' ? 'none' : '';
    document.getElementById('loading').style.display        = section === 'cssr-analysis' ? 'none' : '';

    // Load data for the newly visible section if dates are already set
    if (section === 'packet-loss') {
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;
        if (startDate && endDate) {
            await loadPacketLossData(startDate, endDate);
        }
    } else if (section === 'cssr-analysis') {
        // Initialise CA date pickers with defaults if empty
        initCaDateDefaults();
        loadCssrAnalysis();
    }
}

// Dispatch to the correct load function based on current section
async function loadCurrentSection(startDate, endDate) {
    if (currentSection === 'packet-loss') {
        await loadPacketLossData(startDate, endDate);
    } else if (currentSection === 'cssr-analysis') {
        // CSSR Analysis has its own independent date filter — do nothing here
        return;
    } else {
        await loadData(startDate, endDate);
    }
}

// =============================================================================
// PACKET LOSS API + RENDERING
// =============================================================================

async function fetchPacketLossData(startDate, endDate, view = 'hourly') {
    const url = `/api/packet-loss-data?start_date=${startDate}&end_date=${endDate}&view=${view}`;
    const response = await fetch(url);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || 'Failed to fetch packet loss data');
    }

    return data;
}

async function loadPacketLossData(startDate, endDate) {
    const container = document.getElementById('packet-loss-container');
    document.getElementById('loading').style.display = 'flex';
    container.style.display = 'none';
    clearError();

    try {
        const result = await fetchPacketLossData(startDate, endDate, currentView);

        if (result.success && result.data) {
            updateCurrentRange(startDate, endDate, result.total_records);
            renderPacketLossChart(result.data);
        } else {
            showError('No packet loss data returned from server');
        }
    } catch (error) {
        showError(error.message);
    } finally {
        document.getElementById('loading').style.display = 'none';
        container.style.display = 'grid';
    }
}

function renderPacketLossChart(data) {
    const container = document.getElementById('packet-loss-container');
    container.innerHTML = '';

    // Destroy existing packet loss charts
    Object.values(packetLossCharts).forEach(chart => chart.destroy());
    packetLossCharts = {};

    if (!data || data.length === 0) {
        container.innerHTML = '<p class="no-data">No data available for the selected date range</p>';
        return;
    }

    const isDaily = currentView === 'daily';

    // SQL returns uppercase DATE / TIME aliases — normalize defensively
    const normalized = data.map(row => ({
        date: row.DATE || row.date || '',
        time: row.TIME || row.time || '',
        cssr_ericsson: row.CSSR_ERICSSON !== undefined ? row.CSSR_ERICSSON : null,
        cssr_huawei: row.CSSR_HUAWEI !== undefined ? row.CSSR_HUAWEI : null,
        pl_count_ericsson: row.packet_loss_count_ericsson !== undefined ? row.packet_loss_count_ericsson : null,
        pl_count_huawei: row.packet_loss_count_huawei !== undefined ? row.packet_loss_count_huawei : null
    }));

    const labelData = normalized.map(row => ({
        date: row.date,
        time: row.time,
        full: isDaily ? row.date : (row.time ? `${row.date} ${row.time}` : row.date)
    }));

    // Shared chart options builder — same look for both charts
    function buildChartOptions(labelDataRef) {
        return {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { usePointStyle: true, padding: 15 }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) label += ': ';
                            if (context.parsed.y !== null) {
                                label += context.parsed.y.toFixed(2);
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: { display: true, text: isDaily ? 'Date' : 'Date / Time' },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                        autoSkip: true,
                        maxTicksLimit: isDaily ? 10 : 24,
                        callback: function(value, idx) {
                            const current = labelDataRef[idx];
                            if (!current) return '';
                            if (isDaily) return current.date;
                            const prev = idx > 0 ? labelDataRef[idx - 1] : null;
                            if (!prev || prev.date !== current.date) {
                                return [current.date, current.time];
                            }
                            return current.time;
                        }
                    }
                },
                yCSSR: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: { display: true, text: 'CSSR (%)' }
                },
                yPL: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: { display: true, text: 'Packet Loss Count' },
                    grid: { drawOnChartArea: false }
                }
            }
        };
    }

    // Helper to append a chart card and return its canvas context
    function addChartCard(title, canvasId) {
        const div = document.createElement('div');
        div.className = 'chart-card';
        div.innerHTML = `
            <h3 class="chart-title">${title}</h3>
            <div class="chart-wrapper" style="height:400px;">
                <canvas id="${canvasId}"></canvas>
            </div>
        `;
        container.appendChild(div);
        return document.getElementById(canvasId).getContext('2d');
    }

    const labels = labelData.map(l => l.full);

    // Threshold dataset reused in both charts (CSSR axis, left)
    const thresholdDataset = {
        type: 'line',
        label: 'Threshold (99)',
        data: normalized.map(() => 99),
        borderColor: '#e74c3c',
        backgroundColor: 'transparent',
        borderWidth: 2,
        borderDash: [10, 5],
        fill: false,
        pointRadius: 0,
        pointHoverRadius: 0,
        yAxisID: 'yCSSR',
        order: 0
    };

    // --- Chart 1: Ericsson ---
    const ctxE = addChartCard('CSSR Ericsson &amp; Packet Loss Failure Ericsson', 'pl-chart-ericsson');
    packetLossCharts['pl-chart-ericsson'] = new Chart(ctxE, {
        data: {
            labels,
            datasets: [
                {
                    type: 'line',
                    label: 'CSSR Ericsson (%)',
                    data: normalized.map(r => r.cssr_ericsson),
                    borderColor: '#3498db',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.1,
                    pointRadius: 2,
                    pointHoverRadius: 5,
                    yAxisID: 'yCSSR',
                    order: 1
                },
                {
                    type: 'bar',
                    label: 'Packet Loss Count Ericsson',
                    data: normalized.map(r => r.pl_count_ericsson),
                    backgroundColor: 'rgba(243, 156, 18, 0.7)',
                    borderColor: '#e67e22',
                    borderWidth: 1,
                    yAxisID: 'yPL',
                    order: 2
                },
                thresholdDataset
            ]
        },
        options: buildChartOptions(labelData)
    });

    // --- Chart 2: Huawei ---
    const ctxH = addChartCard('CSSR Huawei &amp; Packet Loss Failure Huawei', 'pl-chart-huawei');
    packetLossCharts['pl-chart-huawei'] = new Chart(ctxH, {
        data: {
            labels,
            datasets: [
                {
                    type: 'line',
                    label: 'CSSR Huawei (%)',
                    data: normalized.map(r => r.cssr_huawei),
                    borderColor: '#3498db',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.1,
                    pointRadius: 2,
                    pointHoverRadius: 5,
                    yAxisID: 'yCSSR',
                    order: 1
                },
                {
                    type: 'bar',
                    label: 'Packet Loss Count Huawei',
                    data: normalized.map(r => r.pl_count_huawei),
                    backgroundColor: 'rgba(243, 156, 18, 0.7)',
                    borderColor: '#e67e22',
                    borderWidth: 1,
                    yAxisID: 'yPL',
                    order: 2
                },
                thresholdDataset
            ]
        },
        options: buildChartOptions(labelData)
    });
}

// =============================================================================
// CSSR ANALYSIS SECTION
// =============================================================================

// State for CSSR Analysis
let caLevel     = 'cell_name';
let caTopN      = 50;
let caSortBy    = 'CSR_FAILURES';
let caPieCharts = {};
let caBarCharts = {};
let _lastBarE   = [];
let _lastBarH   = [];

// Map is only meaningful at cell or site level
const CA_MAP_LEVELS = ['cell_name', 'site_name'];

// Sort column mapping: key → { ericsson col, huawei col, higherIsBetter }
const SORT_COLS = {
    CSR_FAILURES: { e: 'CSR_FAILURES',                   h: 'CSR_FAILURES',                   higherIsBetter: false },
    CSSR:         { e: 'CSSR_ERICSSON',                  h: 'CSSR_HUAWEI',                    higherIsBetter: false }, // worst = lowest
    CDR:          { e: 'CDR_ERICSSON',                   h: 'CDR_HUAWEI',                     higherIsBetter: true  }, // worst = highest
    CBR:          { e: 'CBR_ERICSSON',                   h: 'CBR_HUAWEI',                     higherIsBetter: true  },
    TCH_CONG:     { e: 'TCH_CONGESTION_RATE_ERICSSON',   h: 'TCH_CONGESTION_RATE_HUAWEI',     higherIsBetter: true  },
    SDCCH_DROP:   { e: 'SDCCH_DROP_RATE_ERICSSON',       h: 'SDCCH_DROP_RATE_HUAWEI',         higherIsBetter: true  },
    SDCCH_CONG:   { e: 'SDCCH_CONGESTION_RATE_ERICSSON', h: 'SDCCH_CONGESTION_RATE_HUAWEI',   higherIsBetter: true  },
    TRAFFIC_VOIX: { e: 'TRAFFIC_VOIX_ERICSSON',          h: 'TRAFFIC_VOIX_HUAWEI',            higherIsBetter: false }, // worst = lowest traffic
};

function updateMapBtnVisibility() {
    const btn = document.getElementById('ca-map-btn');
    if (btn) btn.style.visibility = CA_MAP_LEVELS.includes(caLevel) ? '' : 'hidden';
}

function initCaDateDefaults() {
    const start     = document.getElementById('ca-start-date');
    const end       = document.getElementById('ca-end-date');
    const timeStart = document.getElementById('ca-time-start');
    const timeEnd   = document.getElementById('ca-time-end');
    if (!start.value || !end.value) {
        const today = new Date().toISOString().split('T')[0];
        start.value = today;
        end.value   = today;
    }
    if (!timeStart.value) timeStart.value = '00:00';
    if (!timeEnd.value)   timeEnd.value   = '23:00';
}

function setupCaEventListeners() {
    // Aggregation level toggle (uses .ca-btn — not .btn-toggle — to avoid conflict)
    document.querySelectorAll('.ca-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            caLevel = btn.dataset.caLevel;
            document.querySelectorAll('.ca-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            updateMapBtnVisibility();
            loadCssrAnalysis();
        });
    });

    // Auto-format time inputs as HH:MM while typing
    ['ca-time-start', 'ca-time-end'].forEach(id => {
        document.getElementById(id).addEventListener('input', e => {
            let v = e.target.value.replace(/[^0-9]/g, '');
            if (v.length >= 3) v = v.slice(0, 2) + ':' + v.slice(2, 4);
            e.target.value = v;
        });
    });

    document.getElementById('ca-apply').addEventListener('click', () => {
        loadCssrAnalysis();
    });

    document.querySelectorAll('[data-ca-quick]').forEach(btn => {
        btn.addEventListener('click', () => {
            const days = parseInt(btn.dataset.caQuick);
            const today = new Date();
            const end   = new Date(today);
            const start = new Date(today);

            if (days === 0) {
                // Today only
            } else if (days === 1) {
                // Yesterday only
                start.setDate(today.getDate() - 1);
                end.setDate(today.getDate() - 1);
            } else {
                // Last N days: start = N-1 days ago, end = today
                start.setDate(today.getDate() - (days - 1));
            }

            document.getElementById('ca-start-date').value = start.toISOString().split('T')[0];
            document.getElementById('ca-end-date').value   = end.toISOString().split('T')[0];

            document.querySelectorAll('[data-ca-quick]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            loadCssrAnalysis();
        });
    });

    document.getElementById('ca-top-n').addEventListener('change', e => {
        caTopN = parseInt(e.target.value) || 50;
        renderWorstBar('ca-bar-ericsson', _lastBarE, 'ERICSSON', caLevel, caBarCharts);
        renderWorstBar('ca-bar-huawei',   _lastBarH, 'HUAWEI',   caLevel, caBarCharts);
    });

    document.getElementById('ca-sort-by').addEventListener('change', e => {
        caSortBy = e.target.value;
        renderWorstBar('ca-bar-ericsson', _lastBarE, 'ERICSSON', caLevel, caBarCharts);
        renderWorstBar('ca-bar-huawei',   _lastBarH, 'HUAWEI',   caLevel, caBarCharts);
    });
}

async function fetchWorstCells(script, startDate, endDate, level, timeStart, timeEnd) {
    const params = new URLSearchParams({ script, start_date: startDate, end_date: endDate });
    if (level)     params.set('aggregation_level', level);
    if (timeStart) params.set('time_start', timeStart);
    if (timeEnd)   params.set('time_end',   timeEnd);

    const res  = await fetch('/api/worst-cells?' + params.toString());
    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || 'API error');
    return json.data || [];
}

async function loadCssrAnalysis() {
    const startDate = document.getElementById('ca-start-date').value;
    const endDate   = document.getElementById('ca-end-date').value;
    if (!startDate || !endDate) return;

    const diffDays = (new Date(endDate) - new Date(startDate)) / 86400000;
    if (diffDays < 0) { showError('Start date must be before end date'); return; }
    if (diffDays > 2) { showError('CSSR Analysis: max range is 3 days'); return; }

    const timeStart = document.getElementById('ca-time-start').value || null;
    const timeEnd   = document.getElementById('ca-time-end').value   || null;

    document.getElementById('ca-loading').style.display = 'flex';

    try {
        // Pie charts: no aggregation (network-level breakdown)
        const [pieE, pieH, barE, barH] = await Promise.all([
            fetchWorstCells('2g_ericsson_worst_cell', startDate, endDate, null,    timeStart, timeEnd),
            fetchWorstCells('2g_huawei_worst_cell',   startDate, endDate, null,    timeStart, timeEnd),
            fetchWorstCells('2g_ericsson_worst_cell', startDate, endDate, caLevel, timeStart, timeEnd),
            fetchWorstCells('2g_huawei_worst_cell',   startDate, endDate, caLevel, timeStart, timeEnd),
        ]);

        _lastBarE = barE;
        _lastBarH = barH;

        renderPieChart('ca-pie-ericsson', pieE, 'ERICSSON', caPieCharts);
        renderPieChart('ca-pie-huawei',   pieH, 'HUAWEI',   caPieCharts);
        renderWorstBar('ca-bar-ericsson', barE, 'ERICSSON', caLevel, caBarCharts);
        renderWorstBar('ca-bar-huawei',   barH, 'HUAWEI',   caLevel, caBarCharts);

    } catch (err) {
        showError('CSSR Analysis error: ' + err.message);
    } finally {
        document.getElementById('ca-loading').style.display = 'none';
    }
}

function renderPieChart(canvasId, rows, vendor, chartStore) {
    if (chartStore[canvasId]) { chartStore[canvasId].destroy(); delete chartStore[canvasId]; }

    if (!rows || rows.length === 0) return;
    const r = rows[0]; // single row when no aggregation

    const isEricsson = vendor === 'ERICSSON';
    let labels, values;

    if (isEricsson) {
        labels = ['SDCCH Cong', 'SDCCH Drops', 'TCH Assign Fails', 'TCH Drops'];
        values = [
            r['NUMBER_SDCONG']       || 0,
            r['NUMBER_OF_SDDROPS']   || 0,
            r['TCH_ASSIGN_FAILS']    || 0,
            r['NUMBER_OF_TCH_DROPS'] || 0,
        ];
    } else {
        labels = ['SDCCH Assign Fails', 'SDCCH Drops', 'TCH Assign Fails', 'TCH Drops'];
        values = [
            r['SDCCH_ASSIGN_FAILS'] || 0,
            r['SDCCH_DROPS']        || 0,
            r['TCH_ASSIGN_FAILS']   || 0,
            r['TCH_DROPS']          || 0,
        ];
    }

    const ctx = document.getElementById(canvasId).getContext('2d');
    chartStore[canvasId] = new Chart(ctx, {
        type: 'doughnut',
        plugins: [ChartDataLabels],
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: ['#e74c3c', '#f39c12', '#3498db', '#2ecc71'],
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 18, usePointStyle: true, pointStyleWidth: 10, font: { size: 12 } }
                },
                tooltip: {
                    callbacks: {
                        label: ctx => {
                            const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                            const pct   = total ? ((ctx.parsed / total) * 100).toFixed(1) : 0;
                            return ` ${ctx.label}: ${ctx.parsed.toLocaleString()} (${pct}%)`;
                        }
                    }
                },
                datalabels: {
                    color: '#fff',
                    font: { weight: 'bold', size: 11 },
                    textAlign: 'center',
                    textShadowBlur: 4,
                    textShadowColor: 'rgba(0,0,0,0.5)',
                    formatter: (value, ctx) => {
                        const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                        const pct   = total ? (value / total) * 100 : 0;
                        if (pct < 1) return '';
                        return pct.toFixed(1) + '%';
                    },
                    anchor: 'center',
                    align: 'center',
                    clamp: true,
                    overflow: 'hidden',
                }
            }
        }
    });
}

function renderWorstBar(canvasId, rows, vendor, level, chartStore) {
    if (chartStore[canvasId]) { chartStore[canvasId].destroy(); delete chartStore[canvasId]; }

    if (!rows || rows.length === 0) return;

    const isE      = vendor === 'ERICSSON';
    const sortCfg  = SORT_COLS[caSortBy] || SORT_COLS['CSR_FAILURES'];
    const sortCol  = isE ? sortCfg.e : sortCfg.h;

    // Sort client-side by selected KPI (worst first)
    const sorted = [...rows].sort((a, b) => {
        const va = parseFloat(a[sortCol]) || 0;
        const vb = parseFloat(b[sortCol]) || 0;
        // higherIsBetter: false → worst = highest → descending
        // higherIsBetter: true  → worst = lowest  → ascending
        return sortCfg.higherIsBetter ? va - vb : vb - va;
    });

    const topN = sorted.slice(0, caTopN);

    // Determine label column
    const labelCol = level === 'site_name'      ? 'site_name'
                   : level === 'commune'         ? 'commune'
                   : level === 'arrondissement'  ? 'arrondissement'
                   : level === 'departement'     ? 'departement'
                   : level === 'controller_name' ? 'controller_name'
                   : 'cell_name';

    const labels   = topN.map(r => r[labelCol] || r['cell_name'] || 'Unknown');
    const data     = topN.map(r => parseFloat(r[sortCol]) || 0);
    const sortLabel = document.getElementById('ca-sort-by')?.selectedOptions[0]?.text || caSortBy;

    // Dynamic height: 22px per bar
    const wrapEl = document.getElementById(canvasId.replace('ca-bar-', 'ca-bar-wrap-'));
    if (wrapEl) wrapEl.style.height = Math.max(400, topN.length * 22) + 'px';

    // Update chart titles
    const levelLabel = level.replace(/_/g, ' ');
    const titleId = canvasId === 'ca-bar-ericsson' ? 'ca-bar-title-ericsson' : 'ca-bar-title-huawei';
    const titleEl = document.getElementById(titleId);
    if (titleEl) titleEl.textContent = `${vendor === 'ERICSSON' ? 'Ericsson' : 'Huawei'} \u2014 Top ${caTopN} Worst ${levelLabel} by ${sortLabel}`;

    // Build tooltip extra lines per vendor
    const TOOLTIP_ROWS = isE ? [
        { col: 'CSR_FAILURES',                    label: 'CSR Failures'     },
        { col: 'CSSR_ERICSSON',                   label: 'CSSR (%)'         },
        { col: 'CDR_ERICSSON',                    label: 'CDR (%)'          },
        { col: 'CBR_ERICSSON',                    label: 'CBR (%)'          },
        { col: 'CELL_AVAILABILITY_RATE_ERICSSON', label: 'Cell Avail. (%)'  },
        { col: 'TCH_CONGESTION_RATE_ERICSSON',    label: 'TCH Cong. (%)'   },
        { col: 'SDCCH_DROP_RATE_ERICSSON',        label: 'SDCCH Drop (%)'  },
        { col: 'SDCCH_CONGESTION_RATE_ERICSSON',  label: 'SDCCH Cong. (%)' },
        { col: 'TRAFFIC_VOIX_ERICSSON',           label: 'Voice Traffic (Erl)' },
        { col: 'TRAFFIC_DATA_GB_ERICSSON',        label: 'Data Traffic (GB)'   },
    ] : [
        { col: 'CSR_FAILURES',                    label: 'CSR Failures'     },
        { col: 'CSSR_HUAWEI',                     label: 'CSSR (%)'         },
        { col: 'CDR_HUAWEI',                      label: 'CDR (%)'          },
        { col: 'CBR_HUAWEI',                      label: 'CBR (%)'          },
        { col: 'CELL_AVAILABILITY_RATE_HUAWEI',   label: 'Cell Avail. (%)'  },
        { col: 'TCH_CONGESTION_RATE_HUAWEI',      label: 'TCH Cong. (%)'   },
        { col: 'SDCCH_DROP_RATE_HUAWEI',          label: 'SDCCH Drop (%)'  },
        { col: 'SDCCH_CONGESTION_RATE_HUAWEI',    label: 'SDCCH Cong. (%)' },
        { col: 'TRAFFIC_VOIX_HUAWEI',             label: 'Voice Traffic (Erl)' },
        { col: 'HANDOVER_SUCCESS_RATE_HUAWEI',    label: 'Handover SR (%)'  },
    ];

    const ctx = document.getElementById(canvasId).getContext('2d');
    chartStore[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: sortLabel,
                data,
                backgroundColor: isE ? 'rgba(52,152,219,0.75)' : 'rgba(231,76,60,0.75)',
                borderColor:     isE ? '#2980b9'                : '#c0392b',
                borderWidth: 1,
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title: items => items.map(i => i.label),
                        label: item => {
                            const v = item.parsed.x;
                            return ` ${sortLabel}: ${typeof v === 'number' ? v.toLocaleString(undefined, { maximumFractionDigits: 2 }) : v}`;
                        },
                        afterBody: items => {
                            if (!items.length) return [];
                            const idx = items[0].dataIndex;
                            const row = topN[idx];
                            if (!row) return [];
                            return TOOLTIP_ROWS
                                .filter(({ col }) => col !== sortCol && row[col] != null && row[col] !== '')
                                .map(({ col, label }) => {
                                    const v = parseFloat(row[col]);
                                    return ` ${label}: ${isNaN(v) ? row[col] : v.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
                                });
                        }
                    }
                }
            },
            scales: {
                x: { title: { display: true, text: sortLabel } },
                y: { ticks: { font: { size: 11 } } }
            }
        }
    });
}

function openCssrMap() {
    const startDate = document.getElementById('ca-start-date').value;
    const endDate   = document.getElementById('ca-end-date').value;
    if (!startDate || !endDate) { showError('Select a date range first'); return; }

    if (!CA_MAP_LEVELS.includes(caLevel)) {
        showError('Map is only available for Cell and Site aggregation levels');
        return;
    }

    const timeStart = document.getElementById('ca-time-start').value || '';
    const timeEnd   = document.getElementById('ca-time-end').value   || '';

    const params = new URLSearchParams({
        start_date: startDate,
        end_date:   endDate,
        level:      caLevel,
    });
    if (timeStart) params.set('time_start', timeStart);
    if (timeEnd)   params.set('time_end',   timeEnd);

    window.open('/map?' + params.toString(), '_blank');
}

// Wire up CSSR Analysis listeners once DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    setupCaEventListeners();
});
