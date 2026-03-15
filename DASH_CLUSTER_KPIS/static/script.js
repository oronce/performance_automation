/**
 * Cluster KPI Dashboard — Frontend JavaScript
 */

const APP_PASSWORD = '123123';

// Colors for compare mode (up to 7 days)
const DAY_COLORS = [
    '#3498db', // blue
    '#e74c3c', // red
    '#2ecc71', // green
    '#f39c12', // orange
    '#9b59b6', // purple
    '#1abc9c', // teal
    '#e67e22', // dark orange
];

let config        = null;
let charts        = {};
let currentView   = 'hourly';   // 'hourly' | 'daily' | 'compare'
let currentBatch  = 'all';
let dateMode      = 'range';    // 'range' | 'specific'
let specificDates = [];         // array of 'YYYY-MM-DD' strings
let compareDays   = [];         // array of 'YYYY-MM-DD' strings
let popupBatch    = null;       // which batch the popup is for
let popupTimer    = null;

// =============================================================================
// INIT
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
    if (sessionStorage.getItem('cluster_kpi_auth') === 'true') {
        hideLogin();
        initDashboard();
    } else {
        setupLogin();
    }
});

function setupLogin() {
    const btn   = document.getElementById('login-btn');
    const input = document.getElementById('login-password');
    const err   = document.getElementById('login-error');

    function tryLogin() {
        if (input.value === APP_PASSWORD) {
            sessionStorage.setItem('cluster_kpi_auth', 'true');
            hideLogin();
            initDashboard();
        } else {
            err.textContent = 'Wrong password';
            input.value = '';
            input.focus();
        }
    }
    btn.addEventListener('click', tryLogin);
    input.addEventListener('keypress', e => { if (e.key === 'Enter') tryLogin(); });
}

function hideLogin() {
    document.getElementById('login-overlay').classList.add('hidden');
}

async function initDashboard() {
    try {
        config = await fetchConfig();

        // Show cell counts on batch buttons
        Object.entries(config.batches).forEach(([key, info]) => {
            const el = document.getElementById(`count-${key}`);
            if (el && info.count !== null) el.textContent = `(${info.count})`;
        });

        setupClusterPopup();
        setupDateInputs();
        setupEventListeners();
        initCompareRows();
        await loadDefaultData();
    } catch (err) {
        showError('Failed to initialize: ' + err.message);
    }
}

// =============================================================================
// API
// =============================================================================

async function fetchConfig() {
    const res = await fetch('/api/config');
    if (!res.ok) throw new Error('Failed to load config');
    return res.json();
}

async function fetchDefaultDates() {
    const res = await fetch('/api/default-dates');
    if (!res.ok) throw new Error('Failed to load default dates');
    return res.json();
}

