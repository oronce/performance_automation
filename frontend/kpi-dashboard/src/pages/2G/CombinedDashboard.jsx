import React, { useState, useEffect } from 'react';
import { executeQuery, buildQueryRequest, exportToExcel } from '../../services/api';
import KPIChart from '../../components/KPIChart';
import KPITable from '../../components/KPITable';

const CombinedDashboard = () => {
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showTable, setShowTable] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // This will use multi-CTE query to combine Huawei + Ericsson data
      const queryRequest = buildQueryRequest({
        category: '2G',
        subcategory: 'ALL',
        queryName: 'KPI_MONITORING2',
        timeGranularity: 'DAILY',
        selectedKpis: ['CSSR_HUAWEI', 'CSSR_ERICSSON', 'CDR_HUAWEI', 'CDR_ERICSSON'],
        includeDate: true,
        startDate: '2025-11-20',
        endDate: '2025-11-30',
      });

      const result = await executeQuery(queryRequest);
      setChartData(result.data || []);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      const queryRequest = buildQueryRequest({
        category: '2G',
        subcategory: 'ALL',
        queryName: 'KPI_MONITORING2',
        timeGranularity: 'DAILY',
        selectedKpis: ['CSSR_HUAWEI', 'CSSR_ERICSSON', 'CDR_HUAWEI', 'CDR_ERICSSON'],
        includeDate: true,
        startDate: '2025-11-20',
        endDate: '2025-11-30',
      });

      const blob = await exportToExcel(queryRequest);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `2G_Combined_KPI_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert(`Failed to download: ${err.message}`);
    }
  };

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading...</div>;
  }

  if (error) {
    return <div style={{ padding: '20px', color: 'red' }}>Error: {error}</div>;
  }

  return (
    <div style={{ padding: '20px' }}>
      <h2>2G Combined Analysis (Huawei + Ericsson)</h2>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        This dashboard combines data from both Huawei and Ericsson vendors using a multi-CTE query.
      </p>

      <KPIChart
        data={chartData}
        title="2G Combined KPI Comparison"
        type="line"
        dataKeys={['CSSR_HUAWEI', 'CSSR_ERICSSON', 'CDR_HUAWEI', 'CDR_ERICSSON']}
        xAxisKey="date"
        onDownload={handleDownload}
        onViewData={() => setShowTable(!showTable)}
      />

      {showTable && (
        <div style={{ marginTop: '20px' }}>
          <h3>Data Table</h3>
          <KPITable data={chartData} />
        </div>
      )}
    </div>
  );
};

export default CombinedDashboard;
