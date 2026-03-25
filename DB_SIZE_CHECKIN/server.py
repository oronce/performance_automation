"""
DB Size Monitor — FastAPI server + background daemon in one process.
Daemon fires every minute, executes size check at XX:40 each hour.
API: http://localhost:8787
"""

import threading
import time
import datetime
import os
import sys
import sqlite3

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import db_checker

# ─────────────────────────── app ───────────────────────────
app = FastAPI(title="DB Size Monitor", docs_url="/docs")

SQLITE_PATH = db_checker.SQLITE_PATH
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
TARGET_MINUTE = 40   # fire at XX:40

# ─────────────────────────── daemon ────────────────────────
_daemon_status = {"last_run": None, "last_error": None, "next_run": None}


def daemon_loop():
    last_run_hour = -1

    # Initial check on startup
    try:
        db_checker.run_check()
        _daemon_status["last_run"] = datetime.datetime.now().isoformat()
    except Exception as e:
        _daemon_status["last_error"] = str(e)
        print(f"[DAEMON] Initial check failed: {e}")

    while True:
        time.sleep(60)
        now = datetime.datetime.now()

        # Compute next scheduled time for status display
        next_min = TARGET_MINUTE if now.minute < TARGET_MINUTE else TARGET_MINUTE + 60
        next_run = now.replace(minute=next_min % 60, second=0, microsecond=0)
        if next_min >= 60:
            next_run += datetime.timedelta(hours=1)
        _daemon_status["next_run"] = next_run.isoformat()

        if now.minute >= TARGET_MINUTE and now.hour != last_run_hour:
            last_run_hour = now.hour
            print(f"[DAEMON] {now.strftime('%Y-%m-%d %H:%M:%S')} — running check...")
            try:
                db_checker.run_check()
                _daemon_status["last_run"] = now.isoformat()
                _daemon_status["last_error"] = None
            except Exception as e:
                _daemon_status["last_error"] = str(e)
                print(f"[DAEMON] Error: {e}")


# ─────────────────────────── helpers ───────────────────────
def sqlite():
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def latest_two_timestamps():
    conn = sqlite()
    c = conn.cursor()
    c.execute("SELECT DISTINCT timestamp FROM size_snapshots ORDER BY timestamp DESC LIMIT 2")
    ts = [r[0] for r in c.fetchall()]
    conn.close()
    return ts


# ─────────────────────────── API ───────────────────────────
@app.get("/api/status")
def api_status():
    return _daemon_status


@app.get("/api/trigger")
def api_trigger():
    try:
        db_checker.run_check()
        _daemon_status["last_run"] = datetime.datetime.now().isoformat()
        return {"ok": True}
    except Exception as e:
        _daemon_status["last_error"] = str(e)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.get("/api/summary")
def api_summary():
    ts = latest_two_timestamps()
    if not ts:
        return {"databases": [], "last_check": None, "prev_check": None}

    latest, prev = ts[0], (ts[1] if len(ts) > 1 else None)
    conn = sqlite()
    c = conn.cursor()

    c.execute("""
        SELECT db_name,
               SUM(size_bytes) total_bytes, SUM(size_mb) total_mb,
               COUNT(*) table_count, SUM(row_count) total_rows
        FROM size_snapshots WHERE timestamp=? GROUP BY db_name
    """, (latest,))
    current = {r["db_name"]: dict(r) for r in c.fetchall()}

    prev_data = {}
    if prev:
        c.execute("""
            SELECT db_name, SUM(size_bytes) total_bytes, SUM(size_mb) total_mb
            FROM size_snapshots WHERE timestamp=? GROUP BY db_name
        """, (prev,))
        prev_data = {r["db_name"]: dict(r) for r in c.fetchall()}

    conn.close()

    dbs = []
    for db_name, cur in current.items():
        growth_mb = 0.0
        growth_pct = 0.0
        if db_name in prev_data and prev_data[db_name]["total_mb"]:
            growth_mb = cur["total_mb"] - prev_data[db_name]["total_mb"]
            growth_pct = (growth_mb / prev_data[db_name]["total_mb"]) * 100

        dbs.append({
            "db_name":     db_name,
            "total_mb":    round(cur["total_mb"], 2),
            "total_gb":    round(cur["total_mb"] / 1024, 3),
            "table_count": cur["table_count"],
            "total_rows":  cur["total_rows"],
            "growth_mb":   round(growth_mb, 4),
            "growth_pct":  round(growth_pct, 4),
        })

    return {
        "databases":  sorted(dbs, key=lambda x: x["total_mb"], reverse=True),
        "last_check": latest,
        "prev_check": prev,
    }


