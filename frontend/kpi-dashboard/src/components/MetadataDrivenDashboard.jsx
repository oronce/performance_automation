import React, { useState, useEffect, useMemo } from 'react';
import { executeQuery, buildQueryRequest, exportToExcel } from '../services/api';
import PlotlyChart from './PlotlyChart';
import KPITable from './KPITable';
import FilterPanel from './FilterPanel';
import PivotControls from './PivotControls';
import { transformDataWithCombinedAxis } from '../utils/chartUtils';
import './MetadataDrivenDashboard.css';

const MetadataDrivenDashboard = ({ queryConfig, title }) => {
  const [chartData, setChartData] = useState([]);
  const [chartMetadata, setChartMetadata] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedChart, setExpandedChart] = useState(null);
  const [showTableFor, setShowTableFor] = useState(null);
  const [chartsPerRow, setChartsPerRow] = useState(2);
  const [usePivotMode, setUsePivotMode] = useState(false);

  const [xAxisFields, setXAxisFields] = useState([]);
  const [legendFields, setLegendFields] = useState([]);
  const [layoutSettings, setLayoutSettings] = useState({
    nticks: 25,
    tickangle: -45,
    tickfontsize: 10,
  });

  const [filters, setFilters] = useState({
    startDate: null,
    endDate: null,
    timeGranularity: 'DAILY',
    aggregationLevel: null,
    selectedKpis: [],
    filters: {},
  });

  const fetchData = async (filterParams) => {
    try {
      setLoading(true);
      setError(null);

      const queryRequest = buildQueryRequest({
        category: queryConfig.category,
        subcategory: queryConfig.subcategory,
        queryName: queryConfig.queryName,
        timeGranularity: filterParams.timeGranularity,
        aggregationLevel: filterParams.aggregationLevel,
        selectedKpis: filterParams.selectedKpis,
        includeDate: true,
        includeTime: filterParams.timeGranularity === 'HOURLY',
        startDate: filterParams.startDate,
        endDate: filterParams.endDate,
        filters: filterParams.filters || {},
      });

      const result = await executeQuery(queryRequest);
      console.log('Query result:', {
        granularity: filterParams.timeGranularity,
        aggregation: filterParams.aggregationLevel,
        rowCount: result.data?.length || 0,
        sampleRow: result.data?.[0],
        metadata: result.metadata
      });

      let processedData = result.data || [];
      if (filterParams.timeGranularity === 'HOURLY' && processedData.length > 0) {
        processedData = processedData.map(row => ({
          ...row,
          datetime: row.date && row.time ? `${row.date} ${row.time}` : row.date || row.time
        }));
      }

      setChartData(processedData);
      setChartMetadata(result.metadata);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    fetchData(newFilters);
    initializePivotConfig(newFilters);
  };

  const initializePivotConfig = (filterParams) => {
    const xFields = [];
    const legendFieldsArray = [];

    if (filterParams.timeGranularity === 'HOURLY') {
      xFields.push('date', 'time');
    } else if (filterParams.timeGranularity === 'DAILY') {
      xFields.push('date');
    }

    if (filterParams.aggregationLevel) {
      legendFieldsArray.push(filterParams.aggregationLevel);
    }

    setXAxisFields(xFields);
    setLegendFields(legendFieldsArray);
  };

  const handleDownload = async (kpi = null) => {
    try {
      const kpisToExport = kpi ? [kpi] : filters.selectedKpis;

      const queryRequest = buildQueryRequest({
        category: queryConfig.category,
        subcategory: queryConfig.subcategory,
        queryName: queryConfig.queryName,
        timeGranularity: filters.timeGranularity,
        aggregationLevel: filters.aggregationLevel,
        selectedKpis: kpisToExport,
        includeDate: true,
        includeTime: filters.timeGranularity === 'HOURLY',
        startDate: filters.startDate,
        endDate: filters.endDate,
        filters: filters.filters || {},
      });

      const blob = await exportToExcel(queryRequest);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const kpiName = kpi || 'All_KPIs';
      a.download = `${queryConfig.category}_${kpiName}_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert(`Failed to download: ${err.message}`);
    }
  };

  const handleExpandChart = (kpi) => {
    setExpandedChart(expandedChart === kpi ? null : kpi);
  };

  const handleToggleTable = (kpi) => {
    setShowTableFor(showTableFor === kpi ? null : kpi);
  };

  const getAvailableFields = () => {
    const fields = ['date'];

    if (filters.timeGranularity === 'HOURLY') {
      fields.push('time');
    }

    if (filters.aggregationLevel) {
      fields.push(filters.aggregationLevel);
    }

    return fields;
  };

  const transformedData = useMemo(() => {
    if (!usePivotMode || xAxisFields.length === 0) {
      return chartData;
    }
    return transformDataWithCombinedAxis(chartData, xAxisFields);
  }, [chartData, xAxisFields, usePivotMode]);

  return (
    <div className="metadata-driven-dashboard">
      <div className="dashboard-header">
        <h2>{title}</h2>
      </div>

      <FilterPanel
        category={queryConfig.category}
        subcategory={queryConfig.subcategory}
        queryName={queryConfig.queryName}
        onFilterChange={handleFilterChange}
      />

      {!loading && chartData.length > 0 && (
        <div className="pivot-mode-toggle">
          <button
            className={`pivot-toggle-btn ${usePivotMode ? 'active' : ''}`}
            onClick={() => setUsePivotMode(!usePivotMode)}
          >
            {usePivotMode ? '📊 Standard Mode' : '🔄 Pivot Mode'}
          </button>
        </div>
      )}

      {usePivotMode && !loading && chartData.length > 0 && (
        <PivotControls
          availableFields={getAvailableFields()}
          availableKPIs={filters.selectedKpis}
          xAxisFields={xAxisFields}
          setXAxisFields={setXAxisFields}
          legendFields={legendFields}
          setLegendFields={setLegendFields}
          selectedKPIs={filters.selectedKpis}
          setSelectedKPIs={(newKpis) => setFilters({ ...filters, selectedKpis: newKpis })}
          layoutSettings={layoutSettings}
          setLayoutSettings={setLayoutSettings}
          collapsible={true}
          defaultExpanded={true}
          showLayoutSettings={true}
        />
      )}

      {loading && <div className="loading-message">Loading data...</div>}

      {error && <div className="error-message">Error: {error}</div>}

      {!loading && !error && chartData.length > 0 && chartMetadata && (
        <>
          <div className="chart-controls">
            <button
              className={`layout-toggle-btn ${chartsPerRow === 2 ? 'active' : ''}`}
              onClick={() => setChartsPerRow(2)}
            >
              2 per row
            </button>
            <button
              className={`layout-toggle-btn ${chartsPerRow === 3 ? 'active' : ''}`}
              onClick={() => setChartsPerRow(3)}
            >
              3 per row
            </button>
          </div>

          <div
            className={`charts-grid charts-per-row-${chartsPerRow} ${expandedChart ? 'expanded-view' : ''}`}
          >
            {chartMetadata.chart_configs && Object.entries(chartMetadata.chart_configs).map(([chartName, chartConfig]) => {
              const isExpanded = expandedChart === chartName;
              const showTable = showTableFor === chartName;

              let xAxisKey = 'date';
              let dataToUse = chartData;
              let groupBy = filters.aggregationLevel;

              if (usePivotMode) {
                xAxisKey = '_combinedXAxis';
                dataToUse = transformedData;
                groupBy = legendFields.length > 0 ? legendFields[0] : null;
              } else if (filters.timeGranularity === 'HOURLY') {
                xAxisKey = chartData[0]?.time ? 'datetime' : 'date';
              }

              return (
                <div
                  key={chartName}
                  className={`chart-container ${isExpanded ? 'expanded' : ''}`}
                >
                  <div className="chart-header-actions">
                    <div className="chart-controls-row">
                      <button
                        className="chart-btn"
                        onClick={() => handleToggleTable(chartName)}
                      >
                        📋 View Data
                      </button>
                      <button
                        className="chart-btn"
                        onClick={() => handleDownload(chartConfig.KPIS.join('_'))}
                      >
                        📥 Download
                      </button>
                    </div>
                    <button
                      className="expand-btn"
                      onClick={() => handleExpandChart(chartName)}
                      title={isExpanded ? 'Collapse' : 'Expand'}
                    >
                      {isExpanded ? '🗙' : '⛶'}
                    </button>
                  </div>

                  <PlotlyChart
                    data={dataToUse}
                    chartConfig={chartConfig}
                    xAxisKey={xAxisKey}
                    groupByField={groupBy}
                    layoutSettings={usePivotMode ? layoutSettings : null}
                    hideHeader={true}
                  />

                  {showTable && (
                    <div className="chart-table">
                      <KPITable data={chartData} />
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {filters.selectedKpis.length > 1 && (
            <div className="dashboard-actions">
              <button className="download-all-btn" onClick={() => handleDownload()}>
                📥 Download All KPIs
              </button>
            </div>
          )}
        </>
      )}

      {!loading && !error && chartData.length === 0 && filters.selectedKpis.length > 0 && (
        <div className="no-data-message">
          No data available for the selected filters. Try changing the date range or filters.
        </div>
      )}

      {!loading && filters.selectedKpis.length === 0 && (
        <div className="no-kpi-message">
          Please select at least one KPI from the filters above.
        </div>
      )}
    </div>
  );
};

export default MetadataDrivenDashboard;