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
const CA_TOKEN   = urlParams.get('ca_token')   || ''; // CA_LOCK — passed from parent tab

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
  const row_ = (label, value) =>
    `<div style="display:flex;justify-content:space-between;gap:10px;padding:1px 0;">` +
    `<span style="color:#bdc3c7;">${label}</span>` +
    `<span style="font-weight:600;color:#ecf0f1;">${value}</span></div>`;
  const sep = `<div style="border-top:1px solid rgba(255,255,255,0.12);margin:4px 0;"></div>`;

  let html = `<div style="font-weight:700;font-size:12px;color:#3498db;margin-bottom:4px;">${name}</div>`;
  html += `<div style="font-size:10px;color:#7f8c8d;margin-bottom:4px;">${vendor}</div>`;
  html += sep;

  const cols = TOOLTIP_COLS[vendor] || [];
  cols.forEach(({ col, label, unit }) => {
    const v = f(row[col]);
    if (v !== null) html += row_(label, v + unit);
  });

  // Geo block
  const geo = [];
  if (row['site_name'])       geo.push(row_('Site',       row['site_name']));
  if (row['controller_name']) geo.push(row_('Controller', row['controller_name']));
  if (row['commune'])         geo.push(row_('Commune',    row['commune']));
  if (row['arrondissement'])  geo.push(row_('Arrond.',    row['arrondissement']));
  const azReal = parseFloat(row['azimuth']);
  if (isFinite(azReal)) {
    geo.push(row_('Azimuth', azReal + '°'));
  } else if (row._azimuth !== undefined) {
    geo.push(row_('Azimuth', Math.round(row._azimuth) + '° <span style="color:#f39c12;">(auto)</span>'));
  }
  if (geo.length) { html += sep; html += geo.join(''); }

  return `<div style="font-size:11px;line-height:1.55;max-height:240px;overflow-y:auto;min-width:180px;max-width:230px;">${html}</div>`;
}

