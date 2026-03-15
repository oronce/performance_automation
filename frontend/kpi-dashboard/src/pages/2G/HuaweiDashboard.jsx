import React from 'react';
import MetadataDrivenDashboard from '../../components/MetadataDrivenDashboard';

const HuaweiDashboard = () => {
  const QUERY_CONFIG = {
    category: '2G_NETWORK',
    subcategory: 'COMBINED_2',
    queryName: 'KPI_MONITORING'
  };

  return (
    <MetadataDrivenDashboard
      queryConfig={QUERY_CONFIG}
      title="2G Huawei Performance"
    />
  );
};

export default HuaweiDashboard;
