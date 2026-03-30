"""
runner.py
─────────
3-step orchestrator for building the DuckDB KPI cache.

  Step 1 — INSPECT : Connect to MySQL, DESC each table,
                     generate DuckDB CREATE TABLE SQL,
                     save to create_tables.sql for review/edit.

  Step 2 — CREATE  : Read create_tables.sql and create tables in DuckDB.
                     Edit the file before running this step if needed.

  Step 3 — LOAD    : Fetch data from MySQL and insert into DuckDB.

HOW TO USE:
  Edit the RUN CONFIGURATION block at the bottom, then run:
    python runner.py
"""

import sys
import os
import json
import argparse
import traceback
from datetime import date, timedelta, datetime as _dt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger import get_logger

logger = get_logger()

# ─────────────────────────────────────────────────────────────────────────────
#  Status file  (read by the FastAPI /duck/runner/status endpoint)
# ─────────────────────────────────────────────────────────────────────────────

_STATUS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "assets", "runner_status.json"
)


def _write_status(step: str, label: str, status: str,
                  start_time: str = None, message: str = None, error: str = None):
    """Write current runner state to JSON — atomic write via tmp+rename."""
    now = _dt.now().isoformat(timespec="seconds")
    data = {
        "step":       step,
        "label":      label,
        "status":     status,       # "running" | "done" | "failed"
        "start_time": start_time or now,
        "end_time":   now if status in ("done", "failed") else None,
        "message":    message,
        "error":      error,
        "updated_at": now,
    }
    os.makedirs(os.path.dirname(_STATUS_FILE), exist_ok=True)
    tmp = _STATUS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, _STATUS_FILE)


def _run_step(step_key: str, label: str, fn, *args, **kwargs):
    """
    Run a step function with status tracking and error handling.
    Writes runner_status.json before (running) and after (done/failed).
    Logs the full traceback on failure, then re-raises.
    """
    start = _dt.now().isoformat(timespec="seconds")
    _write_status(step_key, label, "running", start_time=start)
    try:
        fn(*args, **kwargs)
        _write_status(step_key, label, "done", start_time=start)
    except Exception as exc:
        err_detail = traceback.format_exc()
        logger.error("%s FAILED: %s\n%s", label, exc, err_detail)
        _write_status(step_key, label, "failed", start_time=start, error=str(exc))
        raise

try:
    from .config           import TABLES, DUCKDB_PATH, SQL_FILE_PATH
    from .schema_inspector import generate_all
    from .duck_manager     import create_tables_from_file, load_all_tables, cleanup_old_data
except ImportError:
    from config            import TABLES, DUCKDB_PATH, SQL_FILE_PATH
    from schema_inspector  import generate_all
    from duck_manager      import create_tables_from_file, load_all_tables, cleanup_old_data


DIVIDER = "=" * 70


# ─────────────────────────────────────────────────────────────────────────────
#  Step functions
# ─────────────────────────────────────────────────────────────────────────────

def step1_inspect(tables: list = TABLES, sql_file: str = SQL_FILE_PATH) -> None:
    """
    Connect to MySQL, DESC each table, generate CREATE TABLE SQL
    and save it to sql_file.
    Open and edit that file before running Step 2 if needed.
    """
    print(f"\n{DIVIDER}")
    logger.info("STEP 1 start")
    print("  STEP 1 — Inspecting MySQL tables & generating DuckDB SQL")
    print(DIVIDER)

    sqls = generate_all(tables)

    failed = [k for k, v in sqls.items() if v is None]

    # build the file content
    lines = []
    for table_name, sql in sqls.items():
        if sql is None:
            lines.append(f"-- [FAILED] {table_name} — could not generate SQL\n")
        else:
            lines.append(sql + "\n")

    # resolve path relative to this file so it always lands next to runner.py
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), sql_file)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n  SQL saved to: {out_path}")
    print("  Open that file, review or edit the types, then run Step 2.")

    if failed:
        print(f"\n  WARNING: {len(failed)} table(s) failed — check MySQL connection / table names.")
        for t in failed:
            print(f"    - {t}")


def step2_create(sql_file: str = SQL_FILE_PATH) -> None:
    """
    Read the SQL file produced by Step 1 and create the tables in DuckDB.
    You can manually edit the file before running this step.
    """
    sql_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), sql_file)

    if not os.path.exists(sql_path):
        print(f"\n  ERROR: SQL file not found: {sql_path}")
        print("  Run Step 1 first to generate it.")
        return

    print(f"\n{DIVIDER}")
    logger.info("STEP 2 start")
    print("  STEP 2 — Creating tables in DuckDB")
    print(f"  Reading from: {sql_path}")
    print(DIVIDER)
    create_tables_from_file(sql_path, duckdb_path=DUCKDB_PATH)
    print("\n  All tables created.")