@app.get("/api/tables")
def api_tables(db: str = None):
    ts = latest_two_timestamps()
    if not ts:
        return {"tables": []}

    latest, prev = ts[0], (ts[1] if len(ts) > 1 else None)
    conn = sqlite()
    c = conn.cursor()

    if db:
        c.execute("SELECT * FROM size_snapshots WHERE timestamp=? AND db_name=? ORDER BY size_bytes DESC", (latest, db))
    else:
        c.execute("SELECT * FROM size_snapshots WHERE timestamp=? ORDER BY size_bytes DESC", (latest,))
    current = {f"{r['db_name']}.{r['table_name']}": dict(r) for r in c.fetchall()}

    prev_data = {}
    if prev:
        q = "SELECT * FROM size_snapshots WHERE timestamp=?"
        args = [prev]
        if db:
            q += " AND db_name=?"
            args.append(db)
        c.execute(q, args)
        prev_data = {f"{r['db_name']}.{r['table_name']}": dict(r) for r in c.fetchall()}

    conn.close()

    tables = []
    for key, cur in current.items():
        p = prev_data.get(key, {})
        prev_mb = p.get("size_mb", 0) or 0
        growth_mb = cur["size_mb"] - prev_mb
        growth_pct = (growth_mb / prev_mb * 100) if prev_mb > 0 else 0

        tables.append({
            "db_name":    cur["db_name"],
            "table_name": cur["table_name"],
            "size_mb":    round(cur["size_mb"], 4),
            "size_bytes": cur["size_bytes"],
            "row_count":  cur["row_count"],
            "growth_mb":  round(growth_mb, 6),
            "growth_pct": round(growth_pct, 4),
            "is_new":     key not in prev_data,
        })

    return {"tables": sorted(tables, key=lambda x: x["size_mb"], reverse=True)}


@app.get("/api/history")
def api_history():
    conn = sqlite()
    c = conn.cursor()
    c.execute("""
        SELECT timestamp, db_name, SUM(size_mb) total_mb
        FROM size_snapshots
        GROUP BY timestamp, db_name
        ORDER BY timestamp ASC
    """)
    rows = c.fetchall()
    conn.close()

    history = {}
    for r in rows:
        db = r["db_name"]
        if db not in history:
            history[db] = {"labels": [], "data": []}
        history[db]["labels"].append(r["timestamp"][5:16])   # MM-DD HH:MM
        history[db]["data"].append(round(r["total_mb"], 2))

    return {"history": history}


@app.get("/api/top-growth")
def api_top_growth(limit: int = 15):
    ts = latest_two_timestamps()
    if len(ts) < 2:
        return {"tables": []}

    latest, prev = ts[0], ts[1]
    conn = sqlite()
    c = conn.cursor()
    c.execute("""
        SELECT c.db_name, c.table_name,
               c.size_mb    AS current_mb,
               COALESCE(p.size_mb, 0) AS prev_mb,
               (c.size_mb - COALESCE(p.size_mb, 0)) AS growth_mb
        FROM size_snapshots c
        LEFT JOIN size_snapshots p
               ON c.db_name=p.db_name AND c.table_name=p.table_name AND p.timestamp=?
        WHERE c.timestamp=?
        ORDER BY growth_mb DESC
        LIMIT ?
    """, (prev, latest, limit))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()

    for r in rows:
        r["current_mb"] = round(r["current_mb"], 4)
        r["prev_mb"]    = round(r["prev_mb"], 4)
        r["growth_mb"]  = round(r["growth_mb"], 6)
        r["growth_pct"] = round((r["growth_mb"] / r["prev_mb"] * 100) if r["prev_mb"] > 0 else 0, 2)

    return {"tables": rows}


# ─────────────────────────── static ────────────────────────
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")

# ─────────────────────────── main ──────────────────────────
if __name__ == "__main__":
    t = threading.Thread(target=daemon_loop, daemon=True, name="daemon")
    t.start()
    print("=" * 55)
    print("  DB Size Monitor")
    print("  Dashboard → http://localhost:8787")
    print(f"  Scheduled check at XX:{TARGET_MINUTE:02d} every hour")
    print("=" * 55)
    uvicorn.run(app, host="0.0.0.0", port=8787, log_level="warning")
