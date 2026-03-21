/**
 * 2G KPI Dashboard
 */

// =============================================================================
// PINNED LOCATIONS  — appear first in the breakdown list
// All other locations from the data are appended alphabetically after these.
// =============================================================================

const PINNED_COMMUNES        = ['COTONOU', 'CALAVI'];
const PINNED_ARRONDISSEMENTS = [];   // fill when needed

// =============================================================================
// KPI CONFIG
// =============================================================================

const KPI_CONFIG = {
  CSSR: {
    label:    'CSSR (%)',
    ERICSSON: { script: '2g_ericsson',             col: 'CSSR_ERICSSON' },
    HUAWEI:   { script: '2g_huawei',               col: 'CSSR_HUAWEI'   },
  },
  AVAILABILITY: {
    label:    'Cell Availability (%)',
    ERICSSON: { script: '2g_ericsson',             col: 'CELL_AVAILABILITY_RATE_ERICSSON' },
    HUAWEI:   { script: '2g_huawei',               col: 'CELL_AVAILABILITY_RATE_HUAWEI'   },
  },
  PACKET_LOSS: {
    label:    'Packet Loss (%)',
    ERICSSON: { script: '3g_ericsson_packet_loss', col: 'packet_loss_3g_bb' },
    HUAWEI:   { script: '3g_huawei_packet_loss',   col: 'packet_loss_pct'   },
  },
};

const KPI_LABELS = { CSSR: 'CSSR', AVAILABILITY: 'Availability', PACKET_LOSS: 'Packet Loss' };
const COLORS     = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22'];

// =============================================================================
// STATE
// =============================================================================

const state = {
  kpi:         'CSSR',
  vendor:      'ERICSSON',
  granularity: 'HOURLY',
  level:       'commune',
  startDate:   '',
  endDate:     '',
};

let overviewChart = null;
const breakdownCharts = {};

// =============================================================================
// INIT
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
  setDefaultDates(2);
  bindToggles();
  bindDateControls();
  bindSearch();
  loadAll();
  initSectionNav();
  initCaFilters();
});

function setDefaultDates(days) {
  const today = new Date();
  const start = new Date(today);
  start.setDate(today.getDate() - (days - 1));
  state.startDate = fmt(start);
  state.endDate   = fmt(today);
  document.getElementById('start-date').value = state.startDate;
  document.getElementById('end-date').value   = state.endDate;
}

function fmt(d) { return d.toISOString().split('T')[0]; }

// =============================================================================
// TOGGLES & DATE CONTROLS
// =============================================================================

function bindToggles() {
  ['kpi', 'vendor', 'granularity', 'level'].forEach(key => {
    document.querySelectorAll(`[data-${key}]`).forEach(btn => {
      btn.addEventListener('click', () => {
        state[key] = btn.dataset[key];
        document.querySelectorAll(`[data-${key}]`).forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        loadAll();
      });
    });
  });

  document.querySelectorAll('.btn-quick').forEach(btn => {
    btn.addEventListener('click', () => {
      setDefaultDates(parseInt(btn.dataset.days));
      document.querySelectorAll('.btn-quick').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      loadAll();
    });
  });
}

const MAX_DAYS = 8;

function validateRange(s, e) {
  if (!s || !e)  return 'Select both dates.';
  if (s > e)     return 'Start must be before end.';
  const days = Math.round((new Date(e) - new Date(s)) / 86400000) + 1;
  if (days > MAX_DAYS) return `Max ${MAX_DAYS} days allowed (${days} selected).`;
  return null;
}

function bindDateControls() {
  document.getElementById('apply-btn').addEventListener('click', () => {
    const s = document.getElementById('start-date').value;
    const e = document.getElementById('end-date').value;
    const err = validateRange(s, e);
    if (err) { showError(err); return; }
    clearError();
    state.startDate = s;
    state.endDate   = e;
    document.querySelectorAll('.btn-quick').forEach(b => b.classList.remove('active'));
    loadAll();
  });
}

