# Backend Debugging Guide

## How to See Server-Side Errors

### 1. Enhanced Logging Added ✅

The backend now prints:
- **Generated SQL query** before execution
- **Full error traceback** when something fails

### 2. Restart the Backend

```bash
# Stop the current server (Ctrl+C)
# Start it again
python start_server.py
```

### 3. Check the Terminal Output

When you refresh the frontend, you'll see:

**On Success:**
```
================================================================================
EXECUTING QUERY:
SELECT DATE AS date,
    100 * (SUM(Suc_SDCCH_Seiz) / NULLIF(SUM(SDCCH_Seiz_Req), 0)) AS CSSR_HUAWEI
FROM hourly_arcep_huawei_2g t
WHERE DATE >= '2025-11-20' AND DATE <= '2025-11-30'
GROUP BY DATE
ORDER BY DATE
================================================================================
```

**On Error:**
```
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
ERROR IN QUERY EXECUTION:
Traceback (most recent call last):
  File "app.py", line 650, in execute_query
    results = db_manager.execute_query(sql_query)
  File "app.py", line 112, in execute_query
    cursor.execute(query)
mysql.connector.errors.ProgrammingError: 1146 (42S02): Table 'local_perf.hourly_arcep_huawei_2g' doesn't exist
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```

## Common Errors and Fixes

### Error 1: "Can't connect to MySQL server"
```
mysql.connector.errors.DatabaseError: 2003 (HY000): Can't connect to MySQL server
```
**Fix:** Start MySQL service

### Error 2: "Table doesn't exist"
```
ProgrammingError: 1146 (42S02): Table 'local_perf.hourly_arcep_huawei_2g' doesn't exist
```
**Fix:**
- Check database name in app.py (line 40-47)
- Check table name in QUERY_CONFIG
- Verify table exists in your database

### Error 3: "Access denied"
```
mysql.connector.errors.ProgrammingError: 1045 (28000): Access denied for user 'root'@'localhost'
```
**Fix:** Update credentials in app.py:
```python
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "database": "your_database_name",  # Change this
    "user": "your_username",           # Change this
    "password": "your_password",       # Change this
    "charset": "utf8mb4"
}
```

### Error 4: "No data returned"
```
Success! Got 0 rows
```
**Fix:**
- Check date range (data exists for those dates?)
- Check filters (too restrictive?)
- Look at the SQL query in logs

## Frontend Debugging

The frontend now shows the actual error message in the alert:
```javascript
alert(`Failed to load data: ${errorMsg}\n\nCheck browser console and backend logs for details.`);
```

## Quick Debug Checklist

1. ✅ Is MySQL running?
2. ✅ Is the database name correct?
3. ✅ Do the tables exist?
4. ✅ Are credentials correct?
5. ✅ Does data exist for the date range?
6. ✅ Check backend terminal for SQL query
7. ✅ Check browser console for frontend errors

## Test Endpoints

### Health Check
```bash
curl http://localhost:8000/api/health
```

Should return:
```json
{"status": "healthy", "database": "connected"}
```

### Test Query Directly
```bash
curl -X POST http://localhost:8000/api/data/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_category": "2G",
    "query_subcategory": "HUAWEI",
    "query_name": "KPI_MONITORING2",
    "time_granularity": "DAILY",
    "selected_kpis": ["CSSR_HUAWEI"],
    "include_date": true,
    "start_date": "2025-11-20",
    "end_date": "2025-11-30"
  }'
```

## Now You Have Full Visibility! 🔍

- Backend logs show SQL queries and errors
- Frontend shows error messages
- Response includes the query for debugging