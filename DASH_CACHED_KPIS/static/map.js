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
  CSSR: {
    ericsson:       'CSSR_ERICSSON',
    huawei:         'CSSR_HUAWEI',
    higherIsBetter: true,
    defaultThreshold: 99,
  },
  AVAILABILITY: {
    ericsson:       'CELL_AVAILABILITY_RATE_ERICSSON',
    huawei:         'CELL_AVAILABILITY_RATE_HUAWEI',
    higherIsBetter: true,
    defaultThreshold: 99,
  },
  CDR: {
    ericsson:       'CDR_ERICSSON',
    huawei:         'CDR_HUAWEI',
    higherIsBetter: false,
    defaultThreshold: 2,
  },
  CBR: {
    ericsson:       'CBR_ERICSSON',
    huawei:         'CBR_HUAWEI',
    higherIsBetter: false,
    defaultThreshold: 5,
  },
};

// ── State ─────────────────────────────────────────────────────────────────────
let mapVendor    = 'BOTH';
let selectedKpi  = 'CSSR';
let threshold    = 99;
let ericssonData = [];
let huaweiData   = [];
let leafletMap   = null;
let markersLayer = null;

// ── Init ──────────────────────────────────────────────────────────────────────
window.addEventListener('load', async () => {
  // Map centred on Cotonou / Bénin area
  leafletMap = L.map('map').setView([6.37, 2.42], 10);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright" style="color:#3498db">OpenStreetMap</a>',
    maxZoom: 19,
  }).addTo(leafletMap);

  markersLayer = L.layerGroup().addTo(leafletMap);

  // Update legend period
  document.getElementById('leg-period').textContent =
    START_DATE && END_DATE ? `${START_DATE} → ${END_DATE}` : 'No date range';

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
      `${START_DATE} → ${END_DATE}  |  Level: ${levelLabel}  |  E: ${e.length}  H: ${h.length}`;

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

  const res  = await fetch('/worst_cells?' + params.toString());
  const json = await res.json();
  if (!res.ok) throw new Error(json.detail || 'API error');
  return json.data || [];
}

// ── Render markers ────────────────────────────────────────────────────────────
function renderMarkers() {
  markersLayer.clearLayers();
  updateLegend();

  const kpiCfg = KPI_COLS[selectedKpi];
  const datasets = [];
  if (mapVendor === 'BOTH' || mapVendor === 'ERICSSON') datasets.push({ rows: ericssonData, vendor: 'ERICSSON' });
  if (mapVendor === 'BOTH' || mapVendor === 'HUAWEI')   datasets.push({ rows: huaweiData,   vendor: 'HUAWEI'   });

  let plotted = 0;
  let noCoords = 0;
  const latlngs = [];

  datasets.forEach(({ rows, vendor }) => {
    const kpiCol   = vendor === 'ERICSSON' ? kpiCfg.ericsson : kpiCfg.huawei;
    const cssrCol  = vendor === 'ERICSSON' ? 'CSSR_ERICSSON' : 'CSSR_HUAWEI';
    const availCol = vendor === 'ERICSSON' ? 'CELL_AVAILABILITY_RATE_ERICSSON' : 'CELL_AVAILABILITY_RATE_HUAWEI';
    const cdrCol   = vendor === 'ERICSSON' ? 'CDR_ERICSSON' : 'CDR_HUAWEI';
    const cbrCol   = vendor === 'ERICSSON' ? 'CBR_ERICSSON' : 'CBR_HUAWEI';

    rows.forEach(row => {
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

      const marker = L.circleMarker([lat, lng], {
        radius:      7,
        fillColor:   color,
        color:       '#fff',
        weight:      1.5,
        fillOpacity: 0.85,
      });

      // Name label
      const nameCol  = LEVEL === 'site_name'       ? 'site_name'
                     : LEVEL === 'commune'          ? 'commune'
                     : LEVEL === 'arrondissement'   ? 'arrondissement'
                     : LEVEL === 'departement'      ? 'departement'
                     : LEVEL === 'controller_name'  ? 'controller_name'
                     : 'cell_name';
      const name = row[nameCol] || row['cell_name'] || row['site_name'] || 'Unknown';

      const f2 = v => (v !== null && v !== undefined) ? parseFloat(v).toFixed(2) : 'N/A';

      const tooltipHtml = [
        `<b>${name}</b> <span style="color:#3498db;font-size:11px;">[${vendor}]</span>`,
        `<b>CSSR:</b> ${f2(row[cssrCol])}%`,
        `<b>Availability:</b> ${f2(row[availCol])}%`,
        `<b>CDR:</b> ${f2(row[cdrCol])}%`,
        `<b>CBR:</b> ${f2(row[cbrCol])}%`,
        `<b>CSR Failures:</b> ${row['CSR_FAILURES'] ?? 'N/A'}`,
        row['commune']        ? `<b>Commune:</b> ${row['commune']}` : null,
        row['arrondissement'] ? `<b>Arrondissement:</b> ${row['arrondissement']}` : null,
        row['site_name']      ? `<b>Site:</b> ${row['site_name']}` : null,
        row['controller_name'] ? `<b>Controller:</b> ${row['controller_name']}` : null,
      ].filter(Boolean).join('<br>');

      marker.bindTooltip(tooltipHtml, { sticky: true, opacity: 0.97 });
      marker.addTo(markersLayer);

      latlngs.push([lat, lng]);
      plotted++;
    });
  });

  document.getElementById('map-status').textContent =
    `${plotted} cells plotted` + (noCoords > 0 ? ` · ${noCoords} without coordinates` : '');

  if (latlngs.length > 0) {
    leafletMap.fitBounds(L.latLngBounds(latlngs), { padding: [40, 40], maxZoom: 14 });
  }
}

// ── Legend update ─────────────────────────────────────────────────────────────
function updateLegend() {
  const cfg = KPI_COLS[selectedKpi];
  const dir = cfg.higherIsBetter ? '<' : '>';
  const dirOpp = cfg.higherIsBetter ? '≥' : '≤';

  document.getElementById('threshold-dir').textContent =
    cfg.higherIsBetter ? '(< bad)' : '(> bad)';
  document.getElementById('leg-bad').textContent =
    `${selectedKpi} ${dir} ${threshold}`;
  document.getElementById('leg-good').textContent =
    `${selectedKpi} ${dirOpp} ${threshold}`;
}