// =============================================================================
// SEARCH / FILTER
// =============================================================================

function bindSearch() {
  document.getElementById('loc-search').addEventListener('input', e => {
    applySearch(e.target.value.trim());
  });

  document.getElementById('search-clear').addEventListener('click', () => {
    document.getElementById('loc-search').value = '';
    applySearch('');
  });
}

function applySearch(query) {
  let visible = 0;
  document.querySelectorAll('[data-location]').forEach(card => {
    const match = !query || card.dataset.location.toLowerCase().includes(query.toLowerCase());
    card.style.display = match ? '' : 'none';
    if (match) visible++;
  });
  const total = document.querySelectorAll('[data-location]').length;
  document.getElementById('loc-count').textContent =
    query ? `${visible} / ${total} shown` : `${total} locations`;
}

// =============================================================================
// API
// =============================================================================

async function fetchKpi(granularity, aggregationLevel) {
  const { script, col } = KPI_CONFIG[state.kpi][state.vendor];
  const params = new URLSearchParams({
    script,
    start_date:  state.startDate,
    end_date:    state.endDate,
    granularity,
  });
  if (aggregationLevel) params.set('aggregation_level', aggregationLevel);

  const res  = await fetch('/sql_query?' + params.toString());
  const json = await res.json();
  if (!res.ok) throw new Error(json.detail || 'API error');
  return { rows: json.data || [], col };
}

// =============================================================================
// LOAD
// =============================================================================

async function loadAll() {
  showLoading(true);
  clearError();

  try {
    const [overview, breakdown] = await Promise.all([
      fetchKpi(state.granularity, null),
      fetchKpi(state.granularity, state.level),
    ]);

    renderOverview(overview.rows, overview.col);
    renderBreakdown(breakdown.rows, breakdown.col);
    updateRange();
  } catch (err) {
    showError(err.message);
  } finally {
    showLoading(false);
  }
}

// =============================================================================
// OVERVIEW CHART
// =============================================================================

function renderOverview(rows, col) {
  const isHourly = state.granularity === 'HOURLY';
  const labels   = rows.map(r => isHourly ? `${r.date} ${r.time || ''}`.trim() : r.date);
  const values   = rows.map(r => r[col] ?? null);

  document.getElementById('overview-title').textContent =
    `${KPI_LABELS[state.kpi]} — ${state.vendor} — Network (${state.granularity})`;

  if (overviewChart) { overviewChart.destroy(); overviewChart = null; }

  const wrapper = document.getElementById('overview-wrapper');
  if (!rows.length) {
    wrapper.innerHTML = '<p class="no-data">No data for this period</p>';
    return;
  }
  wrapper.innerHTML = '<canvas id="overview-chart"></canvas>';

  overviewChart = buildLineChart(
    document.getElementById('overview-chart').getContext('2d'),
    labels, values, KPI_CONFIG[state.kpi].label, COLORS[0], isHourly
  );
}

// =============================================================================
// BREAKDOWN CHARTS
// =============================================================================

