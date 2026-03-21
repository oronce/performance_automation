/**
 * Cell Map View — Leaflet
 * Opens from CSSR Analysis section with URL params:
 *   start_date, end_date, level, time_start, time_end
 */

// ── URL params ────────────────────────────────────────────────────────────────
const urlParams  = new URLSearchParams(window.location.search);
const START_DATE = urlParams.get('start_date') || '';
const END_DATE   = urlParams.get('end_date')   || '';
const LEVEL      = urlParams.get('level')      || 'cell_name';
const TIME_START = urlParams.get('time_start') || '';
const TIME_END   = urlParams.get('time_end')   || '';

// ── KPI column mapping per vendor ─────────────────────────────────────────────
const KPI_COLS = {
  CSSR:         { ericsson: 'CSSR_ERICSSON',                   huawei: 'CSSR_HUAWEI',                      higherIsBetter: true,  defaultThreshold: 99  },
  AVAILABILITY: { ericsson: 'CELL_AVAILABILITY_RATE_ERICSSON', huawei: 'CELL_AVAILABILITY_RATE_HUAWEI',    higherIsBetter: true,  defaultThreshold: 99  },
  CDR:          { ericsson: 'CDR_ERICSSON',                    huawei: 'CDR_HUAWEI',                       higherIsBetter: false, defaultThreshold: 2   },
  CBR:          { ericsson: 'CBR_ERICSSON',                    huawei: 'CBR_HUAWEI',                       higherIsBetter: false, defaultThreshold: 5   },
  TCH_CONG:     { ericsson: 'TCH_CONGESTION_RATE_ERICSSON',    huawei: 'TCH_CONGESTION_RATE_HUAWEI',       higherIsBetter: false, defaultThreshold: 2   },
  SDCCH_DROP:   { ericsson: 'SDCCH_DROP_RATE_ERICSSON',        huawei: 'SDCCH_DROP_RATE_HUAWEI',           higherIsBetter: false, defaultThreshold: 1   },
  SDCCH_CONG:   { ericsson: 'SDCCH_CONGESTION_RATE_ERICSSON',  huawei: 'SDCCH_CONGESTION_RATE_HUAWEI',    higherIsBetter: false, defaultThreshold: 2   },
  TRAFFIC_VOIX: { ericsson: 'TRAFFIC_VOIX_ERICSSON',           huawei: 'TRAFFIC_VOIX_HUAWEI',              higherIsBetter: true,  defaultThreshold: 0   },
};

