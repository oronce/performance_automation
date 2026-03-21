"""
DuckDB SQL Client — FastAPI Router
===================================
Provides read-only access to the DuckDB cache via a clean REST API.
Designed to be reusable: mount this router into any FastAPI app or
call its endpoints from other projects.

Endpoints
---------
GET    /duck/ui                        → Web SQL client (browser UI)
GET    /duck/tables                    → List tables + row counts
GET    /duck/tables/{table}/schema     → Column names & types
GET    /duck/tables/{table}/data       → Paginated rows
POST   /duck/query                     → Execute arbitrary SQL (read-only)
GET    /duck/queries                   → List saved queries
POST   /duck/queries                   → Save a query (max 20)
GET    /duck/queries/{name}            → Load a saved query
DELETE /duck/queries/{name}            → Delete a saved query
"""

import os
import re
import time
import datetime
import decimal
from pathlib import Path

import csv
import io

import duckdb
import pandas as pd
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional

# ── DuckDB path ──────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_HERE)

try:
    import sys
    sys.path.insert(0, _PROJECT_ROOT)
    from cache_builder.config import DUCKDB_PATH
except Exception:
    DUCKDB_PATH = os.environ.get(
        "DUCKDB_PATH",
        os.path.join(_PROJECT_ROOT, "cache_builder", "assets", "cache.db"),
    )

_STATIC = os.path.join(_HERE, "static")

# ── Saved queries directory ───────────────────────────────────────────────────
QUERIES_DIR  = Path(_HERE) / "saved_queries"
MAX_QUERIES  = 20
QUERIES_DIR.mkdir(exist_ok=True)

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
    if isinstance(v, datetime.datetime):
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


