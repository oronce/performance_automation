import React, { useState } from 'react';

/**
 * PivotControls - Reusable pivot table-style configuration UI
 *
 * Features:
 * - Field selection for X-axis and Legend (grouping)
 * - KPI selection with checkboxes
 * - Chart layout settings (ticks, angle, font size)
 * - Collapsible interface
 */
const PivotControls = ({
  availableFields = [],
  availableKPIs = [],
  xAxisFields = [],
  setXAxisFields,
  legendFields = [],
  setLegendFields,
  selectedKPIs = [],
  setSelectedKPIs,
  layoutSettings = { nticks: 25, tickangle: -45, tickfontsize: 10 },
  setLayoutSettings,
  collapsible = true,
  defaultExpanded = false,
  showLayoutSettings = true,
}) => {
  const [configExpanded, setConfigExpanded] = useState(defaultExpanded);

  const handleAddToXAxis = (field) => {
    console.log(`[ACTION] Adding "${field}" to X-Axis`);
    if (!xAxisFields.includes(field)) {
      setXAxisFields([...xAxisFields, field]);
      console.log(`[SUCCESS] "${field}" added to X-Axis`);
    } else {
      console.log(`[SKIP] "${field}" already in X-Axis`);
    }
  };

  const handleAddToLegend = (field) => {
    console.log(`[ACTION] Adding "${field}" to Legend`);
    if (!legendFields.includes(field)) {
      setLegendFields([...legendFields, field]);
      console.log(`[SUCCESS] "${field}" added to Legend`);
    } else {
      console.log(`[SKIP] "${field}" already in Legend`);
    }
  };

  const handleRemoveFromXAxis = (field) => {
    setXAxisFields(xAxisFields.filter(f => f !== field));
  };

  const handleRemoveFromLegend = (field) => {
    setLegendFields(legendFields.filter(f => f !== field));
  };

  const handleKPIToggle = (kpi, checked) => {
    if (checked) {
      setSelectedKPIs([...selectedKPIs, kpi]);
    } else {
      setSelectedKPIs(selectedKPIs.filter(k => k !== kpi));
    }
  };

  const contentSection = (
    <div style={{ padding: '20px' }}>
      {/* Available Fields */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{ fontWeight: 'bold', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '5px' }}>
          📦 Available Fields:
        </div>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          {availableFields.map(field => (
            <div key={field} style={{ display: 'flex', gap: '4px' }}>
              <button
                style={{
                  padding: '6px 12px',
                  border: '1px solid #1976d2',
                  borderRadius: '4px 0 0 4px',
                  background: 'white',
                  color: '#1976d2',
                  cursor: 'pointer',
                  fontSize: '13px',
                  fontWeight: '500'
                }}
                onClick={() => handleAddToXAxis(field)}
                title="Add to X-Axis"
              >
                {field.charAt(0).toUpperCase() + field.slice(1)}
              </button>
              <button
                style={{
                  padding: '6px 8px',
                  border: '1px solid #ff9800',
                  borderLeft: 'none',
                  borderRadius: '0 4px 4px 0',
                  background: '#ff9800',
                  color: 'white',
                  cursor: 'pointer',
                  fontSize: '11px'
                }}
                onClick={() => handleAddToLegend(field)}
                title="Add to Legend"
              >
                🏷️
              </button>
            </div>
          ))}
        </div>
        <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
          Click field name to add to X-Axis, or 🏷️ to add to Legend
        </div>
      </div>

      <div style={{ display: 'flex', gap: '20px' }}>
        {/* X-Axis Section */}
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 'bold', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '5px' }}>
            📊 X-Axis:
          </div>
          <div style={{
            minHeight: '80px',
            border: '2px dashed #ccc',
            borderRadius: '4px',
            padding: '10px',
            background: '#fafafa'
          }}>
            {xAxisFields.length > 0 ? (
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {xAxisFields.map(field => (
                  <div
                    key={field}
                    style={{
                      padding: '6px 10px',
                      background: '#1976d2',
                      color: 'white',
                      borderRadius: '4px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      fontSize: '13px'
                    }}
                  >
                    {field.charAt(0).toUpperCase() + field.slice(1)}
                    <button
                      onClick={() => handleRemoveFromXAxis(field)}
                      style={{
                        background: 'rgba(255,255,255,0.3)',
                        border: 'none',
                        color: 'white',
                        cursor: 'pointer',
                        padding: '2px 6px',
                        borderRadius: '3px',
                        fontSize: '12px'
                      }}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ color: '#999', fontSize: '13px' }}>Select field(s) for X-axis</div>
            )}
          </div>
        </div>

        {/* Legend Section */}
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 'bold', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '5px' }}>
            🏷️ Legend (Group By):
          </div>
          <div style={{
            minHeight: '80px',
            border: '2px dashed #ccc',
            borderRadius: '4px',
            padding: '10px',
            background: '#fafafa'
          }}>
            {legendFields.length > 0 ? (
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {legendFields.map(field => (
                  <div
                    key={field}
                    style={{
                      padding: '6px 10px',
                      background: '#ff9800',
                      color: 'white',
                      borderRadius: '4px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      fontSize: '13px'
                    }}
                  >
                    {field.charAt(0).toUpperCase() + field.slice(1)}
                    <button
                      onClick={() => handleRemoveFromLegend(field)}
                      style={{
                        background: 'rgba(255,255,255,0.3)',
                        border: 'none',
                        color: 'white',
                        cursor: 'pointer',
                        padding: '2px 6px',
                        borderRadius: '3px',
                        fontSize: '12px'
                      }}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ color: '#999', fontSize: '13px' }}>Select field(s) to create separate lines</div>
            )}
          </div>
        </div>
      </div>

      {/* KPI Selection */}
      <div style={{ marginTop: '20px' }}>
        <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>Select KPIs:</div>
        <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
          {availableKPIs.map(kpi => (
            <label key={kpi} style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px' }}>
              <input
                type="checkbox"
                checked={selectedKPIs.includes(kpi)}
                onChange={(e) => handleKPIToggle(kpi, e.target.checked)}
              />
              {kpi}
            </label>
          ))}
        </div>
      </div>

      {/* Chart Layout Settings */}
      {showLayoutSettings && (
        <div style={{ marginTop: '20px', paddingTop: '20px', borderTop: '1px solid #ddd' }}>
          <div style={{ fontWeight: 'bold', marginBottom: '12px' }}>⚙️ Chart Layout Settings:</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '15px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '13px', marginBottom: '5px', color: '#666' }}>
                Number of Ticks:
              </label>
              <input
                type="number"
                value={layoutSettings.nticks}
                onChange={(e) => setLayoutSettings({ ...layoutSettings, nticks: parseInt(e.target.value) || 25 })}
                style={{
                  width: '100%',
                  padding: '6px',
                  border: '1px solid #ccc',
                  borderRadius: '4px',
                  fontSize: '13px'
                }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '13px', marginBottom: '5px', color: '#666' }}>
                Tick Angle (degrees):
              </label>
              <input
                type="number"
                value={layoutSettings.tickangle}
                onChange={(e) => setLayoutSettings({ ...layoutSettings, tickangle: parseInt(e.target.value) || -45 })}
                style={{
                  width: '100%',
                  padding: '6px',
                  border: '1px solid #ccc',
                  borderRadius: '4px',
                  fontSize: '13px'
                }}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '13px', marginBottom: '5px', color: '#666' }}>
                Tick Font Size:
              </label>
              <input
                type="number"
                value={layoutSettings.tickfontsize}
                onChange={(e) => setLayoutSettings({ ...layoutSettings, tickfontsize: parseInt(e.target.value) || 10 })}
                style={{
                  width: '100%',
                  padding: '6px',
                  border: '1px solid #ccc',
                  borderRadius: '4px',
                  fontSize: '13px'
                }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );

  if (!collapsible) {
    return (
      <div style={{
        background: 'white',
        borderRadius: '8px',
        marginBottom: '20px',
        border: '1px solid #ddd'
      }}>
        {contentSection}
      </div>
    );
  }

  return (
    <div style={{
      background: 'white',
      borderRadius: '8px',
      marginBottom: '20px',
      border: '1px solid #ddd'
    }}>
      {/* Collapsible Header */}
      <div
        onClick={() => setConfigExpanded(!configExpanded)}
        style={{
          padding: '15px 20px',
          cursor: 'pointer',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: configExpanded ? '1px solid #ddd' : 'none',
          userSelect: 'none'
        }}
      >
        <h3 style={{ margin: 0 }}>⚙️ Chart Configuration</h3>
        <span style={{
          fontSize: '20px',
          transition: 'transform 0.3s',
          transform: configExpanded ? 'rotate(180deg)' : 'rotate(0deg)'
        }}>
          ▼
        </span>
      </div>

      {/* Collapsible Content */}
      {configExpanded && contentSection}
    </div>
  );
};

export default PivotControls;