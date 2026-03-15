import React, { useState, useEffect } from 'react';
import KPIChart from '../components/KPIChart';
import KPITable from '../components/KPITable';
import { executeQuery, exportToExcel, downloadExcelFile, buildQueryRequest } from '../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const [chartData, setChartData] = useState([]);
  const [tableData, setTableData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showTable, setShowTable] = useState(false);

  // Sample query to fetch data
  const fetchData = async () => {
    setLoading(true);
    try {
      const queryRequest = buildQueryRequest({
        category: '2G',
        subcategory: 'HUAWEI',
        queryName: 'KPI_MONITORING2',
        timeGranularity: 'DAILY',
        // include_time: true,
        include_date: true,
        aggregationLevel: null,
        selectedKpis: ['CSSR_HUAWEI', 'CDR_HUAWEI', 'CBR_HUAWEI'],
        startDate: '2025-11-20',
        endDate: '2025-11-30',
        filters: {},
      });

      const result = await executeQuery(queryRequest);
      setChartData(result.data || []);
      setTableData(result.data || []);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Unknown error';
      alert(`Failed to load data: ${errorMsg}\n\nCheck browser console and backend logs for details.`);
    } finally {
      setLoading(false);
    }
  };

  // Download chart data as Excel
  const handleDownload = async () => {
    try {
      const queryRequest = buildQueryRequest({
        category: '2G',
        subcategory: 'HUAWEI',
        queryName: 'KPI_MONITORING2',
        timeGranularity: 'DAILY',
        aggregationLevel: null,
        selectedKpis: ['CSSR_HUAWEI', 'CDR_HUAWEI', 'CBR_HUAWEI'],
        startDate: '2025-11-20',
        endDate: '2025-11-30',
        filters: {},
      });

      const blob = await exportToExcel(queryRequest);
      downloadExcelFile(blob, '2G_Huawei_KPI_Report.xlsx');
    } catch (error) {
      console.error('Failed to download Excel:', error);
      alert('Excel export not yet implemented on backend');
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Table column definitions
  const tableColumns = [
    { field: 'date', headerName: 'Date', width: 150 },
    { field: 'CSSR_HUAWEI', headerName: 'CSSR (%)', width: 120, valueFormatter: (params) => params.value?.toFixed(2) },
    { field: 'CDR_HUAWEI', headerName: 'CDR (%)', width: 120, valueFormatter: (params) => params.value?.toFixed(2) },
    { field: 'CBR_HUAWEI', headerName: 'CBR (%)', width: 120, valueFormatter: (params) => params.value?.toFixed(2) },
  ];

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <h2>2G Network - Huawei Performance</h2>
        <button className="refresh-btn" onClick={fetchData} disabled={loading}>
          {loading ? '⏳ Loading...' : '🔄 Refresh'}
        </button>
      </div>

      {loading && <div className="loading-message">Loading data...</div>}

      {!loading && chartData.length > 0 && (
        <>
          <KPIChart
            data={chartData}
            title="KPI Trend - Last 30 Days"
            type="line"
            dataKeys={['CSSR_HUAWEI', 'CDR_HUAWEI', 'CBR_HUAWEI']}
            xAxisKey="date"
            onDownload={handleDownload}
            onViewData={() => setShowTable(!showTable)}
          />

          {showTable && (
            <KPITable
              data={tableData}
              columns={tableColumns}
              title="KPI Data Table"
              onDownload={handleDownload}
            />
          )}
        </>
      )}

      {!loading && chartData.length === 0 && (
        <div className="no-data-message">
          No data available. Please check your backend connection.
        </div>
      )}
    </div>
  );
};

export default Dashboard;