def _sanitize_query_name(name: str) -> str:
    """Return a safe filename stem (alphanumeric + underscore + dash, max 64 chars)."""
    name = name.strip()
    name = re.sub(r"[^\w\s\-]", "", name)   # strip special chars
    name = re.sub(r"\s+", "_", name)         # spaces → underscores
    return name[:64]


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
      "tables": [{"name": "hourly_huawei_4g_all_counters_1", "rows": 142800}, ...]
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
    """Return column definitions (name, type, nullable) for *table*."""
    con = _connect()
    try:
        rows = con.execute(f'DESCRIBE "{table}"').fetchall()
        return {
            "table": table,
            "columns": [{"name": r[0], "type": r[1], "nullable": r[2]} for r in rows],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        con.close()


@router.get("/tables/{table}/data")
def table_data(table: str, limit: int = 200, offset: int = 0):
    """
    Return paginated rows from *table*.

    Parameters  limit (max 5 000) / offset.
    """
    limit = min(max(1, limit), 5_000)
    con = _connect()
    try:
        rel     = con.execute(f'SELECT * FROM "{table}" LIMIT {limit} OFFSET {offset}')
        records = _to_records(rel.description, rel.fetchall())
        total   = con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        return {
            "table":   table,
            "total":   total,
            "limit":   limit,
            "offset":  offset,
            "columns": [d[0] for d in rel.description],
            "rows":    records,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        con.close()


# ── Query execution ───────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    sql:   str
    limit: Optional[int] = 2_000


@router.post("/query")
def execute_query(req: QueryRequest):
    """
    Execute arbitrary SQL against the DuckDB cache (read-only).

    Body  `{ "sql": "SELECT ...", "limit": 2000 }`

    Returns  `{ "success", "columns", "rows", "row_count", "duration_ms", "truncated" }`

    Notes
    -----
    - DuckDB opened `read_only=True` — writes are rejected by the engine.
    - `limit` capped at 10 000 rows.
    """
    cap = min(req.limit or 2_000, 10_000)
    con = _connect()
    try:
        t0          = time.perf_counter()
        rel         = con.execute(req.sql)
        description = rel.description or []
        cols        = [d[0] for d in description]
        rows        = rel.fetchmany(cap)
        duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "success":     True,
            "columns":     cols,
            "rows":        _to_records(description, rows),
            "row_count":   len(rows),
            "duration_ms": duration_ms,
            "truncated":   len(rows) == cap,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        con.close()


# ── Export ────────────────────────────────────────────────────────────────────

_CHUNK = 2_000   # rows per fetch batch


def _iter_csv(sql: str):
    """
    Generator that streams query results as CSV in chunks.
    Rows are fetched from DuckDB in batches of _CHUNK so the full
    result set is never held in memory at once.
    """
    con = _connect()
    try:
        rel  = con.execute(sql)
        cols = [d[0] for d in rel.description]
        buf  = io.StringIO()
        w    = csv.writer(buf)
        w.writerow(cols)
        yield buf.getvalue().encode()

        while True:
            rows = rel.fetchmany(_CHUNK)
            if not rows:
                break
            buf = io.StringIO()
            w   = csv.writer(buf)
            w.writerows(rows)
            yield buf.getvalue().encode()
    finally:
        con.close()


def _build_xlsx(sql: str) -> io.BytesIO:
    """
    Build an Excel file using xlsxwriter (5-10× faster than openpyxl).
    The entire DataFrame must be in memory — prefer CSV for large exports.
    """
    con = _connect()
    try:
        df = con.execute(sql).df()
    finally:
        con.close()

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Export")
    buf.seek(0)
    return buf


@router.post("/export")
def export_query(
    sql:    str = Form(...),
    format: str = Form("xlsx"),   # "xlsx" or "csv"
):
    """
    Run *sql* (submitted as an HTML form POST) and stream the result as a file.

    The browser submits this via a hidden `<form>` so the download is handled
    natively — the response is never loaded into JS memory.

    - **csv**  — true row-by-row streaming; safe for any result size.
    - **xlsx** — full DataFrame built server-side with xlsxwriter; fast but
                  requires the whole result set to fit in server RAM.

    Fields  `sql` (required), `format` ("xlsx" | "csv", default "xlsx")
    """
    if format not in ("xlsx", "csv"):
        raise HTTPException(status_code=400, detail="format must be 'xlsx' or 'csv'.")

    if format == "csv":
        try:
            # Validate SQL before streaming (fetchmany(0) is a dry-run)
            con = _connect()
            try:
                con.execute(sql).fetchmany(0)
            finally:
                con.close()
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        return StreamingResponse(
            _iter_csv(sql),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=export.csv"},
        )

    # xlsx
    try:
        buf = _build_xlsx(sql)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=export.xlsx"},
    )


# ── Saved queries ─────────────────────────────────────────────────────────────

class SaveQueryRequest(BaseModel):
    name: str
    sql:  str


@router.get("/queries")
def list_queries():
    """
    List all saved queries, newest first.

    Returns
    -------
    ```json
    { "queries": [{"name": "my_query", "modified": 1234567890.0}, ...] }
    ```
    """
    files = sorted(QUERIES_DIR.glob("*.sql"), key=lambda f: f.stat().st_mtime, reverse=True)
    return {
        "queries": [
            {"name": f.stem, "modified": f.stat().st_mtime}
            for f in files
        ]
    }


@router.post("/queries")
def save_query(req: SaveQueryRequest):
    """
    Save a query to disk.

    - Name is sanitised to a safe filename.
    - Overwrites an existing query with the same name.
    - Returns HTTP 400 if the 20-query limit is reached (for new files only).

    Body  `{ "name": "my_query", "sql": "SELECT ..." }`
    """
    name = _sanitize_query_name(req.name)
    if not name:
        raise HTTPException(status_code=400, detail="Query name cannot be empty.")

    target   = QUERIES_DIR / f"{name}.sql"
    existing = list(QUERIES_DIR.glob("*.sql"))

    if not target.exists() and len(existing) >= MAX_QUERIES:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum of {MAX_QUERIES} saved queries reached. Delete one first.",
        )

    target.write_text(req.sql, encoding="utf-8")
    return {"success": True, "name": name}


@router.get("/queries/{name}")
def get_query(name: str):
    """
    Load a saved query by name.

    Returns  `{ "name": "my_query", "sql": "SELECT ..." }`
    """
    safe = _sanitize_query_name(name)
    path = QUERIES_DIR / f"{safe}.sql"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Query '{safe}' not found.")
    return {"name": safe, "sql": path.read_text(encoding="utf-8")}


@router.delete("/queries/{name}")
def delete_query(name: str):
    """Delete a saved query by name."""
    safe = _sanitize_query_name(name)
    path = QUERIES_DIR / f"{safe}.sql"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Query '{safe}' not found.")
    path.unlink()
    return {"success": True, "name": safe}
