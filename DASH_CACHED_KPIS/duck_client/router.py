"""
DuckDB SQL Client — FastAPI Router
===================================
Provides read-only access to the DuckDB cache via a clean REST API.
Designed to be reusable: mount this router into any FastAPI app or
call its endpoints from other projects.

Endpoints
---------
GET  /duck/ui                       → Web SQL client (browser UI)
GET  /duck/tables                   → List tables + row counts
GET  /duck/tables/{table}/schema    → Column names & types
GET  /duck/tables/{table}/data      → Paginated rows
POST /duck/query                    → Execute arbitrary SQL (read-only)
"""

import os
import time
import datetime
import decimal

import duckdb
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

# ── DuckDB path ──────────────────────────────────────────────────────────────
# Resolved relative to this file so the router works wherever it is imported from
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_HERE)

try:
    import sys
    sys.path.insert(0, _PROJECT_ROOT)
    from cache_builder.config import DUCKDB_PATH
except Exception:
    # Fall back: env var or default location
    DUCKDB_PATH = os.environ.get(
        "DUCKDB_PATH",
        os.path.join(_PROJECT_ROOT, "cache_builder", "assets", "cache.db"),
    )

_STATIC = os.path.join(_HERE, "static")

# ── Router ───────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/duck", tags=["DuckDB Client"])


# ── Internal helpers ─────────────────────────────────────────────────────────

def _connect() -> duckdb.DuckDBPyConnection:
    """Open a read-only DuckDB connection."""
    return duckdb.connect(DUCKDB_PATH, read_only=True)


def _safe(v):
    """Convert any Python value to a JSON-serialisable type."""
    if v is None:
        return None
    if isinstance(v, (datetime.datetime,)):
        return v.isoformat()
    if isinstance(v, datetime.date):
        return v.isoformat()
    if isinstance(v, datetime.time):
        return v.strftime("%H:%M:%S")
    if isinstance(v, datetime.timedelta):
        total = int(v.total_seconds())
        h, rem = divmod(total, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    if isinstance(v, decimal.Decimal):
        return float(v)
    if isinstance(v, bytes):
        return v.hex()
    return v


def _to_records(description, rows: list) -> list[dict]:
    cols = [d[0] for d in description]
    return [dict(zip(cols, [_safe(v) for v in row])) for row in rows]


# ── UI ───────────────────────────────────────────────────────────────────────

@router.get("/ui", include_in_schema=False)
def client_ui():
    """Serve the browser-based SQL client."""
    path = os.path.join(_STATIC, "client.html")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="UI not found.")
    return FileResponse(path, media_type="text/html")


# ── Tables ───────────────────────────────────────────────────────────────────

@router.get("/tables")
def list_tables():
    """
    List every table in the DuckDB cache together with its row count.

    Returns
    -------
    ```json
    {
      "db": "/path/to/cache.db",
      "tables": [
        {"name": "hourly_huawei_4g_all_counters_1", "rows": 142800},
        ...
      ]
    }
    ```
    """
    con = _connect()
    try:
        names = [r[0] for r in con.execute("SHOW TABLES").fetchall()]
        tables = []
        for name in names:
            count = con.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
            tables.append({"name": name, "rows": count})
        return {"db": DUCKDB_PATH, "tables": tables}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        con.close()


@router.get("/tables/{table}/schema")
def table_schema(table: str):
    """
    Return column definitions for *table*.

    Returns
    -------
    ```json
    {
      "table": "hourly_huawei_4g_all_counters_1",
      "columns": [
        {"name": "date",  "type": "DATE",           "nullable": "YES"},
        {"name": "TIME",  "type": "TIME",            "nullable": "YES"},
        {"name": "CSSR",  "type": "DECIMAL(38,12)",  "nullable": "YES"},
        ...
      ]
    }
    ```
    """
    con = _connect()
    try:
        rows = con.execute(f'DESCRIBE "{table}"').fetchall()
        return {
            "table": table,
            "columns": [
                {"name": r[0], "type": r[1], "nullable": r[2]}
                for r in rows
            ],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        con.close()


@router.get("/tables/{table}/data")
def table_data(table: str, limit: int = 200, offset: int = 0):
    """
    Return paginated rows from *table*.

    Parameters
    ----------
    limit   : rows per page, capped at 5 000 (default 200)
    offset  : skip first N rows (default 0)

    Returns
    -------
    ```json
    {
      "table": "...", "total": 142800, "limit": 200, "offset": 0,
      "columns": ["date", "TIME", "CSSR", ...],
      "rows": [{"date": "2026-03-14", "TIME": "00:00:00", ...}, ...]
    }
    ```
    """
    limit = min(max(1, limit), 5_000)
    con = _connect()
    try:
        rel = con.execute(f'SELECT * FROM "{table}" LIMIT {limit} OFFSET {offset}')
        records = _to_records(rel.description, rel.fetchall())
        total = con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        return {
            "table": table,
            "total": total,
            "limit": limit,
            "offset": offset,
            "columns": [d[0] for d in rel.description],
            "rows": records,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        con.close()


# ── Query execution ───────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    sql: str
    limit: Optional[int] = 2_000


@router.post("/query")
def execute_query(req: QueryRequest):
    """
    Execute arbitrary SQL against the DuckDB cache (read-only).

    This endpoint is intentionally generic so **other projects** can send
    requests here to read cached KPI data without needing to know the DuckDB
    file path or open a local connection.

    Body
    ----
    ```json
    { "sql": "SELECT date, CSSR FROM hourly_huawei_4g_all_counters_1 LIMIT 10",
      "limit": 2000 }
    ```

    Returns
    -------
    ```json
    {
      "success": true,
      "columns": ["date", "CSSR"],
      "rows":    [{"date": "2026-03-14", "CSSR": 98.7}, ...],
      "row_count": 10,
      "duration_ms": 4.2,
      "truncated": false
    }
    ```

    Notes
    -----
    - DuckDB is opened `read_only=True` — INSERT / UPDATE / DROP are rejected.
    - `limit` is capped at 10 000 rows to prevent runaway responses.
    - On SQL error the response is HTTP 400 with `detail` containing the message.
    """
    cap = min(req.limit or 2_000, 10_000)

    con = _connect()
    try:
        t0 = time.perf_counter()
        rel = con.execute(req.sql)
        description = rel.description or []
        cols = [d[0] for d in description]
        rows = rel.fetchmany(cap)
        duration_ms = round((time.perf_counter() - t0) * 1000, 2)

        return {
            "success": True,
            "columns": cols,
            "rows": _to_records(description, rows),
            "row_count": len(rows),
            "duration_ms": duration_ms,
            "truncated": len(rows) == cap,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        con.close()
