import React, { useState } from 'react';
import './PivotChartSelector.css';

/**
 * PivotChartSelector Component
 * Excel pivot-style UI for configuring chart X-Axis and grouping/legend
 *
 * Props:
 * - availableFields: Array of field objects [{name: 'date', label: 'Date'}, ...]
 * - initialXAxisFields: Initial X-axis fields
 * - initialLegendFields: Initial legend fields
 * - onApply: Callback when Apply button is clicked
 */
const PivotChartSelector = ({
  availableFields = [],
  initialXAxisFields = [],
  initialLegendFields = [],
  onApply
}) => {
  const [xAxisFields, setXAxisFields] = useState(initialXAxisFields);
  const [legendFields, setLegendFields] = useState(initialLegendFields);
  const [showZoneMenu, setShowZoneMenu] = useState(null); // {field, position}

  // Update local state when initial values change
  React.useEffect(() => {
    setXAxisFields(initialXAxisFields);
    setLegendFields(initialLegendFields);
  }, [initialXAxisFields, initialLegendFields]);

  // Handle clicking an available field
  const handleFieldClick = (field, event) => {
    const rect = event.currentTarget.getBoundingClientRect();
    setShowZoneMenu({
      field,
      x: rect.left,
      y: rect.bottom + 5,
    });
  };

  // Add field to a zone
  const addFieldToZone = (field, zone) => {
    if (zone === 'xAxis') {
      if (!xAxisFields.includes(field)) {
        const newFields = [...xAxisFields, field];
        setXAxisFields(newFields);
      }
    } else if (zone === 'legend') {
      if (!legendFields.includes(field)) {
        const newFields = [...legendFields, field];
        setLegendFields(newFields);
      }
    }
    setShowZoneMenu(null);
  };

  // Remove field from a zone
  const removeFieldFromZone = (field, zone) => {
    if (zone === 'xAxis') {
      const newFields = xAxisFields.filter(f => f !== field);
      setXAxisFields(newFields);
    } else if (zone === 'legend') {
      const newFields = legendFields.filter(f => f !== field);
      setLegendFields(newFields);
    }
  };

  // Handle Apply button click
  const handleApply = () => {
    if (onApply) {
      onApply({
        xAxisFields: xAxisFields,
        legendFields: legendFields,
      });
    }
  };

  // Get display label for a field
  const getFieldLabel = (fieldName) => {
    const field = availableFields.find(f => f.name === fieldName);
    return field ? field.label : fieldName.replace(/_/g, ' ').toUpperCase();
  };

  // Get available fields that aren't in any zone
  const getUnusedFields = () => {
    const used = [...xAxisFields, ...legendFields];
    return availableFields.filter(f => !used.includes(f.name));
  };

  return (
    <div className="pivot-chart-selector">
      <h4>Chart Configuration (Pivot-Style)</h4>

      {/* Available Fields */}
      <div className="pivot-section">
        <label className="pivot-label">📦 Available Fields:</label>
        <div className="available-fields">
          {getUnusedFields().length > 0 ? (
            getUnusedFields().map(field => (
              <span
                key={field.name}
                className="field-tag available"
                onClick={(e) => handleFieldClick(field.name, e)}
                title="Click to add to X-Axis or Legend"
              >
                {field.label}
              </span>
            ))
          ) : (
            <small className="no-fields-msg">All fields are in use</small>
          )}
        </div>
        <small className="pivot-hint">Click a field to add it to X-Axis or Legend</small>
      </div>

      {/* Drop Zones */}
      <div className="pivot-zones">
        {/* X-Axis Zone */}
        <div className="pivot-section">
          <label className="pivot-label">📊 X-Axis:</label>
          <div className="drop-zone" id="xAxisZone">
            {xAxisFields.length > 0 ? (
              xAxisFields.map(field => (
                <span
                  key={field}
                  className="field-tag active"
                  onClick={() => {
                    if (window.confirm(`Remove "${getFieldLabel(field)}" from X-Axis?`)) {
                      removeFieldFromZone(field, 'xAxis');
                    }
                  }}
                  title="Click to remove"
                >
                  {getFieldLabel(field)}
                </span>
              ))
            ) : (
              <small className="empty-zone-msg">Drag fields here</small>
            )}
          </div>
        </div>

        {/* Legend/Grouping Zone */}
        <div className="pivot-section">
          <label className="pivot-label">🏷️ Legend (Group By):</label>
          <div className="drop-zone" id="legendZone">
            {legendFields.length > 0 ? (
              legendFields.map(field => (
                <span
                  key={field}
                  className="field-tag active"
                  onClick={() => {
                    if (window.confirm(`Remove "${getFieldLabel(field)}" from Legend?`)) {
                      removeFieldFromZone(field, 'legend');
                    }
                  }}
                  title="Click to remove"
                >
                  {getFieldLabel(field)}
                </span>
              ))
            ) : (
              <small className="empty-zone-msg">No grouping</small>
            )}
          </div>
        </div>
      </div>

      {/* Apply Button */}
      <div className="pivot-apply-section">
        <button className="pivot-apply-btn" onClick={handleApply}>
          ✓ Apply Changes
        </button>
        <small className="pivot-hint">Click to update charts with current configuration</small>
      </div>

      {/* Zone Selector Menu */}
      {showZoneMenu && (
        <>
          <div className="zone-menu-overlay" onClick={() => setShowZoneMenu(null)} />
          <div
            className="zone-selector-menu"
            style={{
              left: `${showZoneMenu.x}px`,
              top: `${showZoneMenu.y}px`,
            }}
          >
            <button
              className="zone-menu-btn"
              onClick={() => addFieldToZone(showZoneMenu.field, 'xAxis')}
            >
              📊 Add to X-Axis
            </button>
            <button
              className="zone-menu-btn"
              onClick={() => addFieldToZone(showZoneMenu.field, 'legend')}
            >
              🏷️ Add to Legend
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default PivotChartSelector;
