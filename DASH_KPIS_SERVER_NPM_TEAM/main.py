"""
KPI Dashboard Server - FastAPI Backend
Run with: uvicorn main:app --reload --port 8000
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from datetime import datetime, timedelta
import mysql.connector
import os
import sys

from config import DB_CONFIG, MAX_DAYS_ALLOWED, DEFAULT_DAYS, KPI_CHART_GROUPS, CHART_COLORS

# Worst-cell SQL generator lives in the sql/ directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "sql"))
from sql.worst_cell_generator import generate_worst_cell_sql

app = FastAPI(title="KPI Dashboard API")

# Serve static files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
SQL_DIR = os.path.join(os.path.dirname(__file__), "sql")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def get_db_connection():
    """Create database connection"""
    return mysql.connector.connect(**DB_CONFIG)


def load_sql_query(view='hourly'):
    """
    Load SQL query from file based on view type
    - hourly: uses kpi_query.sql (with time column)
    - daily: uses kpi_query_daily.sql (without time, aggregated by date)
    """
    if view == 'daily':
        sql_file = os.path.join(SQL_DIR, "kpi_query_daily.sql")
    else:
        sql_file = os.path.join(SQL_DIR, "kpi_query.sql")

    if not os.path.exists(sql_file):
        raise FileNotFoundError(f"SQL file not found: {sql_file}")
    with open(sql_file, 'r', encoding='utf-8') as f:
        return f.read()


def load_packet_loss_query(view='hourly'):
    """
    Load packet loss SQL query from file based on view type
    - hourly: uses cssr_paket_loss.sql (with TIME column)
    - daily: uses cssr_paket_loss_daily.sql (aggregated by date only)
    """
    if view == 'daily':
        sql_file = os.path.join(SQL_DIR, "cssr_paket_loss_daily.sql")
    else:
        sql_file = os.path.join(SQL_DIR, "cssr_paket_loss.sql")

    if not os.path.exists(sql_file):
        raise FileNotFoundError(f"SQL file not found: {sql_file}")
    with open(sql_file, 'r', encoding='utf-8') as f:
        return f.read()


def validate_date_range(start_date: str, end_date: str):
    """
    Validate date range - MAXIMUM 7 DAYS ALLOWED
    Returns tuple of (start_date, end_date) as date objects
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    if start > end:
        raise HTTPException(status_code=400, detail="Start date must be before end date")

    # CRITICAL: Enforce 7 day maximum
    days_diff = (end - start).days + 1
    if days_diff > MAX_DAYS_ALLOWED:
        raise HTTPException(
            status_code=400,
            detail=f"Date range exceeds maximum of {MAX_DAYS_ALLOWED} days. Requested: {days_diff} days"
        )

    return start, end