function renderBreakdown(rows, col) {
  // Destroy old charts
  Object.values(breakdownCharts).forEach(c => c.destroy());
  Object.keys(breakdownCharts).forEach(k => delete breakdownCharts[k]);

  const levelKey = state.level;
  const pinned   = state.level === 'commune' ? PINNED_COMMUNES : PINNED_ARRONDISSEMENTS;

  // Extract all unique locations from data
  const allLocs = [...new Set(rows.map(r => r[levelKey]).filter(Boolean))];
  const sorted  = sortLocations(allLocs, pinned);

  document.getElementById('breakdown-section-title').textContent =
    `${KPI_LABELS[state.kpi]} — ${state.vendor} — By ${capitalize(levelKey)}`;

  // Reset search
  document.getElementById('loc-search').value = '';
  document.getElementById('loc-count').textContent = `${sorted.length} locations`;

  const container = document.getElementById('breakdown-container');
  container.innerHTML = '';

  const isHourly = state.granularity === 'HOURLY';

  sorted.forEach((loc, i) => {
    const locRows = rows.filter(r => (r[levelKey] || '').toUpperCase() === loc.toUpperCase());
    const labels  = locRows.map(r => isHourly ? `${r.date} ${r.time || ''}`.trim() : r.date);
    const values  = locRows.map(r => r[col] ?? null);
    const isPinned = pinned.map(p => p.toUpperCase()).includes(loc.toUpperCase());

    const card = document.createElement('div');
    card.className = 'chart-card';
    card.dataset.location = loc;
    card.innerHTML = `
      <h3 class="chart-title">
        ${loc}${isPinned ? ' <span class="pinned-badge">★</span>' : ''}
      </h3>
      <div class="chart-wrapper"><canvas id="bc-${i}"></canvas></div>
    `;
    container.appendChild(card);

    if (!locRows.length) {
      card.querySelector('.chart-wrapper').innerHTML = '<p class="no-data">No data</p>';
      return;
    }

    const color = isPinned ? COLORS[0] : COLORS[(i % (COLORS.length - 1)) + 1];
    const ctx   = document.getElementById(`bc-${i}`).getContext('2d');
    breakdownCharts[loc] = buildLineChart(ctx, labels, values, KPI_CONFIG[state.kpi].label, color, isHourly);
  });
}

// =============================================================================
// LOCATION SORT: pinned first, rest alphabetically
// =============================================================================

function sortLocations(allLocs, pinned) {
  const pinnedUp  = pinned.map(p => p.toUpperCase());
  const locUp     = allLocs.map(l => l.toUpperCase());

  const pinnedOut = [];
  const rest      = [];

  allLocs.forEach(l => {
    if (pinnedUp.includes(l.toUpperCase())) pinnedOut.push(l);
    else rest.push(l);
  });

  // Preserve manual pin order
  pinnedOut.sort((a, b) =>
    pinnedUp.indexOf(a.toUpperCase()) - pinnedUp.indexOf(b.toUpperCase())
  );
  rest.sort((a, b) => a.localeCompare(b));

  return [...pinnedOut, ...rest];
}

// =============================================================================
// SHARED LINE CHART BUILDER
// =============================================================================

function buildLineChart(ctx, labels, values, yLabel, color, isHourly) {
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label:            yLabel,
        data:             values,
        borderColor:      color,
        backgroundColor:  color + '20',
        borderWidth:      2,
        fill:             false,
        tension:          0.2,
        pointRadius:      isHourly ? 1 : 3,
        pointHoverRadius: 5,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: c => `${c.dataset.label}: ${c.parsed.y !== null ? c.parsed.y.toFixed(2) : 'N/A'}`,
          },
        },
      },
      scales: {
        x: {
          ticks: {
            maxRotation: 45,
            autoSkip: true,
            maxTicksLimit: isHourly ? 24 : 14,
          },
        },
        y: {
          title: { display: true, text: yLabel },
          beginAtZero: false,
        },
      },
    },
  });
}

// =============================================================================
// UI HELPERS
// =============================================================================

function showLoading(on) {
  document.getElementById('loading').style.display      = on ? 'flex' : 'none';
  document.getElementById('main-content').style.display = on ? 'none' : 'block';
}

function showError(msg) {
  const el = document.getElementById('error-msg');
  el.textContent   = msg;
  el.style.display = 'inline';
}

function clearError() {
  const el = document.getElementById('error-msg');
  el.textContent   = '';
  el.style.display = 'none';
}

function updateRange() {
  document.getElementById('current-range').textContent =
    `${state.startDate} → ${state.endDate}  |  ${state.vendor}  |  ${KPI_LABELS[state.kpi]}  |  ${state.granularity}`;
}

function capitalize(s) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// =============================================================================
// SECTION NAVIGATION
// =============================================================================

let currentSection = 'kpi';

