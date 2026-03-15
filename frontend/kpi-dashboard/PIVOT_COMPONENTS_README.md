# Pivot Chart Components - Usage Guide

## Overview

This project now has reusable, modular components for creating pivot-style interactive charts. All dashboard pages can use these components consistently.

## Architecture

```
src/
├── components/
│   ├── PlotlyChart.jsx          # Reusable chart component (already existed)
│   └── PivotControls.jsx        # NEW: Reusable pivot UI component
├── utils/
│   └── chartUtils.js            # NEW: Utility functions for data transformation
└── pages/
    └── 3G/
        └── Simple3GDashboard.jsx # Example implementation
```

## Components

### 1. PivotControls Component

**Location:** `src/components/PivotControls.jsx`

**Purpose:** Provides Excel-like pivot table interface for configuring charts.

**Features:**
- Field selection for X-axis and Legend (grouping)
- KPI selection with checkboxes
- Chart layout settings (ticks, angle, font size)
- Collapsible interface option

**Props:**
```javascript
<PivotControls
  availableFields={['date', 'time', 'site']}       // Fields to show in Available Fields
  availableKPIs={['CSSR', 'CDR', 'DROP_RATE']}     // KPIs to show as checkboxes
  xAxisFields={xAxisFields}                         // Current X-axis fields
  setXAxisFields={setXAxisFields}                   // Setter for X-axis fields
  legendFields={legendFields}                       // Current legend fields
  setLegendFields={setLegendFields}                 // Setter for legend fields
  selectedKPIs={selectedKPIs}                       // Current selected KPIs
  setSelectedKPIs={setSelectedKPIs}                 // Setter for selected KPIs
  layoutSettings={layoutSettings}                   // Layout settings object
  setLayoutSettings={setLayoutSettings}             // Setter for layout settings
  collapsible={true}                                // Enable collapse (default: true)
  defaultExpanded={false}                           // Start collapsed (default: false)
  showLayoutSettings={true}                         // Show layout settings (default: true)
/>
```

### 2. PlotlyChart Component

**Location:** `src/components/PlotlyChart.jsx`

**Updates:** Now accepts `layoutSettings` prop for dynamic layout configuration.

**Props:**
```javascript
<PlotlyChart
  data={transformedData}                    // Data with _combinedXAxis field
  chartConfig={{
    title: 'My Chart',
    KPIS: ['CSSR', 'CDR'],
    default_type: 'line',
    y_axis_title: 'KPI Value (%)'
  }}
  xAxisKey="_combinedXAxis"                 // Use combined x-axis field
  groupByField={legendFields[0] || null}    // Field to group by (for separate lines)
  layoutSettings={layoutSettings}           // NEW: Layout settings
  onDownload={() => alert('Download')}
  onViewData={() => alert('View Data')}
/>
```

### 3. Utility Functions

**Location:** `src/utils/chartUtils.js`

#### `transformDataWithCombinedAxis(rawData, xAxisFields)`

Transforms raw data by adding a combined X-axis field.

```javascript
import { transformDataWithCombinedAxis } from '../../utils/chartUtils';

const rawData = [
  { date: '2025-12-10', time: '00:00:00', CSSR: 99.5 },
  { date: '2025-12-10', time: '01:00:00', CSSR: 99.6 },
];

const data = transformDataWithCombinedAxis(rawData, ['date', 'time']);
// Result:
// [
//   { date: '2025-12-10', time: '00:00:00', CSSR: 99.5, _combinedXAxis: '2025-12-10 00:00:00' },
//   { date: '2025-12-10', time: '01:00:00', CSSR: 99.6, _combinedXAxis: '2025-12-10 01:00:00' },
// ]
```

#### `DEFAULT_LAYOUT_SETTINGS`

Default values for layout settings:
```javascript
import { DEFAULT_LAYOUT_SETTINGS } from '../../utils/chartUtils';

// { nticks: 25, tickangle: -45, tickfontsize: 10 }
```

## Implementation Example

Here's how to use these components in any dashboard page:

```javascript
import React, { useState, useMemo } from 'react';
import PlotlyChart from '../../components/PlotlyChart';
import PivotControls from '../../components/PivotControls';
import { transformDataWithCombinedAxis } from '../../utils/chartUtils';

const MyDashboard = () => {
  // 1. Define available fields and KPIs
  const availableFields = ['date', 'time', 'site_name'];
  const availableKPIs = ['CSSR_HUAWEI', 'CDR_HUAWEI', 'DROP_RATE'];

  // 2. Set up state
  const [xAxisFields, setXAxisFields] = useState(['date', 'time']);
  const [legendFields, setLegendFields] = useState([]);
  const [selectedKPIs, setSelectedKPIs] = useState(['CSSR_HUAWEI']);
  const [layoutSettings, setLayoutSettings] = useState({
    nticks: 25,
    tickangle: -45,
    tickfontsize: 10,
  });

  // 3. Your raw data (from API, database, etc.)
  const rawData = [
    { date: '2025-12-10', time: '00:00:00', site_name: 'Site_A', CSSR_HUAWEI: 99.5, CDR_HUAWEI: 0.1 },
    // ... more data
  ];

  // 4. Transform data with combined X-axis
  const data = useMemo(() =>
    transformDataWithCombinedAxis(rawData, xAxisFields),
    [rawData, xAxisFields]
  );

  return (
    <div>
      <h2>My Dashboard</h2>

      {/* 5. Add PivotControls */}
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
      />

      {/* 6. Add PlotlyChart */}
      {selectedKPIs.length > 0 && (
        <PlotlyChart
          data={data}
          chartConfig={{
            title: 'My Interactive Chart',
            KPIS: selectedKPIs,
            default_type: 'line',
            y_axis_title: 'KPI Value (%)'
          }}
          xAxisKey="_combinedXAxis"
          groupByField={legendFields[0] || null}
          layoutSettings={layoutSettings}
        />
      )}
    </div>
  );
};

export default MyDashboard;
```

## Benefits

### 1. **Consistency**
All dashboards use the same pivot interface - users get familiar experience across the app.

### 2. **Maintainability**
Update pivot UI in one place (PivotControls.jsx) and all dashboards benefit.

### 3. **Flexibility**
Each dashboard can customize:
- Available fields
- Available KPIs
- Default selections
- Whether to show layout settings
- Collapsible behavior

### 4. **Clean Code**
Dashboard pages are now much simpler - just configure props, no UI code duplication.

### 5. **Easy Testing**
Components can be tested independently.

## Migrating Existing Dashboards

To migrate an existing dashboard to use these components:

1. Import the new components:
```javascript
import PivotControls from '../../components/PivotControls';
import { transformDataWithCombinedAxis } from '../../utils/chartUtils';
```

2. Replace your pivot UI code with `<PivotControls />` component

3. Use `transformDataWithCombinedAxis` for data transformation instead of custom logic

4. Pass `layoutSettings` prop to `PlotlyChart`

5. Remove duplicate code

## Future Enhancements

Possible future additions:
- Add more field types (dropdown, multi-select)
- Support for date range picker
- Export/import configuration
- Saved chart templates
- More layout customization options