async function fetchKPIData(params) {
    const qs = new URLSearchParams(params).toString();
    const res = await fetch(`/api/kpi-data?${qs}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Failed to fetch data');
    return data;
}

// =============================================================================
// DATE HELPERS
// =============================================================================

function setupDateInputs() {
    const today = new Date().toISOString().split('T')[0];
    ['start-date', 'end-date', 'add-specific-date'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.max = today;
    });
}

function validateDateRange(startDate, endDate) {
    const start = new Date(startDate);
    const end   = new Date(endDate);
    if (isNaN(start) || isNaN(end)) return { valid: false, error: 'Invalid date format' };
    if (start > end)                 return { valid: false, error: 'Start date must be before end date' };
    const days = Math.ceil(Math.abs(end - start) / 86400000) + 1;
    const max  = config ? config.max_days : 30;
    if (days > max) return { valid: false, error: `Maximum ${max} days allowed. You selected ${days} days.` };
    return { valid: true, days };
}

function getDateRangeFromDays(days) {
    const today = new Date();
    const start = new Date(today);
    start.setDate(today.getDate() - (days - 1));
    return {
        startDate: start.toISOString().split('T')[0],
        endDate:   today.toISOString().split('T')[0]
    };
}

// =============================================================================
// CLUSTER POPUP (hover to show cells, download XLSX)
// =============================================================================

function setupClusterPopup() {
    ['batch1', 'batch2'].forEach(batch => {
        const btn = document.getElementById(`btn-${batch}`);
        if (!btn) return;
        btn.addEventListener('mouseenter', () => showClusterPopup(batch, btn));
    });

    document.getElementById('popup-download-btn').addEventListener('click', () => {
        if (popupBatch) window.location.href = `/api/cluster-cells/${popupBatch}/download`;
    });

    document.getElementById('popup-close-btn').addEventListener('click', hideClusterPopup);
}

function showClusterPopup(batch, anchorEl) {
    if (!config || !config.batches[batch]) return;
    clearTimeout(popupTimer);
    popupBatch = batch;

    const info  = config.batches[batch];
    const cells = info.cells || [];

    document.getElementById('popup-title').textContent = info.label;
    document.getElementById('popup-count').textContent = `${cells.length} cells`;
    document.getElementById('popup-cells').innerHTML =
        cells.map(c => `<span class="cell-chip">${c}</span>`).join('');

    const popup = document.getElementById('cluster-popup');
    popup.style.display = 'block';

    // Position ABOVE the button
    const rect        = anchorEl.getBoundingClientRect();
    const popupHeight = popup.offsetHeight;
    popup.style.left  = `${rect.left + window.scrollX}px`;
    popup.style.top   = `${rect.top + window.scrollY - popupHeight - 8}px`;

    // Auto-dismiss after 5 seconds
    popupTimer = setTimeout(hideClusterPopup, 5000);
}

function hideClusterPopup() {
    clearTimeout(popupTimer);
    document.getElementById('cluster-popup').style.display = 'none';
    popupBatch = null;
}

// =============================================================================
// SPECIFIC DATES MODE
// =============================================================================

function addSpecificDate(dateStr) {
    if (!dateStr) return;
    const max = config ? config.max_specific_dates : 10;
    if (specificDates.includes(dateStr)) { showError(`${dateStr} already added`); return; }
    if (specificDates.length >= max)     { showError(`Maximum ${max} specific dates`); return; }
    specificDates.push(dateStr);
    specificDates.sort();
    renderDateTags();
    clearError();
}

function removeSpecificDate(dateStr) {
    specificDates = specificDates.filter(d => d !== dateStr);
    renderDateTags();
}

function renderDateTags() {
    const container = document.getElementById('date-tags');
    container.innerHTML = specificDates.map(d =>
        `<span class="date-tag">${d}<button class="tag-remove" onclick="removeSpecificDate('${d}')">&times;</button></span>`
    ).join('');
}

// =============================================================================
// COMPARE MODE — DYNAMIC ROWS
// =============================================================================

function initCompareRows() {
    // Start with 2 rows
    compareDays = ['', ''];
    renderCompareRows();
}

function renderCompareRows() {
    const list = document.getElementById('compare-days-list');
    const max  = config ? config.max_compare_days : 7;
    const today = new Date().toISOString().split('T')[0];

    list.innerHTML = compareDays.map((day, i) => {
        const color   = DAY_COLORS[i % DAY_COLORS.length];
        const canRemove = compareDays.length > 2;
        return `
            <div class="compare-day-row">
                <span class="day-dot" style="background:${color}"></span>
                <label class="day-label">Day ${i + 1}</label>
                <input type="date" class="date-input compare-day-input" data-index="${i}"
                       value="${day}" max="${today}">
                ${canRemove ? `<button class="btn btn-remove" onclick="removeCompareDay(${i})">&#x2715;</button>` : ''}
            </div>`;
    }).join('');

    // Wire change events
    list.querySelectorAll('.compare-day-input').forEach(input => {
        input.addEventListener('change', e => {
            compareDays[parseInt(e.target.dataset.index)] = e.target.value;
        });
    });

    // Show/hide "Add Day" button
    const addBtn = document.getElementById('add-compare-day');
    if (addBtn) addBtn.style.display = compareDays.length >= max ? 'none' : '';
}

function addCompareDay() {
    const max = config ? config.max_compare_days : 7;
    if (compareDays.length >= max) return;
    compareDays.push('');
    renderCompareRows();
}

function removeCompareDay(idx) {
    if (compareDays.length <= 2) return;
    compareDays.splice(idx, 1);
    renderCompareRows();
}

// =============================================================================
// EVENT LISTENERS
// =============================================================================

function setupEventListeners() {
    // View toggle
    document.querySelectorAll('.btn-toggle').forEach(btn => {
        btn.addEventListener('click', async e => {
            currentView = e.target.dataset.view;
            document.querySelectorAll('.btn-toggle').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            const isCompare = currentView === 'compare';
            document.getElementById('normal-date-section').style.display = isCompare ? 'none' : '';
            document.getElementById('compare-section').style.display     = isCompare ? '' : 'none';
            document.getElementById('quick-select-group').style.display  = isCompare ? 'none' : '';
            if (!isCompare) await reloadCurrentDates();
        });
    });

    // Batch buttons
    document.querySelectorAll('.btn-batch').forEach(btn => {
        btn.addEventListener('click', async e => {
            currentBatch = e.target.dataset.batch;
            document.querySelectorAll('.btn-batch').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            if (currentView === 'compare') await triggerCompare();
            else await reloadCurrentDates();
        });
    });

    // Quick select
    document.querySelectorAll('.btn-quick').forEach(btn => {
        btn.addEventListener('click', async e => {
            const days = parseInt(e.target.dataset.days);
            const { startDate, endDate } = getDateRangeFromDays(days);
            document.getElementById('start-date').value = startDate;
            document.getElementById('end-date').value   = endDate;
            document.querySelectorAll('.btn-quick').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            // Switch to range mode if in specific mode
            if (dateMode === 'specific') switchDateMode('range');
            await loadRangeData(startDate, endDate);
        });
    });

    // Date mode toggle
    document.getElementById('btn-mode-range').addEventListener('click', () => switchDateMode('range'));
    document.getElementById('btn-mode-specific').addEventListener('click', () => switchDateMode('specific'));

    // Range apply
    document.getElementById('apply-filter').addEventListener('click', async () => {
        const s = document.getElementById('start-date').value;
        const e = document.getElementById('end-date').value;
        if (!s || !e) { showError('Please select both dates'); return; }
        const v = validateDateRange(s, e);
        if (!v.valid) { showError(v.error); return; }
        document.querySelectorAll('.btn-quick').forEach(b => b.classList.remove('active'));
        clearError();
        await loadRangeData(s, e);
    });

    // Real-time range validation
    ['start-date', 'end-date'].forEach(id => {
        document.getElementById(id).addEventListener('change', () => {
            const s = document.getElementById('start-date').value;
            const e = document.getElementById('end-date').value;
            if (s && e) { const v = validateDateRange(s, e); v.valid ? clearError() : showError(v.error); }
        });
    });

    // Specific date add
    document.getElementById('add-date-btn').addEventListener('click', () => {
        const val = document.getElementById('add-specific-date').value;
        addSpecificDate(val);
        document.getElementById('add-specific-date').value = '';
    });
    document.getElementById('add-specific-date').addEventListener('keypress', e => {
        if (e.key === 'Enter') document.getElementById('add-date-btn').click();
    });

    // Specific date apply
    document.getElementById('apply-specific').addEventListener('click', async () => {
        if (specificDates.length === 0) { showError('Add at least one date'); return; }
        clearError();
        await loadSpecificData(specificDates);
    });

    // Compare: add day
    document.getElementById('add-compare-day').addEventListener('click', addCompareDay);

    // Compare: apply
    document.getElementById('apply-compare').addEventListener('click', triggerCompare);
}

function switchDateMode(mode) {
    dateMode = mode;
    document.getElementById('range-inputs').style.display    = mode === 'range'    ? '' : 'none';
    document.getElementById('specific-inputs').style.display = mode === 'specific' ? '' : 'none';
    document.getElementById('btn-mode-range').classList.toggle('active', mode === 'range');
    document.getElementById('btn-mode-specific').classList.toggle('active', mode === 'specific');
}

async function reloadCurrentDates() {
    if (dateMode === 'specific') {
        if (specificDates.length > 0) await loadSpecificData(specificDates);
    } else {
        const s = document.getElementById('start-date').value;
        const e = document.getElementById('end-date').value;
        if (s && e) await loadRangeData(s, e);
    }
}

// =============================================================================
// DATA LOADING
// =============================================================================

async function loadDefaultData() {
    try {
        const defaults = await fetchDefaultDates();
        document.getElementById('start-date').value = defaults.start_date;
        document.getElementById('end-date').value   = defaults.end_date;

        // Pre-fill compare rows
        if (compareDays.length >= 2) {
            compareDays[0] = defaults.start_date;
            compareDays[1] = defaults.end_date;
            renderCompareRows();
        }

        const defaultBtn = document.querySelector(`.btn-quick[data-days="${defaults.default_days}"]`);
        if (defaultBtn) defaultBtn.classList.add('active');

        await loadRangeData(defaults.start_date, defaults.end_date);
    } catch (err) {
        showError('Failed to load default data: ' + err.message);
    }
}

async function loadRangeData(startDate, endDate) {
    showLoading(true);
    clearError();
    try {
        const result = await fetchKPIData({
            view: currentView === 'compare' ? 'hourly' : currentView,
            batch: currentBatch,
            start_date: startDate,
            end_date: endDate
        });
        if (result.success) {
            updateStatusBar(`${startDate} → ${endDate}`, result.total_records);
            renderCharts(result.data);
        }
    } catch (err) {
        showError(err.message);
    } finally {
        showLoading(false);
    }
}

async function loadSpecificData(dates) {
    showLoading(true);
    clearError();
    try {
        const result = await fetchKPIData({
            view: currentView === 'compare' ? 'hourly' : currentView,
            batch: currentBatch,
            dates: dates.join(',')
        });
        if (result.success) {
            updateStatusBar(dates.join(', '), result.total_records);
            renderCharts(result.data);
        }
    } catch (err) {
        showError(err.message);
    } finally {
        showLoading(false);
    }
}

async function triggerCompare() {
    // Collect filled days from inputs (update compareDays from DOM)
    document.querySelectorAll('.compare-day-input').forEach(input => {
        compareDays[parseInt(input.dataset.index)] = input.value;
    });

    const filled = compareDays.filter(d => d.trim() !== '');
    if (filled.length < 2) { showError('Please select at least 2 days to compare'); return; }
    if (new Set(filled).size !== filled.length) { showError('Please select different dates'); return; }

    const max = config ? config.max_compare_days : 7;
    if (filled.length > max) { showError(`Maximum ${max} days for comparison`); return; }

    clearError();
    showLoading(true);
    try {
        // ONE API call with all days — backend returns all rows, frontend groups by date
        const result = await fetchKPIData({
            view: 'hourly',
            batch: currentBatch,
            dates: filled.join(',')
        });
        if (result.success) {
            const batchLabel = { all: 'All Cells', batch1: 'Cluster 1', batch2: 'Cluster 2' }[currentBatch];
            document.getElementById('current-range').textContent =
                `Comparing ${filled.length} days | ${batchLabel} | ${result.total_records} records`;
            renderCompareCharts(result.data, filled);
        }
    } catch (err) {
        showError(err.message);
    } finally {
        showLoading(false);
    }
}

// =============================================================================
// CHART RENDERING — NORMAL MODE
// =============================================================================

function renderCharts(data) {
    const container = document.getElementById('charts-container');
    container.innerHTML = '';
    Object.values(charts).forEach(c => c.destroy());
    charts = {};

    if (!data || data.length === 0) {
        container.innerHTML = '<p class="no-data">No data available for the selected filters.</p>';
        return;
    }

    const isDaily  = currentView === 'daily';
    const labelData = data.map(row => ({
        date: row.date,
        time: row.time || '',
        full: isDaily ? row.date : (row.time ? `${row.date} ${row.time}` : row.date)
    }));

    Object.entries(config.kpi_groups).forEach(([title, cfg], idx) => {
        const columns  = Array.isArray(cfg) ? cfg : cfg.columns;
        const threshold = Array.isArray(cfg) ? null : cfg.threshold;
        const available = columns.filter(col => data[0].hasOwnProperty(col));
        if (available.length === 0) return;

        const card = createChartCard(title, threshold, idx);
        container.appendChild(card);

        const datasets = available.map((col, i) => ({
            label: col.replace(/_/g, ' '),
            data: data.map(row => row[col] !== null ? row[col] : null),
            borderColor: config.colors[i % config.colors.length],
            backgroundColor: config.colors[i % config.colors.length] + '22',
            borderWidth: 2, fill: false, tension: 0.15,
            pointRadius: data.length > 100 ? 0 : 2, pointHoverRadius: 5
        }));

        if (threshold !== null) datasets.push(thresholdDataset(threshold, data.length));

        const ctx = document.getElementById(`chart-${idx}`).getContext('2d');
        charts[`chart-${idx}`] = new Chart(ctx, {
            type: 'line',
            data: { labels: labelData.map(l => l.full), datasets },
            options: chartOptions(title, isDaily, labelData)
        });
    });
}

// =============================================================================
// CHART RENDERING — COMPARE MODE
// =============================================================================

function renderCompareCharts(data, days) {
    const container = document.getElementById('charts-container');
    container.innerHTML = '';
    Object.values(charts).forEach(c => c.destroy());
    charts = {};

    if (!data || data.length === 0) {
        container.innerHTML = '<p class="no-data">No data available for the selected dates.</p>';
        return;
    }

    // Collect all hours present, sorted
    const allTimes = Array.from(new Set(data.map(r => r.time))).sort();

    // Index data: { date → { time → row } }
    const byDate = {};
    data.forEach(row => {
        if (!byDate[row.date]) byDate[row.date] = {};
        byDate[row.date][row.time] = row;
    });

    Object.entries(config.kpi_groups).forEach(([title, cfg], idx) => {
        const columns   = Array.isArray(cfg) ? cfg : cfg.columns;
        const threshold = Array.isArray(cfg) ? null : cfg.threshold;
        const col       = columns[0];
        const hasData   = data.length > 0 && data[0].hasOwnProperty(col);
        if (!hasData) return;

        const card = createChartCard(title, threshold, idx);
        container.appendChild(card);

        const datasets = days.map((day, i) => ({
            label: `${day}`,
            data: allTimes.map(t => byDate[day]?.[t]?.[col] ?? null),
            borderColor: DAY_COLORS[i % DAY_COLORS.length],
            backgroundColor: DAY_COLORS[i % DAY_COLORS.length] + '22',
            borderWidth: 2, fill: false, tension: 0.15,
            pointRadius: 2, pointHoverRadius: 5,
            borderDash: i === 0 ? [] : (i % 2 === 0 ? [4, 2] : [8, 3])
        }));

        if (threshold !== null) datasets.push(thresholdDataset(threshold, allTimes.length));

        const timeLabels = allTimes.map(t => ({ date: '', time: t, full: t }));
        const ctx = document.getElementById(`chart-${idx}`).getContext('2d');
        charts[`chart-${idx}`] = new Chart(ctx, {
            type: 'line',
            data: { labels: allTimes, datasets },
            options: chartOptions(title, false, timeLabels)
        });
    });
}

// =============================================================================
// CHART HELPERS
// =============================================================================

function createChartCard(title, threshold, idx) {
    const card = document.createElement('div');
    card.className = 'chart-card';
    const badge = threshold !== null
        ? `<span class="threshold-info">Threshold: ${threshold}</span>` : '';
    card.innerHTML = `
        <h3 class="chart-title">${title} ${badge}</h3>
        <div class="chart-wrapper"><canvas id="chart-${idx}"></canvas></div>`;
    return card;
}

function thresholdDataset(threshold, length) {
    return {
        label: `Target (${threshold})`,
        data: Array(length).fill(threshold),
        borderColor: '#FFB347', backgroundColor: 'transparent',
        borderWidth: 2, borderDash: [8, 4],
        fill: false, pointRadius: 0, pointHoverRadius: 0
    };
}

function chartOptions(title, isDaily, labelData) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
            legend: { position: 'bottom', labels: { usePointStyle: true, padding: 12 } },
            tooltip: {
                callbacks: {
                    label: ctx => {
                        const val = ctx.parsed.y;
                        return val !== null ? `${ctx.dataset.label}: ${val.toFixed(3)}` : `${ctx.dataset.label}: N/A`;
                    }
                }
            }
        },
        scales: {
            x: {
                title: { display: true, text: isDaily ? 'Date' : 'Date / Time' },
                ticks: {
                    maxRotation: 45, minRotation: 45, autoSkip: true,
                    maxTicksLimit: isDaily ? 14 : 48,
                    callback: function(tickValue, index, ticks) {
                        const cur = labelData[tickValue];
                        if (!cur) return '';
                        if (isDaily) return cur.date;
                        // Compare against previous VISIBLE tick's date (not previous data point)
                        const prevTick = index > 0 ? ticks[index - 1] : null;
                        const prevDate = prevTick && labelData[prevTick.value]
                            ? labelData[prevTick.value].date : null;
                        if (!prevDate || prevDate !== cur.date) return [cur.date, cur.time];
                        return cur.time;
                    }
                }
            },
            y: { title: { display: true, text: title }, beginAtZero: false }
        }
    };
}

// =============================================================================
// UI HELPERS
// =============================================================================

function showLoading(show) {
    document.getElementById('loading').style.display          = show ? 'flex' : 'none';
    document.getElementById('charts-container').style.display = show ? 'none' : 'grid';
}

function showError(msg) {
    const el = document.getElementById('error-message');
    el.textContent = msg;
    el.style.display = 'inline';
}

function clearError() {
    const el = document.getElementById('error-message');
    el.textContent = '';
    el.style.display = 'none';
}

function updateStatusBar(dateLabel, total) {
    const batchLabel = { all: 'All Cells', batch1: 'Cluster 1', batch2: 'Cluster 2' }[currentBatch] || currentBatch;
    document.getElementById('current-range').textContent = `${dateLabel} | ${batchLabel} | ${total} records`;
}
