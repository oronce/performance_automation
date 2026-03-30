import threading, time, datetime, os, sys, sqlite3
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import db_checker

app        = FastAPI()
SQLITE_DB  = db_checker.SQLITE_DB
FRONTEND   = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
TARGET_MIN = 40   # run at XX:40 every hour

# ── daemon ──────────────────────────────────────────────────
def daemon():
    last_hour = -1
    print("Initial check on startup...")
    try:    db_checker.run_check()
    except Exception as e: print(f"Init check failed: {e}")

    while True:
        time.sleep(60)
        now = datetime.datetime.now()
        if now.minute >= TARGET_MIN and now.hour != last_hour:
            last_hour = now.hour
            try:    db_checker.run_check()
            except Exception as e: print(f"Check failed: {e}")

threading.Thread(target=daemon, daemon=True).start()

# ── helpers ──────────────────────────────────────────────────
def db():
    c = sqlite3.connect(SQLITE_DB)
    c.row_factory = sqlite3.Row
    return c

# ── API ─────────────────────────────────────────────────────
@app.get('/api/trigger')
def trigger():
    try:    ts = db_checker.run_check(); return {'ok': True, 'timestamp': ts}
    except Exception as e: return {'ok': False, 'error': str(e)}

@app.get('/api/timestamps')
def timestamps():
    conn = db()
    rows = conn.execute("SELECT DISTINCT timestamp FROM snapshots ORDER BY timestamp DESC").fetchall()
    conn.close()
    return {'timestamps': [r[0] for r in rows]}

@app.get('/api/growth')
def growth(t1: str = None, t2: str = None):
    """
    Compare two snapshots (t1=oldest, t2=newest).
    If not provided, uses first and last available.
    Returns per-table: size at t1, size at t2, delta.
    """
    conn = db()

    if not t1 or not t2:
        rows = conn.execute("SELECT DISTINCT timestamp FROM snapshots ORDER BY timestamp ASC").fetchall()
        ts_list = [r[0] for r in rows]
        if len(ts_list) < 1:
            conn.close()
            return {'rows': [], 't1': None, 't2': None}
        t1 = ts_list[0]
        t2 = ts_list[-1]

    rows = conn.execute("""
        SELECT
            a.db_name,
            a.table_name,
            a.size_mb    AS size_t1,
            b.size_mb    AS size_t2,
            ROUND(b.size_mb - a.size_mb, 2) AS delta_mb,
            b.table_rows AS rows_t2
        FROM snapshots a
        JOIN snapshots b
          ON a.db_name = b.db_name AND a.table_name = b.table_name
         AND a.timestamp = ? AND b.timestamp = ?
        ORDER BY delta_mb DESC
    """, (t1, t2)).fetchall()

    conn.close()
    return {
        't1': t1, 't2': t2,
        'rows': [dict(r) for r in rows]
    }

@app.get('/api/history')
def history(db_name: str, table_name: str):
    """Full size history for one table — for a sparkline/chart."""
    conn = db()
    rows = conn.execute("""
        SELECT timestamp, size_mb, table_rows
        FROM snapshots
        WHERE db_name=? AND table_name=?
        ORDER BY timestamp ASC
    """, (db_name, table_name)).fetchall()
    conn.close()
    return {'history': [dict(r) for r in rows]}

app.mount('/', StaticFiles(directory=FRONTEND, html=True), name='static')

if __name__ == '__main__':
    print("=" * 50)
    print("  DB Size Monitor  →  http://localhost:8787")
    print("=" * 50)
    uvicorn.run(app, host='0.0.0.0', port=8787, log_level='warning')
