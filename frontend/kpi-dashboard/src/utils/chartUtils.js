/**
 * Utility functions for chart data transformation and state management
 */

/**
 * Transforms raw data by adding a combined X-axis field
 * @param {Array} rawData - The original data array
 * @param {Array} xAxisFields - Array of field names to combine for X-axis
 * @returns {Array} Transformed data with _combinedXAxis field
 */
export const transformDataWithCombinedAxis = (rawData, xAxisFields) => {
  if (!rawData || !Array.isArray(rawData)) {
    return [];
  }

  return rawData.map(row => {
    const combinedXAxis = xAxisFields.length > 0
      ? xAxisFields.map(field => row[field]).join(' ')
      : row.time || row.date || ''; // Fallback to common fields

    return {
      ...row,
      _combinedXAxis: combinedXAxis
    };
  });
};

/**
 * Default layout settings for charts
 */
export const DEFAULT_LAYOUT_SETTINGS = {
  nticks: 25,
  tickangle: -45,
  tickfontsize: 10,
};

/**
 * Custom hook for managing chart state
 * @param {Array} defaultXAxis - Default X-axis fields
 * @param {Array} defaultKPIs - Default selected KPIs
 * @param {Object} defaultLayoutSettings - Default layout settings
 * @returns {Object} State and setter functions
 */
export const useChartState = (
  defaultXAxis = ['date', 'time'],
  defaultKPIs = [],
  defaultLayoutSettings = DEFAULT_LAYOUT_SETTINGS
) => {
  const [xAxisFields, setXAxisFields] = React.useState(defaultXAxis);
  const [legendFields, setLegendFields] = React.useState([]);
  const [selectedKPIs, setSelectedKPIs] = React.useState(defaultKPIs);
  const [layoutSettings, setLayoutSettings] = React.useState(defaultLayoutSettings);

  return {
    xAxisFields,
    setXAxisFields,
    legendFields,
    setLegendFields,
    selectedKPIs,
    setSelectedKPIs,
    layoutSettings,
    setLayoutSettings,
  };
};