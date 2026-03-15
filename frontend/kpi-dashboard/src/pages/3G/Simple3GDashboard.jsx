import React, { useState, useMemo } from 'react';
import Plot from 'react-plotly.js';
import PlotlyChart from '../../components/PlotlyChart';
import PivotControls from '../../components/PivotControls';
import { transformDataWithCombinedAxis } from '../../utils/chartUtils';

const Simple3GDashboard = () => {
  // Available fields from data
  const availableFields = ['date', 'time'];
  const availableKPIs = ['CSSR_HUAWEI', 'CDR_HUAWEI'];

  // State for pivot controls
  const [xAxisFields, setXAxisFields] = useState(['date', 'time']);
  const [legendFields, setLegendFields] = useState([]);
  const [selectedKPIs, setSelectedKPIs] = useState(['CSSR_HUAWEI']);

  // State for chart layout customization
  const [layoutSettings, setLayoutSettings] = useState({
    nticks: 25,
    tickangle: -45,
    tickfontsize: 10,
  });

  // Log current state
  console.log('[COMPONENT STATE] X-Axis Fields:', xAxisFields);
  console.log('[COMPONENT STATE] Legend Fields:', legendFields);
  console.log('[COMPONENT STATE] Selected KPIs:', selectedKPIs);

  // Hardcoded sample data
  const rawData = [
    { date: '2025-12-10', time: '00:00:00', CSSR_HUAWEI: 99.65474513, CDR_HUAWEI: 0.13568049 },
    { date: '2025-12-10', time: '01:00:00', CSSR_HUAWEI: 99.713447, CDR_HUAWEI: 0.059683677 },
    { date: '2025-12-10', time: '02:00:00', CSSR_HUAWEI: 99.80969003, CDR_HUAWEI: 0.137488543 },
    { date: '2025-12-10', time: '03:00:00', CSSR_HUAWEI: 99.81227515, CDR_HUAWEI: 0.030165913 },
    { date: '2025-12-10', time: '04:00:00', CSSR_HUAWEI: 99.50679922, CDR_HUAWEI: 0.048437878 },
    { date: '2025-12-10', time: '05:00:00', CSSR_HUAWEI: 99.72471554, CDR_HUAWEI: 0.046943949 },
    { date: '2025-12-10', time: '06:00:00', CSSR_HUAWEI: 99.75336407, CDR_HUAWEI: 0.060634724 },
    { date: '2025-12-10', time: '07:00:00', CSSR_HUAWEI: 99.57502335, CDR_HUAWEI: 0.072051101 },
    { date: '2025-12-10', time: '08:00:00', CSSR_HUAWEI: 99.58837816, CDR_HUAWEI: 0.063182109 },
    { date: '2025-12-10', time: '09:00:00', CSSR_HUAWEI: 99.6199144, CDR_HUAWEI: 0.062607058 },
    { date: '2025-12-10', time: '10:00:00', CSSR_HUAWEI: 99.64855164, CDR_HUAWEI: 0.064918411 },
    { date: '2025-12-10', time: '11:00:00', CSSR_HUAWEI: 99.63638898, CDR_HUAWEI: 0.060237458 },
    { date: '2025-12-10', time: '12:00:00', CSSR_HUAWEI: 99.66107512, CDR_HUAWEI: 0.058395974 },
    { date: '2025-12-10', time: '13:00:00', CSSR_HUAWEI: 99.65309823, CDR_HUAWEI: 0.06509352 },
    { date: '2025-12-10', time: '14:00:00', CSSR_HUAWEI: 99.73001315, CDR_HUAWEI: 0.053401723 },
    { date: '2025-12-10', time: '15:00:00', CSSR_HUAWEI: 99.63815419, CDR_HUAWEI: 0.059119222 },
    { date: '2025-12-10', time: '16:00:00', CSSR_HUAWEI: 99.63089936, CDR_HUAWEI: 0.05497645 },
    { date: '2025-12-10', time: '17:00:00', CSSR_HUAWEI: 99.59342576, CDR_HUAWEI: 0.05950986 },
    { date: '2025-12-10', time: '18:00:00', CSSR_HUAWEI: 99.410775, CDR_HUAWEI: 0.066463792 },
    { date: '2025-12-10', time: '19:00:00', CSSR_HUAWEI: 99.16023089, CDR_HUAWEI: 0.065607297 },
    { date: '2025-12-10', time: '20:00:00', CSSR_HUAWEI: 99.05112119, CDR_HUAWEI: 0.074936895 },
    { date: '2025-12-10', time: '21:00:00', CSSR_HUAWEI: 99.02729064, CDR_HUAWEI: 0.167977655 },
    { date: '2025-12-10', time: '22:00:00', CSSR_HUAWEI: 99.40977624, CDR_HUAWEI: 0.093975876 },
    { date: '2025-12-10', time: '23:00:00', CSSR_HUAWEI: 99.62786758, CDR_HUAWEI: 0.080669283 },
    { date: '2025-12-11', time: '00:00:00', CSSR_HUAWEI: 99.73331203, CDR_HUAWEI: 0.071530758 },
    { date: '2025-12-11', time: '01:00:00', CSSR_HUAWEI: 99.76203992, CDR_HUAWEI: 0.102534056 },
    { date: '2025-12-11', time: '02:00:00', CSSR_HUAWEI: 99.83635186, CDR_HUAWEI: 0.055256251 },
    { date: '2025-12-11', time: '03:00:00', CSSR_HUAWEI: 99.73572171, CDR_HUAWEI: 0.066323993 },
    { date: '2025-12-11', time: '04:00:00', CSSR_HUAWEI: 99.88916068, CDR_HUAWEI: 0.015782828 },
    { date: '2025-12-11', time: '05:00:00', CSSR_HUAWEI: 99.73578534, CDR_HUAWEI: 0.060984906 },
    { date: '2025-12-11', time: '06:00:00', CSSR_HUAWEI: 99.62288612, CDR_HUAWEI: 0.050059161 },
    { date: '2025-12-11', time: '07:00:00', CSSR_HUAWEI: 99.46567434, CDR_HUAWEI: 0.073640389 },
    { date: '2025-12-11', time: '08:00:00', CSSR_HUAWEI: 99.59208894, CDR_HUAWEI: 0.079210989 },
    { date: '2025-12-11', time: '09:00:00', CSSR_HUAWEI: 99.17848149, CDR_HUAWEI: 0.084144019 },
    { date: '2025-12-11', time: '10:00:00', CSSR_HUAWEI: 99.6567089, CDR_HUAWEI: 0.067416379 },
    { date: '2025-12-11', time: '11:00:00', CSSR_HUAWEI: 99.63817291, CDR_HUAWEI: 0.065050622 },
    { date: '2025-12-11', time: '12:00:00', CSSR_HUAWEI: 99.68455198, CDR_HUAWEI: 0.057908645 },
    { date: '2025-12-11', time: '13:00:00', CSSR_HUAWEI: 99.6137193, CDR_HUAWEI: 0.052767812 },
    { date: '2025-12-11', time: '14:00:00', CSSR_HUAWEI: 99.45631365, CDR_HUAWEI: 0.054016205 },
    { date: '2025-12-11', time: '15:00:00', CSSR_HUAWEI: 99.49580114, CDR_HUAWEI: 0.066574637 },
    { date: '2025-12-11', time: '16:00:00', CSSR_HUAWEI: 99.63556969, CDR_HUAWEI: 0.062398992 },
    { date: '2025-12-11', time: '17:00:00', CSSR_HUAWEI: 99.62495722, CDR_HUAWEI: 0.065582027 },
    { date: '2025-12-11', time: '18:00:00', CSSR_HUAWEI: 99.10948003, CDR_HUAWEI: 0.091534052 },
    { date: '2025-12-11', time: '19:00:00', CSSR_HUAWEI: 98.82444137, CDR_HUAWEI: 0.072718055 },
    { date: '2025-12-11', time: '20:00:00', CSSR_HUAWEI: 98.96069383, CDR_HUAWEI: 0.067666521 },
    { date: '2025-12-11', time: '21:00:00', CSSR_HUAWEI: 99.22297053, CDR_HUAWEI: 0.069355847 },
    { date: '2025-12-11', time: '22:00:00', CSSR_HUAWEI: 99.55157282, CDR_HUAWEI: 0.09985373 },
    { date: '2025-12-11', time: '23:00:00', CSSR_HUAWEI: 99.64335684, CDR_HUAWEI: 0.09506544 },
    { date: '2025-12-12', time: '00:00:00', CSSR_HUAWEI: 99.60673432, CDR_HUAWEI: 0.077803352 },
    { date: '2025-12-12', time: '01:00:00', CSSR_HUAWEI: 99.71962825, CDR_HUAWEI: 0.081788441 },
    { date: '2025-12-12', time: '02:00:00', CSSR_HUAWEI: 99.31673928, CDR_HUAWEI: 0.090859531 },
    { date: '2025-12-12', time: '03:00:00', CSSR_HUAWEI: 99.83121452, CDR_HUAWEI: 0.054585153 },
    { date: '2025-12-12', time: '04:00:00', CSSR_HUAWEI: 99.67086973, CDR_HUAWEI: 0.109914267 },
    { date: '2025-12-12', time: '05:00:00', CSSR_HUAWEI: 99.57575635, CDR_HUAWEI: 0.074446306 },
    { date: '2025-12-12', time: '06:00:00', CSSR_HUAWEI: 99.52687443, CDR_HUAWEI: 0.084245026 },
    { date: '2025-12-12', time: '07:00:00', CSSR_HUAWEI: 99.51354706, CDR_HUAWEI: 0.082203595 },
    { date: '2025-12-12', time: '08:00:00', CSSR_HUAWEI: 99.20322183, CDR_HUAWEI: 0.115042431 },
    { date: '2025-12-12', time: '09:00:00', CSSR_HUAWEI: 98.82884665, CDR_HUAWEI: 0.097336003 },
    { date: '2025-12-12', time: '10:00:00', CSSR_HUAWEI: 99.37006747, CDR_HUAWEI: 0.075787253 },
    { date: '2025-12-12', time: '11:00:00', CSSR_HUAWEI: 99.63242211, CDR_HUAWEI: 0.076026214 },
    { date: '2025-12-12', time: '12:00:00', CSSR_HUAWEI: 99.40079409, CDR_HUAWEI: 0.068921483 },
    { date: '2025-12-12', time: '13:00:00', CSSR_HUAWEI: 99.65190038, CDR_HUAWEI: 0.049591149 },
    { date: '2025-12-12', time: '14:00:00', CSSR_HUAWEI: 99.68402579, CDR_HUAWEI: 0.050364925 },
    { date: '2025-12-12', time: '15:00:00', CSSR_HUAWEI: 99.67297899, CDR_HUAWEI: 0.058412391 },
    { date: '2025-12-12', time: '16:00:00', CSSR_HUAWEI: 99.71006359, CDR_HUAWEI: 0.063304314 },
    { date: '2025-12-12', time: '17:00:00', CSSR_HUAWEI: 99.58263439, CDR_HUAWEI: 0.067050138 },
    { date: '2025-12-12', time: '18:00:00', CSSR_HUAWEI: 99.45146966, CDR_HUAWEI: 0.062944357 },
    { date: '2025-12-12', time: '19:00:00', CSSR_HUAWEI: 98.93569939, CDR_HUAWEI: 0.063447888 },
    { date: '2025-12-12', time: '20:00:00', CSSR_HUAWEI: 99.2735488, CDR_HUAWEI: 0.060305243 },
    { date: '2025-12-12', time: '21:00:00', CSSR_HUAWEI: 99.02471614, CDR_HUAWEI: 0.11071184 },
    { date: '2025-12-12', time: '22:00:00', CSSR_HUAWEI: 99.26388472, CDR_HUAWEI: 0.129371377 },
    { date: '2025-12-12', time: '23:00:00', CSSR_HUAWEI: 99.67113381, CDR_HUAWEI: 0.071809088 }
  ];

  // Transform data to support multiple X-Axis fields
  const data = useMemo(() =>
    transformDataWithCombinedAxis(rawData, xAxisFields),
    [xAxisFields]
  );

  // Create datetime for x-axis (for the old Plot component)
  const xValues = data.map(row => `${row.date} ${row.time}`);
  const cssrValues = data.map(row => row.CSSR_HUAWEI);
  const cdrValues = data.map(row => row.CDR_HUAWEI);

  // Define the traces (data series for the chart)
  const traces = [
    {
      x: xValues,
      y: cssrValues,
      name: 'CSSR_HUAWEI',
      type: 'scatter',
      mode: 'lines+markers',
      line: { color: 'blue', width: 2 },
      marker: { size: 6 },
      yaxis: 'y1'  // Use left y-axis
    },
    {
      x: xValues,
      y: cdrValues,
      name: 'CDR_HUAWEI',
      type: 'scatter',
      mode: 'lines+markers',
      line: { color: 'red', width: 2 },
      marker: { size: 6 },
      yaxis: 'y2'  // Use right y-axis
    }
  ];

  // Define the layout (how the chart looks)
  const layout = {
    title: 'CSSR vs CDR - Dual Axis Example',
    xaxis: {
      title: 'Date Time',
      tickangle: -66,
      // Option 1: Show all ticks (can be crowded)
      // tickmode: 'linear',

      // Option 2: Show specific number of ticks
      nticks: 25,  // Try to show around 20 ticks

      // Option 3: Use auto (default - what you see now)
      // tickmode: 'auto'
    },
    yaxis: {
      title: 'CSSR (%)',
      titlefont: { color: 'blue' },
      tickfont: { color: 'blue' }
    },
    yaxis2: {
      title: 'CDR (%)',
      titlefont: { color: 'red' },
      tickfont: { color: 'red' },
      overlaying: 'y',
      side: 'right'
    },
    hovermode: 'x unified',
    showlegend: true,
    legend: {
      orientation: 'h',
      yanchor: 'bottom',
      y: -0.3,
      xanchor: 'center',
      x: 0.5
    },
    margin: { l: 50, r: 20, t: 40, b: 100 } 
  };

  // Config for the chart toolbar
  const config = {
    responsive: true,
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    toImageButtonOptions: {
      format: 'png',
      filename: '3G_KPI_Chart',
      height: 800,
      width: 1400,
      scale: 2
    }
  };

  // Second chart - CSSR only
  const cssrTrace = {
    x: xValues,
    y: cssrValues,
    name: 'CSSR_HUAWEI',
    type: 'scatter',
    mode: 'lines+markers',
    line: { color: 'green', width: 2 },
    marker: { size: 6 }
  };

  const cssrLayout = {
    title: 'CSSR_HUAWEI Only',
    xaxis: {
      title: 'Date Time',
      tickangle: -90,  // Vertical rotation (more readable for long text)
      nticks: 30,
      tickfont: {
        size: 10  // Smaller font size to fit better
      }
    },
    yaxis: {
      title: 'CSSR (%)',
      titlefont: { color: 'green' },
      tickfont: { color: 'green' }
    },
    hovermode: 'x unified',
    showlegend: true,
    legend: {
      orientation: 'h',
      yanchor: 'bottom',
      y: -0.2,
      xanchor: 'center',
      x: 0.5
    },
    margin: { l: 50, r: 20, t: 40, b: 100 }  // Reduced margins
  };

  return (
    <div style={{ padding: '5px' }}>
      <h1>3G Simple Dashboard - Plotly Example</h1>

      {/* Two charts side by side */}
      <div style={{ display: 'flex', gap: '15px', marginBottom: '20px' }}>
        {/* Chart 1: CSSR Only */}
        <div style={{
          flex: 1,
          background: 'white',
          padding: '10px',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <Plot
            data={[cssrTrace]}
            layout={cssrLayout}
            config={config}
            style={{ width: '100%', height: '500px' }}
          />
        </div>

        {/* Chart 2: CSSR vs CDR (Dual Axis) */}
        <div style={{
          flex: 1,
          background: 'white',
          padding: '10px',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <Plot
            data={traces}
            layout={layout}
            config={config}
            style={{ width: '100%', height: '500px' }}
          />
        </div>
      </div>

      <hr style={{ margin: '30px 0', border: '1px solid #ddd' }} />

      {/* PlotlyChart Component with Interactive Pivot */}
      <h2>Interactive Pivot Chart (PlotlyChart Component)</h2>

      {/* Pivot Configuration - Using Reusable Component */}
      <PivotControls
        availableFields={availableFields}
        availableKPIs={availableKPIs}
        xAxisFields={xAxisFields}
        setXAxisFields={setXAxisFields}
        legendFields={legendFields}
        setLegendFields={setLegendFields}
        selectedKPIs={selectedKPIs}
        setSelectedKPIs={setSelectedKPIs}
        layoutSettings={layoutSettings}
        setLayoutSettings={setLayoutSettings}
        collapsible={true}
        defaultExpanded={false}
        showLayoutSettings={true}
      />

      {/* PlotlyChart Component */}
      {selectedKPIs.length > 0 ? (
        <div style={{
          background: 'white',
          padding: '10px',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <PlotlyChart
            data={data}
            chartConfig={{
              title: 'Interactive Pivot Chart',
              KPIS: selectedKPIs,
              default_type: 'line',
              y_axis_title: 'KPI Value (%)'
            }}
            xAxisKey="_combinedXAxis"
            groupByField={legendFields.length > 0 ? legendFields[0] : null}
            layoutSettings={layoutSettings}
            onDownload={() => alert('Download clicked!')}
            onViewData={() => alert('View Data clicked!')}
          />
        </div>
      ) : (
        <div style={{
          padding: '40px',
          textAlign: 'center',
          background: '#f5f5f5',
          borderRadius: '8px'
        }}>
          Please select at least one KPI to display the chart.
        </div>
      )}
    </div>
  );
};

export default Simple3GDashboard;