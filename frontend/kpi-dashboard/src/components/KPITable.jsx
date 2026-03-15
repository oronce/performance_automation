import React from 'react';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import './KPITable.css';

const KPITable = ({ data, columns, title, onDownload }) => {
  const defaultColDef = {
    sortable: true,
    filter: true,
    resizable: true,
    flex: 1,
  };

  return (
    <div className="kpi-table-container">
      <div className="table-header">
        <h3 className="table-title">{title}</h3>
        {onDownload && (
          <button className="table-btn" onClick={onDownload}>
            📥 Download Excel
          </button>
        )}
      </div>

      <div className="ag-theme-alpine" style={{ height: 500, width: '100%' }}>
        <AgGridReact
          rowData={data}
          columnDefs={columns}
          defaultColDef={defaultColDef}
          pagination={true}
          paginationPageSize={20}
          animateRows={true}
        />
      </div>
    </div>
  );
};

export default KPITable;
