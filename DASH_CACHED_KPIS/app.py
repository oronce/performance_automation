"""
DASH Cached KPIs — FastAPI Gateway
Queries DuckDB (read-only) for Ericsson 2G / 3G / 4G main KPIs.
"""

import os
import sys
import datetime
import numpy as np
import pandas as pd
import duckdb
import mysql.connector
from mysql.connector import Error as MySQLError
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pandas.api.types import is_datetime64_any_dtype

# ── path setup: lets SQL/main.py find contants.py ────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "SQL"))

from main import generate_raw_sql                  # SQL/main.py
from SQL.sql_generator import generate_sql, generate_worst_cell_sql  # SQL/sql_generator.py
from cache_builder.config import DUCKDB_PATH       # cache_builder/config.py
from duck_client.router import router as duck_router  # DuckDB SQL client

# ── MySQL connection config ────────────────────────────────────────
MYSQL_CONFIG = {
    "host":     "10.22.33.116",
    "port":     3306,
    "database": "performanceroute",
    "user":     "root",
    "password": "performance",
}


# ── app ───────────────────────────────────────────────────────────

app = FastAPI(title="DASH Cached KPIs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(duck_router)

_STATIC_DIR = os.path.join(_HERE, "static")
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(os.path.join(_STATIC_DIR, "index.html"))


# ── DuckDB helper ─────────────────────────────────────────────────

def _run_query(sql: str) -> pd.DataFrame:
    """Execute SQL against DuckDB (read-only), return a DataFrame."""
    con = duckdb.connect(DUCKDB_PATH, read_only=True)
    try:
        df =  con.execute(sql).df()
        for col in df.columns:
            if is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.date
                break
            #     df[col] = df[col].dt.strftime("%Y-%m-%d")
        return df
    finally:
        con.close()


def _normalize_mysql_df(df: pd.DataFrame) -> pd.DataFrame:
    """Convert date/time/Decimal columns returned by MySQL to JSON-safe types."""
    if "date" in df.columns:
        df["date"] = df["date"].apply(
            lambda v: v.strftime("%Y-%m-%d") if hasattr(v, "strftime") else v
        )
    if "time" in df.columns:
        def fmt_time(v):
            if v is None or (isinstance(v, float) and pd.isna(v)):
                return v
            if isinstance(v, datetime.timedelta):
                total = int(v.total_seconds())
                return f"{total // 3600:02d}:{(total % 3600) // 60:02d}"
            if hasattr(v, "strftime"):
                return v.strftime("%H:%M")
            return v
        df["time"] = df["time"].apply(fmt_time)
    # Decimal → float
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(
                lambda v: float(v) if hasattr(v, "__float__") and not isinstance(v, str) else v
            )
    return df


def _run_mysql_query(sql: str) -> pd.DataFrame:
    """Execute SQL against MySQL, return a DataFrame."""
    con = mysql.connector.connect(**MYSQL_CONFIG)
    try:
        cursor = con.cursor(dictionary=True)
        cursor.execute(sql)
        rows = cursor.fetchall()
        return pd.DataFrame(rows) if rows else pd.DataFrame()
    finally:
        cursor.close()
        con.close()


def _merge_by_aggregation(
    frames: dict,           # {"2G": df, "3G": df, "4G": df}
    aggregation_level: str,
    include_time: bool,
) -> list:
    """
    Merge 2G/3G/4G DataFrames on date + aggregation_level.
    KPI columns are suffixed with _2G / _3G / _4G so nothing collides.
    Result: one row per (date, aggregation_value) with all tech KPIs together.
    """
    merge_keys = ["date", aggregation_level]
    if include_time:
        merge_keys.append("time")

    merged = None
    for tech, df in frames.items():
        if df.empty:
            continue
        # suffix all columns except the merge keys
        kpi_cols = [c for c in df.columns if c not in merge_keys]
        df = df.rename(columns={c: f"{c}_{tech}" for c in kpi_cols})

        if merged is None:
            merged = df
        else:
            merged = pd.merge(merged, df, on=merge_keys, how="outer")

    if merged is None:
        return []

    merged = merged.replace({np.nan: None})
    return merged.to_dict(orient="records")


# ── endpoints ─────────────────────────────────────────────────────


@app.get("/health")
def health():
    """Check DuckDB file is reachable."""
    if not os.path.exists(DUCKDB_PATH):
        raise HTTPException(status_code=503, detail=f"DuckDB not found at: {DUCKDB_PATH}")
    return {"status": "ok", "duckdb": DUCKDB_PATH}


@app.get("/main_kpis_availability")
def main_kpis_availability(
    start_date: str,
    end_date: str,
    time_granularity: str = "DAILY",
    aggregation_level: Optional[str] = None,
    vendor: str = "ERICSSON",
):
    """
    Fetch main KPIs from DuckDB for 2G, 3G and 4G.

    Parameters
    ----------
    start_date       : e.g. "2025-01-01"
    end_date         : e.g. "2025-01-31"
    time_granularity : DAILY | HOURLY | WEEKLY | MONTHLY
    aggregation_level: cell_name | site_name | commune | ... (optional)
    vendor           : ERICSSON | HUAWEI (default: ERICSSON)
    """
    include_time = time_granularity == "HOURLY"

    frames = {}
    errors = {}

    for tech in ["2G", "3G", "4G"]:
        try:
            sql = generate_raw_sql(
                query_category=tech,
                query_subcategory=vendor,
                query_name="MAIN_KPIS",
                time_granularity=time_granularity,
                start_date=start_date,
                end_date=end_date,
                aggregation_level=aggregation_level,
                include_time=include_time,
            )
            print(sql)
            frames[tech] = _run_query(sql)
        except Exception as e:
            errors[tech] = str(e)

    # if aggregation requested: merge all techs into one flat list per (date, agg_value)
    # if not: return each tech separately
    if aggregation_level and frames:
        data = _merge_by_aggregation(frames, aggregation_level, include_time)
    else:
        data = {tech: df.replace({np.nan: None}).to_dict(orient="records") for tech, df in frames.items()}

    return {
        "success": len(errors) == 0,
        "meta": {
            "start_date": start_date,
            "end_date": end_date,
            "time_granularity": time_granularity,
            "aggregation_level": aggregation_level,
            "vendor": vendor,
        },
        "data": data,
        "errors": errors if errors else None,
    }


@app.get("/sql_query")
def sql_query(
    script:            str,
    start_date:        str,
    end_date:          str,
    granularity:       str           = "DAILY",
    aggregation_level: Optional[str] = None,
):
    """
    Execute a SQL_SCRIPTS template against MySQL and return results.

    Parameters
    ----------
    script            : template name — 2g_ericsson | 2g_huawei | 3g_ericsson_packet_loss | 3g_huawei_packet_loss
    start_date        : "YYYY-MM-DD"
    end_date          : "YYYY-MM-DD"
    granularity       : DAILY | HOURLY | MONTHLY  (default: DAILY)
    aggregation_level : commune | arrondissement | (omit for no aggregation)
    """
    # ── enforce 8-day maximum ─────────────────────────────────────────
    MAX_DAYS = 8
    try:
        d_start = datetime.date.fromisoformat(start_date)
        d_end   = datetime.date.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    if d_end < d_start:
        raise HTTPException(status_code=400, detail="end_date must be >= start_date.")
    if (d_end - d_start).days + 1 > MAX_DAYS:
        raise HTTPException(
            status_code=400,
            detail=f"Date range exceeds {MAX_DAYS}-day maximum ({(d_end - d_start).days + 1} days requested)."
        )

    try:
        sql = generate_sql(
            script=script,
            start_date=start_date,
            end_date=end_date,
            granularity=granularity,
            aggregation_level=aggregation_level,
        )
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        df = _run_mysql_query(sql)
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=f"MySQL error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution error: {e}")

    df = _normalize_mysql_df(df)
    df = df.replace({np.nan: None})

    return {
        "success": True,
        "meta": {
            "script":            script,
            "start_date":        start_date,
            "end_date":          end_date,
            "granularity":       granularity,
            "aggregation_level": aggregation_level,
            "rows":              len(df),
        },
        "data": df.to_dict(orient="records"),
    }


