import { useState, useEffect } from 'react';
import { getQueryDetails } from '../services/api';
import './FilterPanel.css';

const FilterPanel = ({ category, subcategory, queryName, onFilterChange }) => {
  const [queryConfig, setQueryConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isExpanded, setIsExpanded] = useState(false); // Expand/collapse state - collapsed by default

  // Filter states
  const [dateRange, setDateRange] = useState('last_30_days');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [timeGranularity, setTimeGranularity] = useState('DAILY');
  const [aggregationLevel, setAggregationLevel] = useState(null);
  const [selectedKpis, setSelectedKpis] = useState([]);

  // Manual filter input (comma-separated values)
  const [filterInput, setFilterInput] = useState('');

  useEffect(() => {
    fetchQueryConfig();
  }, [category, subcategory, queryName]);

  // Auto-apply filters on initial load
  useEffect(() => {
    if (queryConfig && startDate && endDate && selectedKpis.length > 0) {
      // Automatically apply filters with defaults
      handleApplyFilters();
    }
  }, [queryConfig]);

  const fetchQueryConfig = async () => {
    try {
      setLoading(true);
      const config = await getQueryDetails(category, queryName, subcategory);
      setQueryConfig(config);

      // Set defaults
      if (config.available_kpis && config.available_kpis.length > 0) {
        setSelectedKpis(config.available_kpis);
      }

      // Set default dates (last 30 days)
      const end = new Date();
      const start = new Date();
      start.setDate(start.getDate() - 30);
      setStartDate(start.toISOString().split('T')[0]);
      setEndDate(end.toISOString().split('T')[0]);
    } catch (error) {
      console.error('Failed to fetch query config:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDateRangeChange = (range) => {
    setDateRange(range);
    const end = new Date();
    const start = new Date();

    switch (range) {
      case 'last_7_days':
        start.setDate(start.getDate() - 7);
        break;
      case 'last_10_days':
        start.setDate(start.getDate() - 10);
        break;
      case 'last_30_days':
        start.setDate(start.getDate() - 30);
        break;
      case 'last_60_days':
        start.setDate(start.getDate() - 60);
        break;
      case 'last_90_days':
        start.setDate(start.getDate() - 90);
        break;
      case 'custom':
        return;
      default:
        start.setDate(start.getDate() - 30);
    }

    setStartDate(start.toISOString().split('T')[0]);
    setEndDate(end.toISOString().split('T')[0]);
  };

  const handleApplyFilters = () => {
    // Parse filter input (comma-separated values)
    const filters = {};
    if (aggregationLevel && filterInput.trim()) {
      const values = filterInput
        .split(',')
        .map(v => v.trim())
        .filter(v => v.length > 0);
      if (values.length > 0) {
        filters[aggregationLevel] = values;
      }
    }

    onFilterChange({
      startDate,
      endDate,
      timeGranularity,
      aggregationLevel,
      selectedKpis,
      filters,
    });
  };

  const handleKpiToggle = (kpi) => {
    setSelectedKpis((prev) =>
      prev.includes(kpi) ? prev.filter((k) => k !== kpi) : [...prev, kpi]
    );
  };

  if (loading) {
    return <div className="filter-panel">Loading filters...</div>;
  }

  if (!queryConfig) {
    return <div className="filter-panel">Failed to load filters</div>;
  }

  return (
    <div className="filter-panel">
      {/* Collapsible Header */}
      <div
        className="filter-header"
        onClick={() => setIsExpanded(!isExpanded)}
        style={{
          padding: '15px 20px',
          cursor: 'pointer',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: isExpanded ? '1px solid #ddd' : 'none',
          userSelect: 'none',
          background: 'white',
          borderRadius: isExpanded ? '8px 8px 0 0' : '8px',
        }}
      >
        <h3 style={{ margin: 0 }}>Filters</h3>
        <span
          style={{
            fontSize: '20px',
            transition: 'transform 0.3s',
            transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
          }}
        >
          ▼
        </span>
      </div>

      {/* Collapsible Content */}
      {isExpanded && (
        <div className="filter-section">
          {/* Date Range Quick Select */}
          <div className="filter-group">
            <label>Date Range</label>
            <select value={dateRange} onChange={(e) => handleDateRangeChange(e.target.value)}>
              <option value="last_7_days">Last 7 Days</option>
              <option value="last_10_days">Last 10 Days</option>
              <option value="last_30_days">Last 30 Days</option>
              <option value="last_60_days">Last 60 Days</option>
              <option value="last_90_days">Last 90 Days</option>
              <option value="custom">Custom Range</option>
            </select>
          </div>

          {/* Custom Date Range */}
          {dateRange === 'custom' && (
            <div className="filter-group date-inputs">
              <div className="date-input-group">
                <label>Start Date</label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>
              <div className="date-input-group">
                <label>End Date</label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                />
              </div>
            </div>
          )}

          {/* Always show current date range */}
          <div className="filter-info">
            <small>
              Selected: {startDate} to {endDate}
            </small>
          </div>

          {/* Time Granularity */}
          {queryConfig.time_granularities && queryConfig.time_granularities.length > 0 && (
            <div className="filter-group">
              <label>Time Granularity</label>
              <select
                value={timeGranularity}
                onChange={(e) => setTimeGranularity(e.target.value)}
              >
                {queryConfig.time_granularities.map((gran) => (
                  <option key={gran} value={gran}>
                    {gran}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Aggregation Level */}
          {queryConfig.aggregation_levels && queryConfig.aggregation_levels.length > 0 && (
            <div className="filter-group">
              <label>Aggregation Level</label>
              <select
                value={aggregationLevel || ''}
                onChange={(e) => {
                  setAggregationLevel(e.target.value || null);
                  setFilterInput(''); // Clear filter input when changing aggregation
                }}
              >
                <option value="">None (Network Level)</option>
                {queryConfig.aggregation_levels.map((level) => (
                  <option key={level} value={level}>
                    {level.replace(/_/g, ' ').toUpperCase()}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Manual Filter Input (shown when aggregation level is selected) */}
          {aggregationLevel && (
            <div className="filter-group">
              <label>
                Filter by {aggregationLevel.replace(/_/g, ' ').toUpperCase()}
              </label>
              <input
                type="text"
                className="filter-manual-input"
                placeholder="Enter values separated by commas (e.g., Site1, Site2, Site3)"
                value={filterInput}
                onChange={(e) => setFilterInput(e.target.value)}
              />
              <div className="filter-info">
                <small>Enter comma-separated values to filter by specific {aggregationLevel.replace(/_/g, ' ')}s</small>
              </div>
            </div>
          )}

          {/* KPI Selection */}
          {queryConfig.available_kpis && queryConfig.available_kpis.length > 0 && (
            <div className="filter-group">
              <label>Select KPIs</label>
              <div className="kpi-checkboxes">
                {queryConfig.available_kpis.map((kpi) => (
                  <label key={kpi} className="kpi-checkbox">
                    <input
                      type="checkbox"
                      checked={selectedKpis.includes(kpi)}
                      onChange={() => handleKpiToggle(kpi)}
                    />
                    <span>{kpi}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Apply Button */}
          <div className="filter-actions">
            <button className="apply-btn" onClick={handleApplyFilters}>
              Apply Filters
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FilterPanel;