@app.get("/")
async def root():
    """Serve the main dashboard page"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/api/config")
async def get_config():
    """Return chart configuration to frontend"""
    return {
        "kpi_groups": KPI_CHART_GROUPS,
        "colors": CHART_COLORS,
        "max_days": MAX_DAYS_ALLOWED,
        "default_days": DEFAULT_DAYS
    }


@app.get("/api/kpi-data")
async def get_kpi_data(
    start_date: str = Query(..., description="Start date YYYY-MM-DD"),
    end_date: str = Query(..., description="End date YYYY-MM-DD"),
    view: str = Query("hourly", description="View type: 'hourly' or 'daily'")
):
    """
    Fetch KPI data for the given date range
    MAXIMUM 7 DAYS ALLOWED - enforced here
    view: 'hourly' for hourly data, 'daily' for daily aggregated data
    """
    # Validate view parameter
    if view not in ['hourly', 'daily']:
        view = 'hourly'

    # Validate date range (will raise HTTPException if invalid)
    start, end = validate_date_range(start_date, end_date)

    try:
        # Load SQL query based on view type
        sql_template = load_sql_query(view)

        # Replace date placeholders
        # YOUR SQL SHOULD USE: {start_date} and {end_date}
        sql_query = sql_template.format(
            start_date=start.strftime("%Y-%m-%d"),
            end_date=end.strftime("%Y-%m-%d")
        )

        # Execute query
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        # Process data for charts
        # Convert date/time to string for JSON serialization
        for row in rows:
            if 'date' in row and row['date']:
                if hasattr(row['date'], 'strftime'):
                    row['date'] = row['date'].strftime("%Y-%m-%d")
            if 'time' in row and row['time']:
                if hasattr(row['time'], 'total_seconds'):
                    # timedelta object
                    total_seconds = int(row['time'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    row['time'] = f"{hours:02d}:{minutes:02d}"
                elif hasattr(row['time'], 'strftime'):
                    row['time'] = row['time'].strftime("%H:%M")

            # Convert Decimal to float for JSON
            for key, value in row.items():
                if hasattr(value, '__float__'):
                    row[key] = float(value)

        return {
            "success": True,
            "data": rows,
            "start_date": start_date,
            "end_date": end_date,
            "total_records": len(rows)
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.get("/api/packet-loss-data")
async def get_packet_loss_data(
    start_date: str = Query(..., description="Start date YYYY-MM-DD"),
    end_date: str = Query(..., description="End date YYYY-MM-DD"),
    view: str = Query("hourly", description="View type: 'hourly' or 'daily'")
):
    """
    Fetch CSSR + Packet Loss data for the given date range.
    MAXIMUM 7 DAYS ALLOWED - enforced here.
    view: 'hourly' for hourly data, 'daily' for daily aggregated data.
    """
    if view not in ['hourly', 'daily']:
        view = 'hourly'

    # Validate date range (will raise HTTPException if invalid)
    start, end = validate_date_range(start_date, end_date)

    try:
        sql_template = load_packet_loss_query(view)

        sql_query = sql_template.format(
            start_date=start.strftime("%Y-%m-%d"),
            end_date=end.strftime("%Y-%m-%d")
        )

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        # Normalize date/time fields (SQL uses uppercase DATE / TIME aliases)
        for row in rows:
            for date_key in ('DATE', 'date'):
                if date_key in row and row[date_key]:
                    if hasattr(row[date_key], 'strftime'):
                        row[date_key] = row[date_key].strftime("%Y-%m-%d")
            for time_key in ('TIME', 'time'):
                if time_key in row and row[time_key]:
                    if hasattr(row[time_key], 'total_seconds'):
                        total_seconds = int(row[time_key].total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        row[time_key] = f"{hours:02d}:{minutes:02d}"
                    elif hasattr(row[time_key], 'strftime'):
                        row[time_key] = row[time_key].strftime("%H:%M")

            # Convert Decimal to float for JSON
            for key, value in row.items():
                if hasattr(value, '__float__'):
                    row[key] = float(value)

        return {
            "success": True,
            "data": rows,
            "start_date": start_date,
            "end_date": end_date,
            "total_records": len(rows)
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.get("/api/default-dates")
async def get_default_dates():
    """Get default date range (last N days based on config)"""
    today = datetime.now().date()
    start = today - timedelta(days=DEFAULT_DAYS - 1)
    return {
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date": today.strftime("%Y-%m-%d"),
        "default_days": DEFAULT_DAYS
    }


@app.get("/api/worst-cells")
async def get_worst_cells(
    script: str = Query(..., description="2g_ericsson_worst_cell | 2g_huawei_worst_cell"),
    start_date: str = Query(..., description="Start date YYYY-MM-DD"),
    end_date: str = Query(..., description="End date YYYY-MM-DD"),
    aggregation_level: str = Query(None, description="None | cell_name | site_name | commune | arrondissement | departement | controller_name"),
    time_start: str = Query(None, description="Optional time filter start HH:MM"),
    time_end: str = Query(None, description="Optional time filter end HH:MM"),
):
    """
    Fetch worst-cell / worst-site / geo breakdown data.
    No date-range cap here — caller controls the period.
    """
    try:
        start, end = validate_date_range(start_date, end_date)
    except HTTPException:
        raise

    try:
        sql_query = generate_worst_cell_sql(
            script=script,
            start_date=start.strftime("%Y-%m-%d"),
            end_date=end.strftime("%Y-%m-%d"),
            aggregation_level=aggregation_level,
            time_start=time_start,
            time_end=time_end,
        )

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        # Normalize Decimal → float for JSON serialization
        for row in rows:
            for key, value in row.items():
                if hasattr(value, '__float__'):
                    row[key] = float(value)

        return {
            "success": True,
            "data": rows,
            "total_records": len(rows),
        }

    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.get("/map")
async def serve_map():
    """Serve the Leaflet cell map page"""
    return FileResponse(os.path.join(STATIC_DIR, "map.html"))


if __name__ == "__main__":
    import uvicorn
    print("Starting KPI Dashboard Server...")
    print(f"Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)
