// ============================================================================
// HOW TO CREATE A NEW DASHBOARD - SIMPLE TEMPLATE
// ============================================================================
//
// Just copy this file, rename it, and change the QUERY_CONFIG.
// That's it! Everything else is handled automatically by MetadataDrivenDashboard.
//
// Example: To create a "3G Nokia Dashboard":
//   1. Copy this file to: src/pages/3G/NokiaDashboard.jsx
//   2. Change QUERY_CONFIG to your values
//   3. Change title prop
//   4. Done! All features work automatically:
//      - Filters (dates, KPIs, aggregation, dynamic filters)
//      - Pivot mode with controls
//      - Chart expand/collapse
//      - View data table
//      - Download Excel
//      - 2 or 3 charts per row
// ============================================================================

import React from 'react';
import MetadataDrivenDashboard from '../components/MetadataDrivenDashboard';

const ExampleDashboard = () => {
  // ⬇️ ONLY THING YOU NEED TO CHANGE ⬇️
  const QUERY_CONFIG = {
    category: '2G_NETWORK',      // Change to your category
    subcategory: 'COMBINED_2',   // Change to your subcategory
    queryName: 'KPI_MONITORING'  // Change to your query name
  };

  return (
    <MetadataDrivenDashboard
      queryConfig={QUERY_CONFIG}
      title="Your Dashboard Title Here"  // Change to your title
    />
  );
};

export default ExampleDashboard;

// ============================================================================
// REAL WORLD EXAMPLES:
// ============================================================================

// Example 1: 3G Huawei Dashboard
// File: src/pages/3G/HuaweiDashboard.jsx
/*
import React from 'react';
import MetadataDrivenDashboard from '../../components/MetadataDrivenDashboard';

const HuaweiDashboard = () => {
  const QUERY_CONFIG = {
    category: '3G_NETWORK',
    subcategory: 'HUAWEI',
    queryName: 'KPI_MONITORING'
  };

  return (
    <MetadataDrivenDashboard
      queryConfig={QUERY_CONFIG}
      title="3G Huawei Performance"
    />
  );
};

export default HuaweiDashboard;
*/

// Example 2: 4G Nokia Dashboard
// File: src/pages/4G/NokiaDashboard.jsx
/*
import React from 'react';
import MetadataDrivenDashboard from '../../components/MetadataDrivenDashboard';

const NokiaDashboard = () => {
  const QUERY_CONFIG = {
    category: '4G_NETWORK',
    subcategory: 'NOKIA',
    queryName: 'LTE_MONITORING'
  };

  return (
    <MetadataDrivenDashboard
      queryConfig={QUERY_CONFIG}
      title="4G Nokia Performance"
    />
  );
};

export default NokiaDashboard;
*/