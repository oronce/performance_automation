import React, { useState } from 'react';
import Plot from 'react-plotly.js';
import './PlotlyChart.css';

const PlotlyChart = ({
  data,
  chartConfig,
  xAxisKey = 'date',
  groupByField = null, // Field to group by (e.g., 'commune', 'controller_name')
  layoutSettings = null, // Optional layout settings (nticks, tickangle, tickfontsize)
  onDownload,
  onViewData,
  hideHeader = false, // Option to hide the chart header
  chartType: externalChartType = null, // Allow external chart type control
  onChartTypeChange = null, // Callback for chart type changes
}) => {
  const [internalChartType, setInternalChartType] = useState(chartConfig.default_type || 'line');

  // Use external chart type if provided, otherwise use internal state
  const chartType = externalChartType !== null ? externalChartType : internalChartType;

  // Get chart configuration
  const title = chartConfig.title || '';
  const kpis = chartConfig.KPIS || [];
  const isDualAxis = chartConfig.is_dual_axis || false;
  const yAxisTitles = chartConfig.y_axis_titles || [];
  const yAxisTitle = chartConfig.y_axis_title || '';
  const threshold = chartConfig.threshold;

  // Use the groupByField passed from parent (comes from filters.aggregationLevel)
  const activeGroupByField = groupByField;

  /**
   * Get chart type for a specific KPI (for dual-axis charts)
   */
  const getChartTypeForKPI = (index) => {
    if (isDualAxis) {
      // Use default_type_1 for first KPI, default_type_2 for second KPI
      if (index === 0 && chartConfig.default_type_1) {
        return chartConfig.default_type_1;
      }
      if (index === 1 && chartConfig.default_type_2) {
        return chartConfig.default_type_2;
      }
    }
    // Fallback to user-selected chart type
    return chartType;
  };

  /**
   * Build Plotly traces based on KPIs and chart type with grouping support
   */
  const buildTraces = () => {
    const traces = [];

    // If we have a groupBy field, create separate traces for each group
    if (activeGroupByField) {
      // Get unique group values
      const groupValues = [...new Set(data.map(row => row[activeGroupByField]))].filter(v => v != null);

      kpis.forEach((kpi, kpiIndex) => {
        const kpiChartType = getChartTypeForKPI(kpiIndex);

        groupValues.forEach((groupValue) => {
          // Filter data for this group
          const groupData = data.filter(row => row[activeGroupByField] === groupValue);

          // Sort by x-axis to ensure proper line connections
          groupData.sort((a, b) => {
            const aVal = a[xAxisKey];
            const bVal = b[xAxisKey];
            if (aVal < bVal) return -1;
            if (aVal > bVal) return 1;
            return 0;
          });

          const xValues = groupData.map(row => row[xAxisKey]);
          const yValues = groupData.map(row => row[kpi]);

          const traceName = kpis.length > 1 ? `${kpi} - ${groupValue}` : `${groupValue}`;

          const trace = {
            x: xValues,
            y: yValues,
            name: traceName,
            type: kpiChartType === 'bar' ? 'bar' : 'scatter',
            mode: kpiChartType === 'line' ? 'lines+markers' : kpiChartType === 'area' ? 'lines' : undefined,
            fill: kpiChartType === 'area' ? 'tonexty' : undefined,
            marker: {
              size: kpiChartType === 'line' ? 6 : undefined,
            },
            line: {
              width: 2,
            },
          };

          // For dual-axis, assign second KPI to second y-axis
          if (isDualAxis && kpiIndex === 1) {
            trace.yaxis = 'y2';
          }

          traces.push(trace);
        });
      });
    } else {
      // No grouping - create one trace per KPI (original behavior)
      kpis.forEach((kpi, index) => {
        const xValues = data.map(row => row[xAxisKey]);
        const yValues = data.map(row => row[kpi]);
        const kpiChartType = getChartTypeForKPI(index);

        const trace = {
          x: xValues,
          y: yValues,
          name: kpi,
          type: kpiChartType === 'bar' ? 'bar' : 'scatter',
          mode: kpiChartType === 'line' ? 'lines+markers' : kpiChartType === 'area' ? 'lines' : undefined,
          fill: kpiChartType === 'area' ? 'tonexty' : undefined,
          marker: {
            size: kpiChartType === 'line' ? 6 : undefined,
          },
          line: {
            width: 2,
          },
        };

        // For dual-axis, assign second KPI to second y-axis
        if (isDualAxis && index === 1) {
          trace.yaxis = 'y2';
        }

        traces.push(trace);
      });
    }

    // Add threshold line if specified
    if (threshold && !isDualAxis) {
      traces.push({
        x: data.map(row => row[xAxisKey]),
        y: Array(data.length).fill(threshold),
        name: `Threshold (${threshold})`,
        type: 'scatter',
        mode: 'lines',
        line: {
          dash: 'dash',
          color: 'red',
          width: 2,
        },
      });
    }

    return traces;
  };

  /**
   * Build Plotly layout configuration
   */
  const buildLayout = () => {
    const layout = {
      title: {
        text: title,
        font: { size: 16 },
      },
      xaxis: {
        title: xAxisKey.charAt(0).toUpperCase() + xAxisKey.slice(1),
        tickangle: layoutSettings?.tickangle ?? -45,
        nticks: layoutSettings?.nticks ?? 25,
        tickfont: {
          size: layoutSettings?.tickfontsize ?? 10,
        },
      },
      yaxis: {
        title: isDualAxis && yAxisTitles[0] ? yAxisTitles[0] : yAxisTitle,
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
        r: isDualAxis ? 60 : 20,
        t: 60,
        b: 120,
      },
      autosize: true,
    };

    // Add second y-axis for dual-axis charts
    if (isDualAxis) {
      layout.yaxis2 = {
        title: yAxisTitles[1] || kpis[1],
        overlaying: 'y',
        side: 'right',
      };
    }

    return layout;
  };

  const handleChartTypeChange = (newType) => {
    if (onChartTypeChange) {
      onChartTypeChange(newType);
    } else {
      setInternalChartType(newType);
    }
  };

  return (
    <div className="plotly-chart-container">
      {!hideHeader && (
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
      )}

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
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
              width: 1400,
              scale: 2,
            },
          }}
          style={{ width: '100%', height: '100%' }}
          useResizeHandler={true}
        />
      </div>
    </div>
  );
};

export default PlotlyChart;
