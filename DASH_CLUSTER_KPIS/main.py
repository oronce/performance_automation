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
    DEFAULT_DAYS, CHART_COLORS, TECHNOLOGIES
)

app = FastAPI(title="Cluster KPI Dashboard API")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
SQL_DIR    = os.path.join(os.path.dirname(__file__), "SQL")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# =============================================================================
# HELPERS — CONFIG LOOKUP
# =============================================================================

def get_vendor_cfg(tech: str, vendor: str) -> dict:
    """Return the vendor config dict or raise 400."""
    tech_cfg = TECHNOLOGIES.get(tech)
    if not tech_cfg:
        raise HTTPException(status_code=400, detail=f"Unknown technology: '{tech}'")
    vendor_cfg = tech_cfg["vendors"].get(vendor)
    if not vendor_cfg:
        raise HTTPException(status_code=400, detail=f"Unknown vendor: '{vendor}' for technology '{tech}'")
    return vendor_cfg


# =============================================================================
# HELPERS — DB / SQL
# =============================================================================

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def load_sql_template(vendor_cfg: dict) -> str:
    path = os.path.join(SQL_DIR, vendor_cfg["sql_file"])
    if not os.path.exists(path):
        raise FileNotFoundError(f"SQL file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_cell_filter(vendor_cfg: dict, batch: str) -> str:
    batches = vendor_cfg.get("batches", {})
    if batch not in batches:
        return ""
    cells = batches[batch]["cells"]
    if not cells:
        return ""
    cell_col = vendor_cfg["cell_col"]
    quoted   = ", ".join(f"'{c}'" for c in cells)
    return f"AND {cell_col} IN ({quoted})"


# =============================================================================
# HELPERS — VALIDATION
# =============================================================================

def validate_date_str(date_str: str):
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid date format '{date_str}'. Use YYYY-MM-DD")


def validate_date_range(start_date: str, end_date: str):
    start = validate_date_str(start_date)
    end   = validate_date_str(end_date)
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
    parts = [d.strip() for d in dates_str.split(",") if d.strip()]
    if len(parts) == 0:
        raise HTTPException(status_code=400, detail="No dates provided")
    if len(parts) > max_count:
        raise HTTPException(status_code=400, detail=f"Maximum {max_count} dates allowed. Got {len(parts)}")
    validated = []
    for p in parts:
        validated.append(validate_date_str(p).strftime("%Y-%m-%d"))
    return sorted(set(validated))


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


# =============================================================================
# ROUTES
# =============================================================================

@app.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/api/config")
async def get_config():
    technologies_out = {}
    for tech_key, tech_cfg in TECHNOLOGIES.items():
        vendors_out = {}
        for vendor_key, vendor_cfg in tech_cfg["vendors"].items():
            # Build batches — always include "all" first
            batches_out = {
                "all": {"label": "All Cells", "count": None, "cells": []}
            }
            for batch_key, batch_info in vendor_cfg["batches"].items():
                batches_out[batch_key] = {
                    "label": batch_info["label"],
                    "count": len(batch_info["cells"]),
                    "cells": batch_info["cells"],
                }
            vendors_out[vendor_key] = {
                "label":      vendor_cfg["label"],
                "kpi_groups": vendor_cfg["kpi_groups"],
                "batches":    batches_out,
            }
        technologies_out[tech_key] = {
            "label":   tech_cfg["label"],
            "vendors": vendors_out,
        }

    return {
        "colors":             CHART_COLORS,
        "max_days":           MAX_DAYS_ALLOWED,
        "max_specific_dates": MAX_SPECIFIC_DATES,
        "max_compare_days":   MAX_COMPARE_DAYS,
        "default_days":       DEFAULT_DAYS,
        "technologies":       technologies_out,
    }


@app.get("/api/kpi-data")
async def get_kpi_data(
    tech:       str           = Query("2g",     description="2g | 3g | 4g"),
    vendor:     str           = Query("ericsson", description="ericsson | huawei"),
    view:       str           = Query("hourly",  description="hourly | daily"),
    batch:      str           = Query("all",     description="all | <batch_key>"),
    start_date: Optional[str] = Query(None,      description="Start date YYYY-MM-DD (range mode)"),
    end_date:   Optional[str] = Query(None,      description="End date YYYY-MM-DD (range mode)"),
    dates:      Optional[str] = Query(None,      description="Comma-separated specific dates YYYY-MM-DD")
):
    # --- Validate tech + vendor ---
    vendor_cfg = get_vendor_cfg(tech, vendor)

    # --- Validate view ---
    if view not in ("hourly", "daily"):
        view = "hourly"

    # --- Validate batch ---
    valid_batches = {"all"} | set(vendor_cfg["batches"].keys())
    if batch not in valid_batches:
        batch = "all"

    # --- Build date_filter ---
    date_col = vendor_cfg["date_col"]

    if dates:
        date_list = validate_specific_dates(
            dates,
            MAX_COMPARE_DAYS if view == "hourly" else MAX_SPECIFIC_DATES
        )
        quoted      = ", ".join(f"'{d}'" for d in date_list)
        date_filter = f"{date_col} IN ({quoted})"
        meta        = {"dates": date_list}
    elif start_date and end_date:
        start, end  = validate_date_range(start_date, end_date)
        date_filter = f"{date_col} BETWEEN '{start.strftime('%Y-%m-%d')}' AND '{end.strftime('%Y-%m-%d')}'"
        meta        = {"start_date": start_date, "end_date": end_date}
    else:
        raise HTTPException(status_code=400, detail="Provide either 'dates' or both 'start_date' and 'end_date'")

    # --- Build time placeholders ---
    time_col    = vendor_cfg["time_col"]
    time_select = f",\n    {time_col} AS time" if view == "hourly" else ""
    time_group  = f",\n    {time_col}"         if view == "hourly" else ""

    # --- Build cell filter ---
    cell_filter = build_cell_filter(vendor_cfg, batch)

    try:
        sql_template = load_sql_template(vendor_cfg)
        sql_query    = sql_template.format(
            date_filter=date_filter,
            cell_filter=cell_filter,
            time_select=time_select,    
            time_group=time_group,
        )

        print(sql_query)

        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql_query)
        rows   = cursor.fetchall()
        cursor.close()
        conn.close()

        rows = serialize_rows(rows)

        return {
            "success":       True,
            "data":          rows,
            "tech":          tech,
            "vendor":        vendor,
            "batch":         batch,
            "view":          view,
            "total_records": len(rows),
            **meta
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.get("/api/cluster-cells/{tech}/{vendor}/{batch}/download")
async def download_cluster_cells(tech: str, vendor: str, batch: str):
    """Download the cell list for a given tech/vendor/batch as an XLSX file."""
    vendor_cfg = get_vendor_cfg(tech, vendor)

    batches = vendor_cfg["batches"]
    if batch not in batches:
        raise HTTPException(status_code=404, detail=f"Batch '{batch}' not found")

    batch_info = batches[batch]
    cells      = batch_info["cells"]
    label      = batch_info["label"].replace(" ", "_")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = label[:31]
    ws.column_dimensions["A"].width = 20
    ws.append(["Cell Name"])
    for cell in cells:
        ws.append([cell])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    filename = f"{tech}_{vendor}_{label}_cells.xlsx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/api/default-dates")
async def get_default_dates():
    today = datetime.now().date()
    start = today - timedelta(days=DEFAULT_DAYS - 1)
    return {
        "start_date":   start.strftime("%Y-%m-%d"),
        "end_date":     today.strftime("%Y-%m-%d"),
        "default_days": DEFAULT_DAYS
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