@app.get("/worst_cells")
def worst_cells(
    script:            str,
    start_date:        str,
    end_date:          str,
    aggregation_level: Optional[str] = None,
    time_start:        Optional[str] = None,
    time_end:          Optional[str] = None,
    limit:             Optional[int] = None,
):
    """
    Execute a worst-cell SQL template against MySQL and return results.

    Parameters
    ----------
    script            : 2g_ericsson_worst_cell | 2g_huawei_worst_cell
    start_date        : "YYYY-MM-DD"
    end_date          : "YYYY-MM-DD"
    aggregation_level : None | cell_name | site_name | commune |
                        arrondissement | departement | controller_name
    time_start        : optional "HH:MM"  — filter time >= time_start
    time_end          : optional "HH:MM"  — filter time <= time_end
    limit             : optional row cap (e.g. 50 for top-50 bar chart)
    """
    try:
        sql = generate_worst_cell_sql(
            script=script,
            start_date=start_date,
            end_date=end_date,
            aggregation_level=aggregation_level,
            time_start=time_start,
            time_end=time_end,
        )
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    if limit is not None:
        sql = sql.rstrip() + f"\nLIMIT {int(limit)}"

    try:
        df = _run_mysql_query(sql)
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=f"MySQL error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {e}")

    df = _normalize_mysql_df(df)
    df = df.replace({np.nan: None})

    return {
        "success": True,
        "meta": {
            "script":            script,
            "start_date":        start_date,
            "end_date":          end_date,
            "aggregation_level": aggregation_level,
            "rows":              len(df),
        },
        "data": df.to_dict(orient="records"),
    }


# ── run ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)