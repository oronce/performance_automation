"""
Cluster KPI Dashboard - FastAPI Backend
Run with: uvicorn main:app --reload --port 8001
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from datetime import datetime, timedelta
from typing import Optional
import mysql.connector
import openpyxl
import io
import os

from config import (
    DB_CONFIG, MAX_DAYS_ALLOWED, MAX_SPECIFIC_DATES, MAX_COMPARE_DAYS,
    DEFAULT_DAYS, KPI_CHART_GROUPS, CHART_COLORS, BATCHES
)

app = FastAPI(title="Cluster KPI Dashboard API")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
SQL_DIR = os.path.join(os.path.dirname(__file__), "SQL")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def load_sql_template() -> str:
    path = os.path.join(SQL_DIR, "kpi_query.sql")
    if not os.path.exists(path):
        raise FileNotFoundError(f"SQL file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_cell_filter(batch: str) -> str:
    if batch not in BATCHES:
        return ""
    cells = BATCHES[batch]
    quoted = ", ".join(f"'{c}'" for c in cells)
    return f"AND h.CELL_NAME IN ({quoted})"


def validate_date_str(date_str: str):
    """Parse and return a date object, raise HTTPException on bad format."""
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid date format '{date_str}'. Use YYYY-MM-DD")


def validate_date_range(start_date: str, end_date: str):
    start = validate_date_str(start_date)
    end = validate_date_str(end_date)
    if start > end:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    days_diff = (end - start).days + 1
    if days_diff > MAX_DAYS_ALLOWED:
        raise HTTPException(
            status_code=400,
            detail=f"Date range exceeds maximum of {MAX_DAYS_ALLOWED} days. Requested: {days_diff} days"
        )
    return start, end


def validate_specific_dates(dates_str: str, max_count: int):
    """Parse comma-separated dates, validate each, return sorted list of date strings."""
    parts = [d.strip() for d in dates_str.split(",") if d.strip()]
    if len(parts) == 0:
        raise HTTPException(status_code=400, detail="No dates provided")
    if len(parts) > max_count:
        raise HTTPException(status_code=400, detail=f"Maximum {max_count} dates allowed. Got {len(parts)}")
    validated = []
    for p in parts:
        validated.append(validate_date_str(p).strftime("%Y-%m-%d"))
    return sorted(set(validated))  # deduplicate and sort


def serialize_rows(rows):
    for row in rows:
        if "date" in row and row["date"] and hasattr(row["date"], "strftime"):
            row["date"] = row["date"].strftime("%Y-%m-%d")
        if "time" in row and row["time"] is not None:
            if hasattr(row["time"], "total_seconds"):
                total_seconds = int(row["time"].total_seconds())
                row["time"] = f"{total_seconds // 3600:02d}:{(total_seconds % 3600) // 60:02d}"
            elif hasattr(row["time"], "strftime"):
                row["time"] = row["time"].strftime("%H:%M")
        for key, value in row.items():
            if hasattr(value, "__float__"):
                row[key] = float(value)
    return rows


@app.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/api/config")
async def get_config():
    return {
        "kpi_groups": KPI_CHART_GROUPS,
        "colors": CHART_COLORS,
        "max_days": MAX_DAYS_ALLOWED,
        "max_specific_dates": MAX_SPECIFIC_DATES,
        "max_compare_days": MAX_COMPARE_DAYS,
        "default_days": DEFAULT_DAYS,
        "batches": {
            "all":    {"label": "All Cells", "count": None,                      "cells": []},
            "batch1": {"label": "Cluster 1", "count": len(BATCHES["batch1"]), "cells": BATCHES["batch1"]},
            "batch2": {"label": "Cluster 2", "count": len(BATCHES["batch2"]), "cells": BATCHES["batch2"]},
        }
    }


@app.get("/api/kpi-data")
async def get_kpi_data(
    view:       str           = Query("hourly", description="hourly or daily"),
    batch:      str           = Query("all",    description="all | batch1 | batch2"),
    start_date: Optional[str] = Query(None,     description="Start date YYYY-MM-DD (range mode)"),
    end_date:   Optional[str] = Query(None,     description="End date YYYY-MM-DD (range mode)"),
    dates:      Optional[str] = Query(None,     description="Comma-separated specific dates YYYY-MM-DD")
):
    if view not in ("hourly", "daily"):
        view = "hourly"
    if batch not in ("all", "batch1", "batch2"):
        batch = "all"

    # --- Build date_filter ---
    if dates:
        # Specific dates mode (used by compare mode and specific-dates picker)
        date_list = validate_specific_dates(dates, MAX_COMPARE_DAYS if view == "hourly" else MAX_SPECIFIC_DATES)
        quoted = ", ".join(f"'{d}'" for d in date_list)
        date_filter = f"h.date IN ({quoted})"
        meta = {"dates": date_list}
    elif start_date and end_date:
        start, end = validate_date_range(start_date, end_date)
        date_filter = f"h.date BETWEEN '{start.strftime('%Y-%m-%d')}' AND '{end.strftime('%Y-%m-%d')}'"
        meta = {"start_date": start_date, "end_date": end_date}
    else:
        raise HTTPException(status_code=400, detail="Provide either 'dates' or both 'start_date' and 'end_date'")

    try:
        sql_template = load_sql_template()
        cell_filter  = build_cell_filter(batch)
        time_select  = ",\n    h.time" if view == "hourly" else ""
        time_group   = ",\n    h.time" if view == "hourly" else ""

        sql_query = sql_template.format(
            date_filter=date_filter,
            cell_filter=cell_filter,
            time_select=time_select,
            time_group=time_group
        )

        print(sql_query)

        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql_query)
        rows   = cursor.fetchall()
        cursor.close()
        conn.close()

        rows = serialize_rows(rows)

        return {"success": True, "data": rows, "batch": batch, "view": view,
                "total_records": len(rows), **meta}

    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.get("/api/cluster-cells/{batch}/download")
async def download_cluster_cells(batch: str):
    """Download the cell list for a given cluster as an XLSX file."""
    if batch not in BATCHES:
        raise HTTPException(status_code=404, detail="Cluster not found")

    cells = BATCHES[batch]
    label = "Cluster_1" if batch == "batch1" else "Cluster_2"

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = label
    ws.column_dimensions["A"].width = 20
    ws.append(["Cell Name"])
    for cell in cells:
        ws.append([cell])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={label}_cells.xlsx"}
    )


@app.get("/api/default-dates")
async def get_default_dates():
    today = datetime.now().date()
    start = today - timedelta(days=DEFAULT_DAYS - 1)
    return {
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date":   today.strftime("%Y-%m-%d"),
        "default_days": DEFAULT_DAYS
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