function initSectionNav() {
  document.querySelectorAll('.btn-section').forEach(btn => {
    btn.addEventListener('click', () => {
      const section = btn.dataset.section;
      if (section === currentSection) return;
      currentSection = section;
      document.querySelectorAll('.btn-section').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById('kpi-section').style.display  = section === 'kpi'  ? '' : 'none';
      document.getElementById('cssr-section').style.display = section === 'cssr' ? '' : 'none';
      if (section === 'cssr') loadCssrAnalysis();
    });
  });
}

// =============================================================================
// CSSR ANALYSIS — STATE & INIT
// =============================================================================

const caState = {
  startDate: '',
  endDate:   '',
  timeStart: '',
  timeEnd:   '',
  level:     'cell_name',
  vendor:    'ERICSSON',
};

let pieEricssonChart = null;
let pieHuaweiChart   = null;
let barChart         = null;

function initCaFilters() {
  // Default: last 7 days
  const today = new Date();
  const start = new Date(today);
  start.setDate(today.getDate() - 6);
  caState.startDate = fmt(start);
  caState.endDate   = fmt(today);
  document.getElementById('ca-start-date').value = caState.startDate;
  document.getElementById('ca-end-date').value   = caState.endDate;
  updateCaRange();

  document.getElementById('ca-apply-btn').addEventListener('click', () => {
    const s = document.getElementById('ca-start-date').value;
    const e = document.getElementById('ca-end-date').value;
    if (!s || !e || s > e) { showCaError('Invalid date range.'); return; }
    clearCaError();
    caState.startDate = s;
    caState.endDate   = e;
    caState.timeStart = document.getElementById('ca-time-start').value || '';
    caState.timeEnd   = document.getElementById('ca-time-end').value   || '';
    updateCaRange();
    loadCssrAnalysis();
  });

  document.querySelectorAll('.ca-level').forEach(btn => {
    btn.addEventListener('click', () => {
      caState.level = btn.dataset.caLevel;
      document.querySelectorAll('.ca-level').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      loadBarChart();
    });
  });

  document.querySelectorAll('.ca-vendor').forEach(btn => {
    btn.addEventListener('click', () => {
      caState.vendor = btn.dataset.caVendor;
      document.querySelectorAll('.ca-vendor').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      loadBarChart();
    });
  });

  document.getElementById('open-map-btn').addEventListener('click', () => {
    const params = new URLSearchParams({
      start_date: caState.startDate,
      end_date:   caState.endDate,
      level:      caState.level,
    });
    if (caState.timeStart) params.set('time_start', caState.timeStart);
    if (caState.timeEnd)   params.set('time_end',   caState.timeEnd);
    window.open('/static/map.html?' + params.toString(), '_blank');
  });
}

// =============================================================================
// CSSR ANALYSIS — FETCH
// =============================================================================

async function fetchWorstCells(script, aggregation_level, limit) {
  const params = new URLSearchParams({
    script,
    start_date: caState.startDate,
    end_date:   caState.endDate,
  });
  if (aggregation_level) params.set('aggregation_level', aggregation_level);
  if (caState.timeStart) params.set('time_start', caState.timeStart);
  if (caState.timeEnd)   params.set('time_end',   caState.timeEnd);
  if (limit)             params.set('limit', limit);

  const res  = await fetch('/worst_cells?' + params.toString());
  const json = await res.json();
  if (!res.ok) throw new Error(json.detail || 'API error');
  return json.data || [];
}

// =============================================================================
// CSSR ANALYSIS — LOAD
// =============================================================================

async function loadCssrAnalysis() {
  showCaLoading(true);
  clearCaError();

  try {
    const [ericssonPie, huaweiPie] = await Promise.all([
      fetchWorstCells('2g_ericsson_worst_cell', null, null),
      fetchWorstCells('2g_huawei_worst_cell',   null, null),
    ]);

    renderPieChart(
      'pie-ericsson-wrapper', 'pie-ericsson',
      ericssonPie[0] || null, 'ericsson'
    );
    renderPieChart(
      'pie-huawei-wrapper', 'pie-huawei',
      huaweiPie[0] || null, 'huawei'
    );

    await loadBarChart();

  } catch (err) {
    showCaError(err.message);
  } finally {
    showCaLoading(false);
  }
}