// ── Per-vendor tooltip column definitions ─────────────────────────────────────
const TOOLTIP_COLS = {
  ERICSSON: [
    { col: 'CSSR_ERICSSON',                   label: 'CSSR',             unit: '%'   },
    { col: 'CDR_ERICSSON',                    label: 'CDR',              unit: '%'   },
    { col: 'CBR_ERICSSON',                    label: 'CBR',              unit: '%'   },
    { col: 'CELL_AVAILABILITY_RATE_ERICSSON', label: 'Cell Avail.',      unit: '%'   },
    { col: 'TCH_AVAILABILITY_RATE_ERICSSON',  label: 'TCH Avail.',       unit: '%'   },
    { col: 'TCH_CONGESTION_RATE_ERICSSON',    label: 'TCH Congestion',   unit: '%'   },
    { col: 'SDCCH_DROP_RATE_ERICSSON',        label: 'SDCCH Drop',       unit: '%'   },
    { col: 'SDCCH_BLOCKING_RATE_ERICSSON',    label: 'SDCCH Block',      unit: '%'   },
    { col: 'SDCCH_CONGESTION_RATE_ERICSSON',  label: 'SDCCH Cong.',      unit: '%'   },
    { col: 'SDCCH_TRAFFIC_ERICSSON',          label: 'SDCCH Traffic',    unit: ' Erl'},
    { col: 'TRAFFIC_VOIX_ERICSSON',           label: 'Voice Traffic',    unit: ' Erl'},
    { col: 'TRAFFIC_DATA_GB_ERICSSON',        label: 'Data Traffic',     unit: ' GB' },
    { col: 'DOWNTIME_MANUAL',                 label: 'Downtime Manual',  unit: ' h'  },
    { col: 'CSR_FAILURES',                    label: 'CSR Failures',     unit: ''    },
  ],
  HUAWEI: [
    { col: 'CSSR_HUAWEI',                         label: 'CSSR',             unit: '%'   },
    { col: 'CDR_HUAWEI',                          label: 'CDR',              unit: '%'   },
    { col: 'CBR_HUAWEI',                          label: 'CBR',              unit: '%'   },
    { col: 'CELL_AVAILABILITY_RATE_HUAWEI',       label: 'Cell Avail.',      unit: '%'   },
    { col: 'TCH_CONGESTION_RATE_HUAWEI',          label: 'TCH Congestion',   unit: '%'   },
    { col: 'TCH_ASSIGNMENT_SUCCESS_RATE_HUAWEI',  label: 'TCH Assign SR',    unit: '%'   },
    { col: 'SDCCH_DROP_RATE_HUAWEI',              label: 'SDCCH Drop',       unit: '%'   },
    { col: 'SDCCH_CONGESTION_RATE_HUAWEI',        label: 'SDCCH Cong.',      unit: '%'   },
    { col: 'SDCCH_TRAFFIC_HUAWEI',                label: 'SDCCH Traffic',    unit: ' Erl'},
    { col: 'TRAFFIC_VOIX_HUAWEI',                 label: 'Voice Traffic',    unit: ' Erl'},
    { col: 'HANDOVER_SUCCESS_RATE_HUAWEI',        label: 'Handover SR',      unit: '%'   },
    { col: 'CSR_FAILURES',                        label: 'CSR Failures',     unit: ''    },
  ],
};

function buildTooltipHtml(row, vendor, name) {
  const f = v => (v != null && v !== '') ? parseFloat(v).toFixed(2) : null;
  const cols = TOOLTIP_COLS[vendor] || [];
  const lines = [
    `<b>${name}</b> <span style="color:#3498db;font-size:11px;">[${vendor}]</span>`,
    `<hr style="border:none;border-top:1px solid #2c3e50;margin:4px 0;">`,
  ];
  cols.forEach(({ col, label, unit }) => {
    const v = f(row[col]);
    if (v !== null) lines.push(`<b>${label}:</b> ${v}${unit}`);
  });
  // Geo context (only add if available and not already the label)
  if (row['commune'])         lines.push(`<b>Commune:</b> ${row['commune']}`);
  if (row['arrondissement'])  lines.push(`<b>Arrond.:</b> ${row['arrondissement']}`);
  if (row['site_name'])       lines.push(`<b>Site:</b> ${row['site_name']}`);
  if (row['controller_name']) lines.push(`<b>Controller:</b> ${row['controller_name']}`);
  return lines.join('<br>');
}

// ── State ─────────────────────────────────────────────────────────────────────
let mapVendor    = 'BOTH';
let selectedKpi  = 'CSSR';
let threshold    = 99;
let topN         = 50;   // 0 = show all; otherwise top N worst by CSSR
let ericssonData = [];
let huaweiData   = [];
let leafletMap   = null;
let markersLayer = null;

// ── Init ──────────────────────────────────────────────────────────────────────
window.addEventListener('load', async () => {
  // Map centred on Cotonou / Bénin area
  leafletMap = L.map('map').setView([6.37, 2.42], 10);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" style="color:#3498db">OpenStreetMap</a>',
    maxZoom: 19,
  }).addTo(leafletMap);

  markersLayer = L.layerGroup().addTo(leafletMap);

  // Update legend period
  document.getElementById('leg-period').textContent =
    START_DATE && END_DATE ? `${START_DATE} \u2192 ${END_DATE}` : 'No date range';

  bindToolbar();
  await loadData();
});

