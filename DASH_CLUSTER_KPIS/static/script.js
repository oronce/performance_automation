/**
 * Cluster KPI Dashboard — Frontend JavaScript
 */

const APP_PASSWORD = '123123';

// Colors for compare mode (up to 7 days)
const DAY_COLORS = [
    '#3498db', // blue
    '#f59905', // orange
    '#2ecc71', // green
    '#9b59b6', // purple
    '#1abc9c', // teal
    '#e67e22', // dark orange
    '#8e44ad', // dark purple
];

let config        = null;
let charts        = {};
let currentTech   = '2g';      // active technology key
let currentVendor = null;      // active vendor key (set on init)
let currentView   = 'hourly';  // 'hourly' | 'daily' | 'compare'
let currentBatch  = 'all';
let dateMode      = 'range';   // 'range' | 'specific'
let specificDates = [];
let compareDays   = [];
let popupBatch    = null;
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

        // Set initial state: first tech and its first vendor
        currentTech   = Object.keys(config.technologies)[0];
        currentVendor = Object.keys(config.technologies[currentTech].vendors)[0];
        currentBatch  = 'all';

        renderTechButtons();
        renderVendorButtons(currentTech);
        renderBatchButtons(currentTech, currentVendor);
        setupPopupButtons();
        updateSubtitle();
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
    const qs  = new URLSearchParams(params).toString();
    const res = await fetch(`/api/kpi-data?${qs}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Failed to fetch data');
    return data;
}

// =============================================================================
// TECHNOLOGY BUTTONS
// =============================================================================

function renderTechButtons() {
    const container = document.getElementById('tech-buttons');
    container.innerHTML = Object.entries(config.technologies).map(([key, info]) =>
        `<button class="btn btn-toggle${key === currentTech ? ' active' : ''}" data-tech="${key}">${info.label}</button>`
    ).join('');

    container.querySelectorAll('[data-tech]').forEach(btn => {
        btn.addEventListener('click', async e => {
            const selected = e.currentTarget.dataset.tech;
            if (selected === currentTech) return;

            currentTech   = selected;
            currentVendor = Object.keys(config.technologies[currentTech].vendors)[0];
            currentBatch  = 'all';

            container.querySelectorAll('[data-tech]').forEach(b => b.classList.remove('active'));
            e.currentTarget.classList.add('active');

            renderVendorButtons(currentTech);
            renderBatchButtons(currentTech, currentVendor);
            updateSubtitle();
            await reloadCurrentDates();
        });
    });
}

// =============================================================================
// VENDOR BUTTONS
// =============================================================================

function renderVendorButtons(tech) {
    const container = document.getElementById('vendor-buttons');
    const vendors   = config.technologies[tech]?.vendors || {};

    container.innerHTML = Object.entries(vendors).map(([key, info]) =>
        `<button class="btn btn-toggle${key === currentVendor ? ' active' : ''}" data-vendor="${key}">${info.label}</button>`
    ).join('');

    container.querySelectorAll('[data-vendor]').forEach(btn => {
        btn.addEventListener('click', async e => {
            const selected = e.currentTarget.dataset.vendor;
            if (selected === currentVendor) return;

            currentVendor = selected;
            currentBatch  = 'all';

            container.querySelectorAll('[data-vendor]').forEach(b => b.classList.remove('active'));
            e.currentTarget.classList.add('active');

            renderBatchButtons(currentTech, currentVendor);
            updateSubtitle();
            await reloadCurrentDates();
        });
    });
}

// =============================================================================
// BATCH BUTTONS  (dynamic per tech + vendor)
// =============================================================================

function renderBatchButtons(tech, vendor) {
    const container = document.getElementById('batch-buttons');
    const vendorCfg = config.technologies[tech]?.vendors[vendor] || {};
    const batches   = vendorCfg.batches || {};

    // "All Cells" is always first
    let html = `<button class="btn btn-batch${currentBatch === 'all' ? ' active' : ''}" data-batch="all">All Cells</button>`;

    Object.entries(batches).forEach(([key, info]) => {
        if (key === 'all') return;
        const count = info.count !== null ? ` (${info.count})` : '';
        html += `<button class="btn btn-batch${currentBatch === key ? ' active' : ''}" data-batch="${key}">${info.label}${count}</button>`;
    });

    container.innerHTML = html;

    // Click events
    container.querySelectorAll('.btn-batch').forEach(btn => {
        btn.addEventListener('click', async e => {
            const clicked = e.currentTarget;
            currentBatch  = clicked.dataset.batch;
            container.querySelectorAll('.btn-batch').forEach(b => b.classList.remove('active'));
            clicked.classList.add('active');
            if (currentView === 'compare') await triggerCompare();
            else await reloadCurrentDates();
        });
    });

    // Hover popup for batches that have cells
    Object.entries(batches).forEach(([key, info]) => {
        if (key === 'all' || !info.cells || info.cells.length === 0) return;
        const btn = container.querySelector(`[data-batch="${key}"]`);
        if (!btn) return;
        btn.addEventListener('mouseenter', () => showClusterPopup(key, btn));
    });
}

// =============================================================================
// CLUSTER POPUP
// =============================================================================

function setupPopupButtons() {
    document.getElementById('popup-download-btn').addEventListener('click', () => {
        if (popupBatch) {
            window.location.href = `/api/cluster-cells/${currentTech}/${currentVendor}/${popupBatch}/download`;
        }
    });
    document.getElementById('popup-close-btn').addEventListener('click', hideClusterPopup);
}

function showClusterPopup(batch, anchorEl) {
    const vendorCfg = config.technologies[currentTech]?.vendors[currentVendor];
    if (!vendorCfg || !vendorCfg.batches[batch]) return;
    clearTimeout(popupTimer);
    popupBatch = batch;

    const info  = vendorCfg.batches[batch];
    const cells = info.cells || [];

    document.getElementById('popup-title').textContent = info.label;
    document.getElementById('popup-count').textContent = `${cells.length} cells`;
    document.getElementById('popup-cells').innerHTML   =
        cells.map(c => `<span class="cell-chip">${c}</span>`).join('');

    const popup = document.getElementById('cluster-popup');
    popup.style.display = 'block';

    const rect        = anchorEl.getBoundingClientRect();
    const popupHeight = popup.offsetHeight;
    popup.style.left  = `${rect.left + window.scrollX}px`;
    popup.style.top   = `${rect.top  + window.scrollY - popupHeight - 8}px`;

    popupTimer = setTimeout(hideClusterPopup, 5000);
}

function hideClusterPopup() {
    clearTimeout(popupTimer);
    document.getElementById('cluster-popup').style.display = 'none';
    popupBatch = null;
}

// =============================================================================
// SUBTITLE
// =============================================================================

function updateSubtitle() {
    const techLabel   = config.technologies[currentTech]?.label   || currentTech.toUpperCase();
    const vendorLabel = config.technologies[currentTech]?.vendors[currentVendor]?.label || currentVendor;
    document.getElementById('header-subtitle').textContent =
        `${techLabel} \u2014 ${vendorLabel} \u2014 Network Performance Indicators`;
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
    if (start > end)                return { valid: false, error: 'Start date must be before end date' };
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
    compareDays = ['', ''];
    renderCompareRows();
}

function renderCompareRows() {
    const list  = document.getElementById('compare-days-list');
    const max   = config ? config.max_compare_days : 7;
    const today = new Date().toISOString().split('T')[0];

    list.innerHTML = compareDays.map((day, i) => {
        const color     = DAY_COLORS[i % DAY_COLORS.length];
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

    list.querySelectorAll('.compare-day-input').forEach(input => {
        input.addEventListener('change', e => {
            compareDays[parseInt(e.target.dataset.index)] = e.target.value;
        });
    });

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
    document.querySelectorAll('.btn-toggle[data-view]').forEach(btn => {
        btn.addEventListener('click', async e => {
            currentView = e.target.dataset.view;
            document.querySelectorAll('.btn-toggle[data-view]').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            const isCompare = currentView === 'compare';
            document.getElementById('normal-date-section').style.display = isCompare ? 'none' : '';
            document.getElementById('compare-section').style.display     = isCompare ? '' : 'none';
            document.getElementById('quick-select-group').style.display  = isCompare ? 'none' : '';
            if (!isCompare) await reloadCurrentDates();
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
            if (dateMode === 'specific') switchDateMode('range');
            await loadRangeData(startDate, endDate);
        });
    });

    // Date mode toggle
    document.getElementById('btn-mode-range').addEventListener('click',    () => switchDateMode('range'));
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
    document.getElementById('btn-mode-range').classList.toggle('active',    mode === 'range');
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
            tech:       currentTech,
            vendor:     currentVendor,
            view:       currentView === 'compare' ? 'hourly' : currentView,
            batch:      currentBatch,
            start_date: startDate,
            end_date:   endDate
        });
        if (result.success) {
            updateStatusBar(`${startDate} \u2192 ${endDate}`, result.total_records);
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
            tech:   currentTech,
            vendor: currentVendor,
            view:   currentView === 'compare' ? 'hourly' : currentView,
            batch:  currentBatch,
            dates:  dates.join(',')
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
    document.querySelectorAll('.compare-day-input').forEach(input => {
        compareDays[parseInt(input.dataset.index)] = input.value;
    });

    const filled = compareDays.filter(d => d.trim() !== '');
    if (filled.length < 2)                      { showError('Please select at least 2 days to compare'); return; }
    if (new Set(filled).size !== filled.length) { showError('Please select different dates'); return; }

    const max = config ? config.max_compare_days : 7;
    if (filled.length > max) { showError(`Maximum ${max} days for comparison`); return; }

    clearError();
    showLoading(true);
    try {
        const result = await fetchKPIData({
            tech:   currentTech,
            vendor: currentVendor,
            view:   'hourly',
            batch:  currentBatch,
            dates:  filled.join(',')
        });
        if (result.success) {
            const vendorCfg  = config.technologies[currentTech]?.vendors[currentVendor];
            const batchLabel = vendorCfg?.batches[currentBatch]?.label || 'All Cells';
            const techLabel  = config.technologies[currentTech]?.label || currentTech;
            const vendorLabel = vendorCfg?.label || currentVendor;
            document.getElementById('current-range').textContent =
                `Comparing ${filled.length} days | ${techLabel} | ${vendorLabel} | ${batchLabel} | ${result.total_records} records`;
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

    const isDaily   = currentView === 'daily';
    const labelData = data.map(row => ({
        date: row.date,
        time: row.time || '',
        full: isDaily ? row.date : (row.time ? `${row.date} ${row.time}` : row.date)
    }));

    const kpiGroups = config.technologies[currentTech].vendors[currentVendor].kpi_groups;

    Object.entries(kpiGroups).forEach(([title, cfg], idx) => {
        const columns   = Array.isArray(cfg) ? cfg : cfg.columns;
        const threshold = Array.isArray(cfg) ? null : cfg.threshold;
        const available = columns.filter(col => data[0].hasOwnProperty(col));
        if (available.length === 0) return;

        const card = createChartCard(title, threshold, idx);
        container.appendChild(card);

        const datasets = available.map((col, i) => ({
            label:           col.replace(/_/g, ' '),
            data:            data.map(row => row[col] !== null ? row[col] : null),
            borderColor:     config.colors[i % config.colors.length],
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

    const allTimes = Array.from(new Set(data.map(r => r.time))).sort();

    const byDate = {};
    data.forEach(row => {
        if (!byDate[row.date]) byDate[row.date] = {};
        byDate[row.date][row.time] = row;
    });

    const kpiGroups = config.technologies[currentTech].vendors[currentVendor].kpi_groups;

    Object.entries(kpiGroups).forEach(([title, cfg], idx) => {
        const columns   = Array.isArray(cfg) ? cfg : cfg.columns;
        const threshold = Array.isArray(cfg) ? null : cfg.threshold;
        const col       = columns[0];
        const hasData   = data.length > 0 && data[0].hasOwnProperty(col);
        if (!hasData) return;

        const card = createChartCard(title, threshold, idx);
        container.appendChild(card);

        const datasets = days.map((day, i) => ({
            label:           `${day}`,
            data:            allTimes.map(t => byDate[day]?.[t]?.[col] ?? null),
            borderColor:     DAY_COLORS[i % DAY_COLORS.length],
            backgroundColor: DAY_COLORS[i % DAY_COLORS.length] + '22',
            borderWidth: 2, fill: false, tension: 0.15,
            pointRadius: 2, pointHoverRadius: 5,
            borderDash: i === 0 ? [] : (i % 2 === 0 ? [4, 2] : [8, 3])
        }));

        if (threshold !== null) datasets.push(thresholdDataset(threshold, allTimes.length));

        const ctx = document.getElementById(`chart-${idx}`).getContext('2d');
        charts[`chart-${idx}`] = new Chart(ctx, {
            type: 'line',
            data: { labels: allTimes, datasets },
            options: chartOptions(title, false, allTimes.map(t => ({ date: '', time: t, full: t })))
        });
    });
}

// =============================================================================
// CHART HELPERS
// =============================================================================

function createChartCard(title, threshold, idx) {
    const card  = document.createElement('div');
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
        label:           `Target (${threshold})`,
        data:            Array(length).fill(threshold),
        borderColor:     '#e74c3c',
        backgroundColor: 'transparent',
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
    el.textContent   = msg;
    el.style.display = 'inline';
}

function clearError() {
    const el = document.getElementById('error-message');
    el.textContent   = '';
    el.style.display = 'none';
}

function updateStatusBar(dateLabel, total) {
    const techLabel   = config.technologies[currentTech]?.label || currentTech;
    const vendorCfg   = config.technologies[currentTech]?.vendors[currentVendor];
    const vendorLabel = vendorCfg?.label || currentVendor;
    const batchLabel  = vendorCfg?.batches[currentBatch]?.label || 'All Cells';
    document.getElementById('current-range').textContent =
        `${dateLabel} | ${techLabel} | ${vendorLabel} | ${batchLabel} | ${total} records`;
}