async function loadBarChart() {
  const script = caState.vendor === 'ERICSSON'
    ? '2g_ericsson_worst_cell'
    : '2g_huawei_worst_cell';

  const levelLabel = caState.level.replace('_', ' ');
  const vendorLabel = caState.vendor === 'ERICSSON' ? 'Ericsson' : 'Huawei';
  document.getElementById('bar-title').textContent =
    `Top 50 Worst ${capitalize(levelLabel)}s — ${vendorLabel} — by CSR Failures`;

  try {
    const rows = await fetchWorstCells(script, caState.level, 50);
    renderWorstCellsBar(rows);
  } catch (err) {
    showCaError(err.message);
  }
}

// =============================================================================
// CSSR ANALYSIS — PIE CHART
// =============================================================================

const CA_PIE_CFG = {
  ericsson: {
    labels: ['SDCCH Congestion', 'SDCCH Drops', 'TCH Assign Fails', 'TCH Drops'],
    cols:   ['NUMBER_SDCONG', 'NUMBER_OF_SDDROPS', 'TCH_ASSIGN_FAILS', 'NUMBER_OF_TCH_DROPS'],
    colors: ['#e74c3c', '#e67e22', '#3498db', '#9b59b6'],
    cssrCol: 'CSSR_ERICSSON',
  },
  huawei: {
    labels: ['SDCCH Assign Fails', 'SDCCH Drops', 'TCH Assign Fails', 'TCH Drops'],
    cols:   ['SDCCH_ASSIGN_FAILS', 'SDCCH_DROPS', 'TCH_ASSIGN_FAILS', 'TCH_DROPS'],
    colors: ['#e74c3c', '#e67e22', '#3498db', '#9b59b6'],
    cssrCol: 'CSSR_HUAWEI',
  },
};

function renderPieChart(wrapperId, canvasId, row, vendor) {
  if (vendor === 'ericsson' && pieEricssonChart) { pieEricssonChart.destroy(); pieEricssonChart = null; }
  if (vendor === 'huawei'   && pieHuaweiChart)   { pieHuaweiChart.destroy();   pieHuaweiChart   = null; }

  const wrapper = document.getElementById(wrapperId);

  if (!row) {
    wrapper.innerHTML = '<p class="no-data">No data for this period</p>';
    return;
  }

  if (!document.getElementById(canvasId)) {
    wrapper.innerHTML = `<canvas id="${canvasId}"></canvas>`;
  }

  const cfg    = CA_PIE_CFG[vendor];
  const values = cfg.cols.map(c => row[c] ?? 0);
  const total  = values.reduce((a, b) => a + b, 0);
  const cssrVal = row[cfg.cssrCol];
  const cssrTxt = cssrVal !== null && cssrVal !== undefined
    ? `CSSR: ${parseFloat(cssrVal).toFixed(2)}%`
    : 'CSSR: N/A';

  const chart = new Chart(
    document.getElementById(canvasId).getContext('2d'),
    {
      type: 'doughnut',
      data: {
        labels: cfg.labels,
        datasets: [{
          data:            values,
          backgroundColor: cfg.colors,
          borderWidth:     2,
          borderColor:     '#fff',
        }],
      },
      options: {
        responsive:          true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels:   { padding: 15, font: { size: 13 } },
          },
          tooltip: {
            callbacks: {
              label: c => {
                const v   = c.parsed;
                const pct = total > 0 ? (v / total * 100).toFixed(1) : 0;
                return `${c.label}: ${Number(v).toLocaleString()} (${pct}%)`;
              },
            },
          },
          title: {
            display: true,
            text:    cssrTxt,
            font:    { size: 14, weight: '600' },
            color:   '#2c3e50',
            padding: { bottom: 10 },
          },
        },
      },
    }
  );

  if (vendor === 'ericsson') pieEricssonChart = chart;
  else                       pieHuaweiChart   = chart;
}