// ── Toolbar bindings ──────────────────────────────────────────────────────────
function bindToolbar() {
  document.getElementById('kpi-select').addEventListener('change', e => {
    selectedKpi = e.target.value;
    threshold   = parseFloat(document.getElementById('threshold-input').value)
                  || KPI_COLS[selectedKpi].defaultThreshold;
    document.getElementById('threshold-input').value = threshold;
    updateLegend();
    renderMarkers();
  });

  document.getElementById('threshold-input').addEventListener('change', e => {
    threshold = parseFloat(e.target.value) || KPI_COLS[selectedKpi].defaultThreshold;
    updateLegend();
    renderMarkers();
  });

  document.querySelectorAll('[data-map-vendor]').forEach(btn => {
    btn.addEventListener('click', () => {
      mapVendor = btn.dataset.mapVendor;
      document.querySelectorAll('[data-map-vendor]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderMarkers();
    });
  });

  document.getElementById('top-n-select').addEventListener('change', e => {
    topN = parseInt(e.target.value) || 0;
    renderMarkers();
  });
}

// ── Load data from API ────────────────────────────────────────────────────────
async function loadData() {
  try {
    const [e, h] = await Promise.all([
      fetchCells('2g_ericsson_worst_cell'),
      fetchCells('2g_huawei_worst_cell'),
    ]);
    ericssonData = e;
    huaweiData   = h;

    const levelLabel = LEVEL.replace(/_/g, ' ');
    document.getElementById('tb-info').textContent =
      `${START_DATE} \u2192 ${END_DATE}  |  Level: ${levelLabel}  |  E: ${e.length}  H: ${h.length} total`;

    renderMarkers();
  } catch (err) {
    document.getElementById('map-status').textContent = 'Error: ' + err.message;
    console.error(err);
  } finally {
    document.getElementById('map-loading').style.display = 'none';
  }
}

async function fetchCells(script) {
  const params = new URLSearchParams({
    script,
    start_date:        START_DATE,
    end_date:          END_DATE,
    aggregation_level: LEVEL,
  });
  if (TIME_START) params.set('time_start', TIME_START);
  if (TIME_END)   params.set('time_end',   TIME_END);

  const res  = await fetch('/api/worst-cells?' + params.toString());
  const json = await res.json();
  if (!res.ok) throw new Error(json.detail || 'API error');
  return json.data || [];
}

// ── Sector spread — fans co-located cells around their shared site point ──────
// At cell level, multiple cells share the same site coordinates (same tower,
// different antenna directions).  We offset each cell radially so all are
// individually visible and hoverable on the map.
//
//   SPREAD_RADIUS ≈ 0.0025° ≈ ~275 m  — enough separation at zoom 12-14
//   Angles start from North (–90°) and are distributed evenly around 360°.
//
function applySectorSpread(rows) {
  if (LEVEL !== 'cell_name') return; // only needed at cell level

  // Group row indices by rounded coordinate key
  const coordMap = new Map();
  rows.forEach((row, i) => {
    const lat = parseFloat(row['latitude']  ?? row['LATITUDE']  ?? '');
    const lng = parseFloat(row['longitude'] ?? row['LONGITUDE'] ?? '');
    if (!isFinite(lat) || !isFinite(lng) || lat === 0 || lng === 0) return;
    const key = `${lat.toFixed(5)},${lng.toFixed(5)}`;
    if (!coordMap.has(key)) coordMap.set(key, []);
    coordMap.get(key).push(i);
  });

  const SPREAD_RADIUS = 0.0002; // degrees (~22 m) — tight visual offset only

  coordMap.forEach(indices => {
    if (indices.length < 2) return; // no overlap, nothing to do
    const n = indices.length;
    indices.forEach((rowIdx, k) => {
      // Start from North (–90°), spread evenly
      const angleDeg = (360 / n) * k - 90;
      const angleRad = angleDeg * Math.PI / 180;
      const row = rows[rowIdx];
      const baseLat = parseFloat(row['latitude']  ?? row['LATITUDE']);
      const baseLng = parseFloat(row['longitude'] ?? row['LONGITUDE']);
      row._lat = baseLat + SPREAD_RADIUS * Math.cos(angleRad);
      row._lng = baseLng + SPREAD_RADIUS * Math.sin(angleRad);
    });
  });
}

// ── Render markers ────────────────────────────────────────────────────────────
function renderMarkers() {
  markersLayer.clearLayers();
  updateLegend();

  const kpiCfg = KPI_COLS[selectedKpi];

  // Top N worst by CSR Failures count (highest = worst), same ranking as the bar chart
  function applyTopN(rows) {
    if (!topN) return rows; // 0 = all
    return [...rows]
      .sort((a, b) => (parseFloat(b['CSR_FAILURES']) || 0) - (parseFloat(a['CSR_FAILURES']) || 0))
      .slice(0, topN);
  }

  const datasets = [];
  if (mapVendor === 'BOTH' || mapVendor === 'ERICSSON') datasets.push({ rows: applyTopN(ericssonData), vendor: 'ERICSSON' });
  if (mapVendor === 'BOTH' || mapVendor === 'HUAWEI')   datasets.push({ rows: applyTopN(huaweiData),   vendor: 'HUAWEI'   });

  // Apply sector spread to all datasets before plotting
  datasets.forEach(({ rows }) => applySectorSpread(rows));

  let plotted  = 0;
  let noCoords = 0;
  const latlngs = [];

  datasets.forEach(({ rows, vendor }) => {
    const kpiCol = vendor === 'ERICSSON' ? kpiCfg.ericsson : kpiCfg.huawei;

    rows.forEach(row => {
      // Use spread coordinates if set, otherwise fall back to raw coordinates
      const lat = row._lat ?? parseFloat(row['latitude']  ?? row['LATITUDE']  ?? '');
      const lng = row._lng ?? parseFloat(row['longitude'] ?? row['LONGITUDE'] ?? '');
      if (!isFinite(lat) || !isFinite(lng) || lat === 0 || lng === 0) {
        noCoords++;
        return;
      }

      const kpiVal = row[kpiCol];
      let color;
      if (kpiVal === null || kpiVal === undefined) {
        color = '#95a5a6';
      } else {
        const v     = parseFloat(kpiVal);
        const isBad = kpiCfg.higherIsBetter ? v < threshold : v > threshold;
        color = isBad ? '#e74c3c' : '#2ecc71';
      }

      const marker = L.circleMarker([lat, lng], {
        radius:      7,
        fillColor:   color,
        color:       '#fff',
        weight:      1.5,
        fillOpacity: 0.85,
      });

      const nameCol = LEVEL === 'site_name'      ? 'site_name'
                    : LEVEL === 'controller_name' ? 'controller_name'
                    : 'cell_name';
      const name = row[nameCol] || row['cell_name'] || row['site_name'] || 'Unknown';

      marker.bindTooltip(buildTooltipHtml(row, vendor, name), { sticky: true, opacity: 0.97 });
      marker.addTo(markersLayer);

      latlngs.push([lat, lng]);
      plotted++;
    });
  });

  const topNLabel = topN ? ` \u00b7 Top ${topN} highest CSR Failures per vendor` : '';
  document.getElementById('map-status').textContent =
    `${plotted} cells plotted${topNLabel}` + (noCoords > 0 ? ` \u00b7 ${noCoords} without coordinates` : '');

  if (latlngs.length > 0) {
    leafletMap.fitBounds(L.latLngBounds(latlngs), { padding: [40, 40], maxZoom: 14 });
  }
}

// ── Legend update ─────────────────────────────────────────────────────────────
function updateLegend() {
  const cfg    = KPI_COLS[selectedKpi];
  const dir    = cfg.higherIsBetter ? '<' : '>';
  const dirOpp = cfg.higherIsBetter ? '\u2265' : '\u2264';

  document.getElementById('threshold-dir').textContent =
    cfg.higherIsBetter ? '(< bad)' : '(> bad)';
  document.getElementById('leg-bad').textContent =
    `${selectedKpi} ${dir} ${threshold}`;
  document.getElementById('leg-good').textContent =
    `${selectedKpi} ${dirOpp} ${threshold}`;
}