def step3_load(tables: list = TABLES, start_date: str = None, end_date: str = None, batch_days: int = None) -> None:
    """Fetch data from MySQL and insert into DuckDB."""
    print(f"\n{DIVIDER}")
    logger.info("STEP 3 start: %s -> %s  batch_days=%s", start_date, end_date, batch_days)
    print("  STEP 3 - Loading data from MySQL into DuckDB")
    print(DIVIDER)
    kwargs = dict(start_date=start_date, end_date=end_date)
    if batch_days is not None:
        kwargs["batch_days"] = batch_days
    load_all_tables(tables, **kwargs)
    print("\n  Data load complete.")


def run_cleanup(tables: list = TABLES, max_days: int = 30) -> None:
    """Remove rows older than max_days from all DuckDB tables, then VACUUM + CHECKPOINT."""
    import duckdb as _duckdb
    print(f"\n{DIVIDER}")
    logger.info("CLEANUP start: max_days=%d", max_days)
    print(f"  CLEANUP — Removing rows older than {max_days} days from DuckDB")
    print(DIVIDER)
    cleanup_old_data(tables, max_days=max_days, duckdb_path=DUCKDB_PATH)

    print("  Running VACUUM + CHECKPOINT to reclaim disk space ...")
    con = _duckdb.connect(DUCKDB_PATH)
    try:
        con.execute("VACUUM")
        con.execute("CHECKPOINT")
    finally:
        con.close()
    print("\n  Cleanup done.")


# ─────────────────────────────────────────────────────────────────────────────
#  CLI  — each step callable independently (cron-friendly)
#
#  Usage
#  -----
#  python runner.py step1
#  python runner.py step2
#  python runner.py step3                          # defaults: yesterday → today
#  python runner.py step3 --start 2026-03-01 --end 2026-03-21
#  python runner.py step3 --days-back 7            # last 7 days
#  python runner.py cleanup
#  python runner.py cleanup --max-days 60
#  python runner.py all                            # step1 + step2 + step3 + cleanup
#
#  Cron examples
#  -------------
#  # Daily load at 06:00
#  0 6 * * * /path/to/venv/python /path/to/runner.py step3
#
#  # Weekly cleanup every Sunday at 02:00
#  0 2 * * 0 /path/to/venv/python /path/to/runner.py cleanup --max-days 30
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="runner.py",
        description="DuckDB cache builder — run individual steps or all at once.",
    )
    parser.add_argument(
        "step",
        choices=["step1", "step2", "step3", "cleanup", "all"],
        help="Which step to execute.",
    )
    parser.add_argument("--start",     default=None, help="Start date YYYY-MM-DD (step3)")
    parser.add_argument("--end",       default=None, help="End date   YYYY-MM-DD (step3)")
    parser.add_argument("--days", type=int, default=None,
                        help="Load last N days ending today (step3, overrides --start/--end)")
    parser.add_argument("--batch-days", type=int, default=None,
                        help="Days per MySQL fetch batch (step3, default from config)")
    parser.add_argument("--max-days",  type=int, default=30,
                        help="Retention days for cleanup (default 30)")

    args = parser.parse_args()

    # ── Resolve date range for step3 ──────────────────────────
    start_date = args.start
    end_date   = args.end

    if args.days is not None:
        end_date   = str(date.today())
        start_date = str(date.today() - timedelta(days=args.days - 1))

    # ── Dispatch ──────────────────────────────────────────────
    if args.step in ("step1", "all"):
        _run_step("step1", "STEP 1 — Inspect MySQL / generate SQL",
                  step1_inspect)

    if args.step in ("step2", "all"):
        _run_step("step2", "STEP 2 — Create tables in DuckDB",
                  step2_create)

    if args.step in ("step3", "all"):
        _run_step("step3", "STEP 3 - Load data MySQL -> DuckDB",
                  step3_load,
                  start_date=start_date, end_date=end_date, batch_days=args.batch_days)

    if args.step in ("cleanup", "all"):
        _run_step("cleanup", "CLEANUP — Remove old rows",
                  run_cleanup, max_days=args.max_days)