// =============================================================================
// CSSR ANALYSIS — HORIZONTAL BAR CHART
// =============================================================================

function renderWorstCellsBar(rows) {
  if (barChart) { barChart.destroy(); barChart = null; }

  const wrapper = document.getElementById('worst-cells-bar-wrapper');

  if (!rows.length) {
    wrapper.innerHTML = '<p class="no-data">No data for this period</p>';
    return;
  }

  if (!document.getElementById('worst-cells-bar')) {
    wrapper.innerHTML = '<canvas id="worst-cells-bar"></canvas>';
  }

  // Dynamic height: ~22px per row, minimum 300px
  const h = Math.max(300, rows.length * 24);
  wrapper.style.height = h + 'px';

  const cssrKey  = caState.vendor === 'ERICSSON' ? 'CSSR_ERICSSON' : 'CSSR_HUAWEI';
  const availKey = caState.vendor === 'ERICSSON' ? 'CELL_AVAILABILITY_RATE_ERICSSON' : 'CELL_AVAILABILITY_RATE_HUAWEI';
  const cdrKey   = caState.vendor === 'ERICSSON' ? 'CDR_ERICSSON' : 'CDR_HUAWEI';
  const cbrKey   = caState.vendor === 'ERICSSON' ? 'CBR_ERICSSON' : 'CBR_HUAWEI';

  const labels    = rows.map(r => r[caState.level] || 'Unknown');
  const values    = rows.map(r => r['CSR_FAILURES'] ?? 0);
  const barColors = rows.map(r => {
    const cssr = r[cssrKey];
    return (cssr !== null && cssr !== undefined && parseFloat(cssr) < 99) ? '#e74c3c' : '#3498db';
  });

  barChart = new Chart(
    document.getElementById('worst-cells-bar').getContext('2d'),
    {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label:           'CSR Failures',
          data:            values,
          backgroundColor: barColors,
          borderWidth:     0,
        }],
      },
      options: {
        indexAxis:           'y',
        responsive:          true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: c => {
                const r    = rows[c.dataIndex];
                const cssr = r[cssrKey];
                const avail = r[availKey];
                const cdr  = r[cdrKey];
                const cbr  = r[cbrKey];
                return [
                  `CSR Failures: ${c.parsed.x}`,
                  `CSSR: ${cssr  !== null && cssr  !== undefined ? parseFloat(cssr).toFixed(2)  : 'N/A'}%`,
                  `Availability: ${avail !== null && avail !== undefined ? parseFloat(avail).toFixed(2) : 'N/A'}%`,
                  `CDR: ${cdr   !== null && cdr   !== undefined ? parseFloat(cdr).toFixed(2)   : 'N/A'}%`,
                  `CBR: ${cbr   !== null && cbr   !== undefined ? parseFloat(cbr).toFixed(2)   : 'N/A'}%`,
                ];
              },
            },
          },
        },
        scales: {
          x: {
            title:       { display: true, text: 'CSR Failures' },
            beginAtZero: true,
          },
          y: {
            ticks: { font: { size: 11 } },
          },
        },
      },
    }
  );
}

// =============================================================================
// CSSR ANALYSIS — UI HELPERS
// =============================================================================

function showCaLoading(on) {
  document.getElementById('cssr-loading').style.display = on ? 'flex' : 'none';
  document.getElementById('cssr-content').style.display = on ? 'none' : 'block';
}

function showCaError(msg) {
  const el = document.getElementById('ca-error-msg');
  el.textContent   = msg;
  el.style.display = 'inline';
}

function clearCaError() {
  const el = document.getElementById('ca-error-msg');
  el.textContent   = '';
  el.style.display = 'none';
}

function updateCaRange() {
  document.getElementById('ca-current-range').textContent =
    `${caState.startDate} → ${caState.endDate}`;
}
