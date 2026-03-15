# KPI Dashboard - Frontend Setup

## Overview
React-based dashboard for visualizing network KPI data with charts, tables, and Excel export.

## Tech Stack
- **React** with Vite
- **Recharts** for data visualization
- **AG Grid** for data tables
- **Axios** for API calls

## Project Structure
```
src/
├── components/
│   ├── Layout.jsx          # Main layout with sidebar
│   ├── KPIChart.jsx        # Reusable chart component
│   └── KPITable.jsx        # Data table with AG Grid
├── pages/
│   └── Dashboard.jsx       # Main dashboard page
├── services/
│   └── api.js              # API client for backend
└── App.jsx                 # Root component
```

## Getting Started

### 1. Install Dependencies (Already Done)
```bash
cd performance_automation/frontend/kpi-dashboard
npm install
```

### 2. Configure Backend URL
Edit `src/services/api.js` and update the API base URL:
```javascript
const API_BASE_URL = 'http://localhost:8000';  // Change if needed
```

### 3. Start Development Server
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### 4. Build for Production
```bash
npm run build
```

## Features Implemented

### ✅ Components
- **Layout**: Sidebar navigation with collapsible sections (2G, 3G, 4G, Traffic)
- **KPIChart**: Line/Bar charts with download and view data buttons
- **KPITable**: Data grid with sorting, filtering, pagination

### ✅ API Integration
- Query execution
- Category/subcategory discovery
- Query details retrieval
- Excel export (backend endpoint needed)

### ✅ Sample Dashboard
- 2G Huawei KPI trend chart
- Toggleable data table
- Refresh button
- Excel download button

## Next Steps

### Backend Integration Needed:
1. **Enable CORS** on FastAPI backend:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. **Add Excel Export Endpoint** (see API_SERVER/app.py updates)

### Frontend Enhancements:
- Add more dashboard pages (3G, 4G, Traffic)
- Add filter panel for dynamic queries
- Add date range picker
- Add more chart types (pie, area, etc.)

## Dependencies Installed
```json
{
  "recharts": "^2.x",
  "ag-grid-react": "^32.x",
  "ag-grid-community": "^32.x",
  "axios": "^1.x"
}
```

## Troubleshooting

### Backend Connection Issues
- Ensure FastAPI server is running on port 8000
- Check CORS configuration
- Verify API_BASE_URL in `src/services/api.js`

### Chart Not Showing
- Check if data format matches expected structure
- Open browser console for errors
- Verify data contains expected fields (date, KPI names)

## Development Notes
- Hot Module Replacement (HMR) enabled for fast development
- Component-based architecture for reusability
- Clean separation of concerns (components, services, pages)
