# KPI Dashboard - Quick Start Guide

## ✅ What's Been Done

### Backend (FastAPI)
- ✅ Excel export endpoint added: `/api/export/excel`
- ✅ CORS already enabled for frontend connection
- ✅ All imports added (openpyxl, StreamingResponse, BytesIO)

### Frontend (React)
- ✅ Project created in `performance_automation/frontend/kpi-dashboard/`
- ✅ All dependencies installed (Recharts, AG Grid, Axios)
- ✅ Components created:
  - Layout with sidebar navigation
  - KPIChart (line/bar charts)
  - KPITable (data grid)
- ✅ API service layer configured
- ✅ Sample dashboard page

## 🚀 How to Run

### 1. Start Backend (if not running)
```bash
cd performance_automation/API_SERVER
python app.py
```
Backend should be running on `http://localhost:8000`

### 2. Start Frontend
```bash
cd performance_automation/frontend/kpi-dashboard
npm run dev
```
Frontend will be available at `http://localhost:5173`

### 3. Open Browser
Navigate to `http://localhost:5173`

You should see:
- Sidebar with 2G, 3G, 4G, Traffic sections
- Dashboard showing 2G Huawei KPI chart
- Download Excel button
- View Data button to show table

## 📁 Project Structure

```
performance_automation/
├── API_SERVER/
│   └── app.py                    # ✅ Excel export added
└── frontend/
    └── kpi-dashboard/
        ├── src/
        │   ├── components/
        │   │   ├── Layout.jsx    # Sidebar navigation
        │   │   ├── KPIChart.jsx  # Chart component
        │   │   └── KPITable.jsx  # Data table
        │   ├── pages/
        │   │   └── Dashboard.jsx # Main page
        │   ├── services/
        │   │   └── api.js        # API client
        │   └── App.jsx
        ├── package.json
        └── README_SETUP.md       # Detailed docs
```

## 🎯 Features Implemented

### Charts
- Line and bar charts using Recharts
- Download Excel button
- View data table button
- Responsive design

### Data Table
- Sorting, filtering, pagination
- AG Grid implementation
- Export to Excel

### API Integration
- Query execution
- Excel file download
- Category/subcategory discovery
- Error handling

## 📥 Excel Export

The Excel export:
- Uses the same query parameters as the chart
- Styled headers (blue background, white text)
- Auto-adjusted column widths
- Timestamped filename
- Downloads directly to browser

## 🔧 Configuration

### Backend URL
Edit `frontend/kpi-dashboard/src/services/api.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

### Sample Query
The dashboard currently shows a sample query for 2G Huawei KPIs.
Edit `frontend/kpi-dashboard/src/pages/Dashboard.jsx` to customize.

## 📝 Next Steps

### To Add More Dashboards:
1. Create new page in `src/pages/` (e.g., `3G_Dashboard.jsx`)
2. Copy structure from `Dashboard.jsx`
3. Update query parameters
4. Add to navigation in `Layout.jsx`

### To Customize Charts:
1. Change `type="line"` to `type="bar"` in KPIChart
2. Modify `dataKeys` array for different KPIs
3. Adjust colors in `KPIChart.jsx`

### To Add Filters:
1. Create filter panel component
2. Add date range picker
3. Pass filter values to API

## 🐛 Troubleshooting

### "Failed to load data"
- Ensure backend is running on port 8000
- Check browser console for errors
- Verify database connection

### Excel download not working
- Check backend logs
- Ensure openpyxl is installed: `pip install openpyxl`
- Verify `/api/export/excel` endpoint is accessible

### Charts not showing
- Check if data format matches expected structure
- Verify KPI field names in response
- Open browser DevTools console

## 💡 Tips

- Use `npm run dev` for development (hot reload)
- Use `npm run build` for production
- Check `README_SETUP.md` in kpi-dashboard for detailed docs
- Backend logs will show SQL queries for debugging

## 📞 Need Help?

Check the detailed README:
```
performance_automation/frontend/kpi-dashboard/README_SETUP.md
```

Your existing backend code was NOT modified (except adding Excel export endpoint).
Everything is clean and isolated in the `frontend/` folder! 🎉