// ── State ─────────────────────────────────────────────────────────────────────
let mapVendor       = 'BOTH';
let selectedKpi     = 'CSSR';
let threshold       = 99;
let topN            = 50;
let showRank   = false;
let sectorMode = false;  // true = antenna sector beams, false = dot markers
let searchText    = '';
let filterDept       = '';
let filterCommune    = '';
let filterArrond     = '';
let filterSite       = '';
let filterController = '';
let ericssonData  = [];
let huaweiData    = [];
let leafletMap    = null;
let markersLayer  = null;

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

  // Show/hide toolbar groups based on aggregation level
  // View mode (sectors/dots) — cell level only
  if (LEVEL !== 'cell_name') document.getElementById('grp-view-mode').style.display = 'none';
  // Site filter — cell level only
  if (LEVEL !== 'cell_name') document.getElementById('grp-filter-site').style.display = 'none';
  // Arrondissement filter — only levels that return arrondissement data
  if (!['cell_name','site_name','arrondissement'].includes(LEVEL))
    document.getElementById('grp-filter-arrond').style.display = 'none';
  // Département & Commune — hide for controller_name
  if (LEVEL === 'controller_name') document.getElementById('grp-filter-dept').style.display    = 'none';
  if (LEVEL === 'controller_name') document.getElementById('grp-filter-commune').style.display = 'none';
  // Controller filter — only for cell_name, site_name, controller_name
  if (!['cell_name','site_name','controller_name'].includes(LEVEL))
    document.getElementById('grp-filter-controller').style.display = 'none';

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

  document.getElementById('map-search').addEventListener('input', e => {
    searchText = e.target.value.trim().toLowerCase();
    renderMarkers();
  });

  document.querySelectorAll('[data-map-view]').forEach(btn => {
    btn.addEventListener('click', () => {
      sectorMode = btn.dataset.mapView === 'sector';
      document.querySelectorAll('[data-map-view]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderMarkers();
    });
  });

  document.getElementById('map-filter-dept').addEventListener('input', e => {
    filterDept = e.target.value.trim();
    renderMarkers();
  });

  document.getElementById('map-filter-commune').addEventListener('input', e => {
    filterCommune = e.target.value.trim();
    renderMarkers();
  });

  document.getElementById('map-filter-arrond').addEventListener('input', e => {
    filterArrond = e.target.value.trim();
    renderMarkers();
  });

  document.getElementById('map-filter-site').addEventListener('input', e => {
    filterSite = e.target.value.trim();
    renderMarkers();
  });

  document.getElementById('map-filter-controller').addEventListener('input', e => {
    filterController = e.target.value.trim();
    renderMarkers();
  });

  document.getElementById('map-show-rank').addEventListener('change', e => {
    showRank = e.target.checked;
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

    populateFilters([...ericssonData, ...huaweiData]);
    renderMarkers();
  } catch (err) {
    document.getElementById('map-status').textContent = 'Error: ' + err.message;
    console.error(err);
  } finally {
    document.getElementById('map-loading').style.display = 'none';
  }
}

// ── Populate filter dropdowns from loaded data ────────────────────────────────
function populateFilters(allRows) {
  const nameCol     = LEVEL === 'site_name' ? 'site_name' : 'cell_name';
  const names       = [...new Set(allRows.map(r => r[nameCol]).filter(Boolean))].sort();
  const depts       = [...new Set(allRows.map(r => r['departement']).filter(Boolean))].sort();
  const communes    = [...new Set(allRows.map(r => r['commune']).filter(Boolean))].sort();
  const arronds     = [...new Set(allRows.map(r => r['arrondissement']).filter(Boolean))].sort();
  const sites       = [...new Set(allRows.map(r => r['site_name']).filter(Boolean))].sort();
  const controllers = [...new Set(allRows.map(r => r['controller_name']).filter(Boolean))].sort();

  const fill = (datalistId, values) => {
    document.getElementById(datalistId).innerHTML =
      values.map(v => `<option value="${v}">`).join('');
  };

  fill('map-search-list',       names);
  fill('list-filter-dept',      depts);
  fill('list-filter-commune',   communes);
  fill('list-filter-arrond',    arronds);
  fill('list-filter-site',      sites);
  fill('list-filter-controller', controllers);
}

// ── Apply search + filters to a dataset ──────────────────────────────────────
function applyFilters(rows) {
  const nameCol = LEVEL === 'site_name' ? 'site_name' : 'cell_name';
  const inc = (val, filter) => (val || '').toLowerCase().includes(filter.toLowerCase());
  return rows.filter(row => {
    if (searchText       && !inc(row[nameCol],            searchText))       return false;
    if (filterDept       && !inc(row['departement'],      filterDept))       return false;
    if (filterCommune    && !inc(row['commune'],          filterCommune))    return false;
    if (filterArrond     && !inc(row['arrondissement'],   filterArrond))     return false;
    if (filterSite       && !inc(row['site_name'],        filterSite))       return false;
    if (filterController && !inc(row['controller_name'],  filterController)) return false;
    return true;
  });
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

  const res  = await fetch('/api/worst-cells?' + params.toString(), {
    headers: { 'X-CA-Token': CA_TOKEN }
  });
  const json = await res.json();
  if (!res.ok) throw new Error(json.detail || 'API error');
  return json.data || [];
}

// ── Sector beam drawing ───────────────────────────────────────────────────────
const SECTOR_BEAM_DEG  = 65;   // beam width in degrees
const SECTOR_RADIUS_M  = 400;  // sector arc radius in metres
const SECTOR_ARC_STEPS = 18;   // polygon smoothness

// Approximate metre → degree conversions
function mToDegLat(m)      { return m / 111320; }
function mToDegLng(m, lat) { return m / (111320 * Math.cos(lat * Math.PI / 180)); }

/**
 * Build [lat, lng] polygon points for a sector wedge.
 * azimuthDeg: telecom convention — 0 = North, 90 = East, clockwise.
 */
function sectorPoints(lat, lng, azimuthDeg, beamDeg, radiusM) {
  const half   = beamDeg / 2;
  const startA = azimuthDeg - half;
  const endA   = azimuthDeg + half;
  const pts    = [[lat, lng]]; // apex = tower location

  for (let i = 0; i <= SECTOR_ARC_STEPS; i++) {
    const deg = startA + (endA - startA) * (i / SECTOR_ARC_STEPS);
    const rad = deg * Math.PI / 180;
    // azimuth 0° = North (+lat), 90° = East (+lng)
    pts.push([
      lat + mToDegLat(radiusM) * Math.cos(rad),
      lng + mToDegLng(radiusM, lat) * Math.sin(rad),
    ]);
  }

  pts.push([lat, lng]); // close back to apex
  return pts;
}

/**
 * Return the midpoint of the largest angular gap in a sorted list of
 * angles (degrees, 0–360).  Used to place virtual azimuths for cells
 * that have no azimuth defined.
 */
function largestGapMidpoint(sorted) {
  if (sorted.length === 0) return 0;
  if (sorted.length === 1) return (sorted[0] + 180) % 360;

  let maxGap = 0, bestStart = 0;
  for (let i = 0; i < sorted.length; i++) {
    const next = sorted[(i + 1) % sorted.length];
    const gap  = ((next - sorted[i]) + 360) % 360;
    if (gap > maxGap) { maxGap = gap; bestStart = sorted[i]; }
  }
  return (bestStart + maxGap / 2) % 360;
}

/**
 * Assign row._azimuth to every cell row:
 *   - defined azimuth → use it
 *   - missing azimuth → auto-compute from the largest gap among siblings
 *                       at the same site, so sectors never overlap
 */
function assignAzimuths(rows) {
  if (LEVEL !== 'cell_name') return;

  // Group by site_name (fall back to rounded coordinate key)
  const siteMap = new Map();
  rows.forEach((row, i) => {
    const key = row['site_name'] ||
      `${parseFloat(row['latitude']  || 0).toFixed(4)},` +
      `${parseFloat(row['longitude'] || 0).toFixed(4)}`;
    if (!siteMap.has(key)) siteMap.set(key, []);
    siteMap.get(key).push(i);
  });

  siteMap.forEach(indices => {
    // Normalised defined azimuths for this site (sorted)
    const defined = indices
      .map(i => parseFloat(rows[i]['azimuth']))
      .filter(v => isFinite(v))
      .map(v => ((v % 360) + 360) % 360)
      .sort((a, b) => a - b);

    // Working copy that grows as we assign virtual azimuths
    const taken = [...defined];

    indices.forEach(i => {
      const raw = parseFloat(rows[i]['azimuth']);
      if (isFinite(raw)) {
        rows[i]._azimuth = ((raw % 360) + 360) % 360;
      } else {
        const az = largestGapMidpoint(taken);
        rows[i]._azimuth = az;
        // Register so the next unassigned cell at this site avoids it too
        taken.push(az);
        taken.sort((a, b) => a - b);
      }
    });
  });
}

// ── Render markers ────────────────────────────────────────────────────────────
function renderMarkers() {
  markersLayer.clearLayers();
  updateLegend();

  const kpiCfg = KPI_COLS[selectedKpi];

  // Filters → sort by CSR_FAILURES → topN
  function prepareRows(rows) {
    let r = applyFilters(rows);
    r = [...r].sort((a, b) => (parseFloat(b['CSR_FAILURES']) || 0) - (parseFloat(a['CSR_FAILURES']) || 0));
    if (topN) r = r.slice(0, topN);
    return r;
  }

  const datasets = [];
  if (mapVendor === 'BOTH' || mapVendor === 'ERICSSON') datasets.push({ rows: prepareRows(ericssonData), vendor: 'ERICSSON' });
  if (mapVendor === 'BOTH' || mapVendor === 'HUAWEI')   datasets.push({ rows: prepareRows(huaweiData),   vendor: 'HUAWEI'   });

  // Assign azimuths (real or auto-computed) for cell-level rendering
  datasets.forEach(({ rows }) => assignAzimuths(rows));

  let plotted  = 0;
  let noCoords = 0;
  const latlngs = [];

  datasets.forEach(({ rows, vendor }) => {
    const kpiCol = vendor === 'ERICSSON' ? kpiCfg.ericsson : kpiCfg.huawei;

    rows.forEach((row, idx) => {
      const rank = idx + 1;

      const lat = parseFloat(row['latitude']  ?? row['LATITUDE']  ?? '');
      const lng = parseFloat(row['longitude'] ?? row['LONGITUDE'] ?? '');
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

      const borderColor = color === '#e74c3c' ? '#c0392b'
                        : color === '#2ecc71' ? '#27ae60'
                        : '#7f8c8d';

      const nameCol = LEVEL === 'site_name'      ? 'site_name'
                    : LEVEL === 'controller_name' ? 'controller_name'
                    : 'cell_name';
      const name = row[nameCol] || row['cell_name'] || row['site_name'] || 'Unknown';

      const tooltipHtml = buildTooltipHtml(row, vendor, name);
      let marker;

      if (LEVEL === 'cell_name' && sectorMode) {
        // ── Draw antenna sector beam ──────────────────────────────────────────
        const az = row._azimuth ?? 0;
        const R  = SECTOR_RADIUS_M;
        const pts = sectorPoints(lat, lng, az, SECTOR_BEAM_DEG, R);

        marker = L.polygon(pts, {
          fillColor:   color,
          color:       borderColor,
          weight:      1.5,
          fillOpacity: 0.65,
          opacity:     0.9,
        });

        marker.bindTooltip(tooltipHtml, { sticky: true, opacity: 0.97 });
        marker.addTo(markersLayer);

        // Rank label: small circle at ~60 % of radius along azimuth direction
        if (showRank) {
          const rad      = az * Math.PI / 180;
          const labelLat = lat + mToDegLat(R * 0.58) * Math.cos(rad);
          const labelLng = lng + mToDegLng(R * 0.58, lat) * Math.sin(rad);
          const rankIcon = L.divIcon({
            className: '',
            html: `<div style="background:${color};color:#fff;border:1.5px solid rgba(255,255,255,0.9);border-radius:50%;width:18px;height:18px;display:flex;align-items:center;justify-content:center;font-size:8px;font-weight:700;box-shadow:0 1px 4px rgba(0,0,0,0.5);line-height:1;pointer-events:none;">${rank}</div>`,
            iconSize:   [18, 18],
            iconAnchor: [9, 9],
          });
          L.marker([labelLat, labelLng], { icon: rankIcon, interactive: false }).addTo(markersLayer);
        }

      } else {
        // ── Non-cell levels: keep simple circle markers ───────────────────────
        if (showRank) {
          const icon = L.divIcon({
            className: '',
            html: `<div style="background:${color};color:#fff;border:2px solid rgba(255,255,255,0.9);border-radius:50%;width:22px;height:22px;display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:700;box-shadow:0 1px 4px rgba(0,0,0,0.45);line-height:1">${rank}</div>`,
            iconSize:   [22, 22],
            iconAnchor: [11, 11],
          });
          marker = L.marker([lat, lng], { icon });
        } else {
          marker = L.circleMarker([lat, lng], {
            radius:      7,
            fillColor:   color,
            color:       '#fff',
            weight:      1.5,
            fillOpacity: 0.85,
          });
        }
        marker.bindTooltip(tooltipHtml, { sticky: true, opacity: 0.97 });
        marker.addTo(markersLayer);
      }

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
