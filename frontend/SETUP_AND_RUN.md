# Setup and Run - FIXED

## Issues Fixed:
1. ✅ Dark background removed (layout now full screen)
2. ✅ CORS setup ready (backend needs to be started)

## Quick Setup

### 1. Install Backend Dependencies
```bash
cd performance_automation/API_SERVER
pip install fastapi uvicorn[standard]
```

### 2. Start Backend Server
```bash
python start_server.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 3. Start Frontend (New Terminal)
```bash
cd performance_automation/frontend/kpi-dashboard
npm run dev
```

### 4. Open Browser
Navigate to: `http://localhost:5173`

The page should now:
- ✅ Take full screen (no dark area)
- ✅ Load data from backend
- ✅ Show charts and tables

## Troubleshooting

### Backend not starting?
Make sure you have MySQL credentials in app.py or update the database connection.

### Still seeing CORS error?
1. Check backend is running: `http://localhost:8000/api/health`
2. If it shows connection refused, backend isn't running
3. Check firewall/antivirus blocking port 8000

### Frontend shows "No data available"?
1. Backend is running but database connection failed
2. Check browser console for exact error
3. Update database credentials in app.py

## Files Created for Backend:
- `API_SERVER/requirements.txt` - FastAPI dependencies
- `API_SERVER/start_server.py` - Server startup script

## Files Modified:
- `frontend/kpi-dashboard/src/index.css` - Fixed dark background

That's it! 🎉
