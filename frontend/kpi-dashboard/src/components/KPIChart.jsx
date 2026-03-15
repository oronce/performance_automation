import React, { useState } from 'react';
import Plot from 'react-plotly.js';
import './KPIChart.css';

/**
 * KPIChart Component - Now powered by Plotly.js
 *
 * Props:
 * - data: Array of data objects
 * - title: Chart title
 * - type: Chart type ('line', 'bar', 'area')
 * - dataKeys: Array of KPI field names to plot
 * - xAxisKey: Field name for X-axis (default: 'date')
 * - onDownload: Download callback
 * - onViewData: View data callback
 * - onChartTypeChange: Chart type change callback (optional)
 */
const KPIChart = ({
  data,
  title,
  type: initialType = 'line',
  dataKeys = [],
  xAxisKey = 'date',
  onDownload,
  onViewData,
  onChartTypeChange,
}) => {
  const [chartType, setChartType] = useState(initialType);

  const colors = [
    '#1976d2', '#dc004e', '#388e3c', '#f57c00', '#7b1fa2',
    '#00796b', '#d32f2f', '#303f9f', '#c2185b', '#512da8',
    '#0097a7', '#5d4037', '#455a64', '#e64a19', '#689f38'
  ];

  /**
   * Build Plotly traces for each KPI
   */
  const buildTraces = () => {
    const traces = [];

    dataKeys.forEach((kpi, index) => {
      const xValues = data.map(row => row[xAxisKey]);
      const yValues = data.map(row => row[kpi]);

      const trace = {
        x: xValues,
        y: yValues,
        name: kpi,
        type: chartType === 'bar' ? 'bar' : 'scatter',
        mode: chartType === 'line' ? 'lines+markers' : chartType === 'area' ? 'lines' : undefined,
        fill: chartType === 'area' ? 'tonexty' : undefined,
        marker: {
          size: chartType === 'line' ? 6 : undefined,
          color: colors[index % colors.length],
        },
        line: {
          width: 2,
          color: colors[index % colors.length],
        },
      };

      traces.push(trace);
    });

    return traces;
  };

  /**
   * Build Plotly layout configuration
   */
  const buildLayout = () => {
    return {
      title: {
        text: title,
        font: { size: 18, weight: 600 },
      },
      xaxis: {
        title: xAxisKey.charAt(0).toUpperCase() + xAxisKey.slice(1),
        tickangle: -45,
      },
      yaxis: {
        title: 'Value',
      },
      hovermode: 'x unified',
      showlegend: true,
      legend: {
        orientation: 'h',
        yanchor: 'bottom',
        y: -0.3,
        xanchor: 'center',
        x: 0.5,
      },
      margin: {
        l: 60,
        r: 40,
        t: 80,
        b: 100,
      },
    };
  };

  const handleChartTypeChange = (newType) => {
    setChartType(newType);
    if (onChartTypeChange) {
      onChartTypeChange(newType);
    }
  };

  return (
    <div className="kpi-chart-container">
      <div className="chart-header">
        <div className="chart-controls">
          {/* Chart Type Selector */}
          <div className="chart-type-selector">
            <button
              className={`chart-type-btn ${chartType === 'line' ? 'active' : ''}`}
              onClick={() => handleChartTypeChange('line')}
              title="Line Chart"
            >
              📈
            </button>
            <button
              className={`chart-type-btn ${chartType === 'bar' ? 'active' : ''}`}
              onClick={() => handleChartTypeChange('bar')}
              title="Bar Chart"
            >
              📊
            </button>
            <button
              className={`chart-type-btn ${chartType === 'area' ? 'active' : ''}`}
              onClick={() => handleChartTypeChange('area')}
              title="Area Chart"
            >
              📉
            </button>
          </div>

          <div className="chart-actions">
            {onViewData && (
              <button className="chart-btn" onClick={onViewData}>
                📋 View Data
              </button>
            )}
            {onDownload && (
              <button className="chart-btn" onClick={onDownload}>
                📥 Download
              </button>
            )}
          </div>
        </div>
      </div>

      <Plot
        data={buildTraces()}
        layout={buildLayout()}
        config={{
          responsive: true,
          displayModeBar: true,
          displaylogo: false,
          modeBarButtonsToRemove: ['lasso2d', 'select2d'],
          toImageButtonOptions: {
            format: 'png',
            filename: `${title.replace(/\s+/g, '_')}`,
            height: 800,
            width: 1200,
            scale: 2,
          },
        }}
        style={{ width: '100%', height: '500px' }}
      />
    </div>
  );
};

export default KPIChart;
