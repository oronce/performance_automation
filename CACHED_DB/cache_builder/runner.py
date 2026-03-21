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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger import get_logger

logger = get_logger()

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
    print("  STEP 3 — Loading data from MySQL into DuckDB")
    print(DIVIDER)
    kwargs = dict(start_date=start_date, end_date=end_date)
    if batch_days is not None:
        kwargs["batch_days"] = batch_days
    load_all_tables(tables, **kwargs)
    print("\n  Data load complete.")


def run_cleanup(tables: list = TABLES, max_days: int = 30) -> None:
    """Remove rows older than max_days from all DuckDB tables."""
    print(f"\n{DIVIDER}")
    logger.info("CLEANUP start: max_days=%d", max_days)
    print(f"  CLEANUP — Removing rows older than {max_days} days from DuckDB")
    print(DIVIDER)
    cleanup_old_data(tables, max_days=max_days, duckdb_path=DUCKDB_PATH)
    print("\n  Cleanup done.")


# ─────────────────────────────────────────────────────────────────────────────
#  RUN CONFIGURATION
#  Edit this block then run:  python runner.py
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    # ── Choose what to run ────────────────────────────────────
    RUN_STEP_1  = True    # inspect MySQL → generate & save create_tables.sql
    RUN_STEP_2  = True   # read create_tables.sql → create tables in DuckDB
    RUN_STEP_3  = True   # load data from MySQL into DuckDB
    RUN_CLEANUP = False   # remove rows older than MAX_DAYS

    # ── Date range for Step 3 (None = yesterday → today) ─────
    START_DATE = "2026-03-14"     # e.g. "2026-02-01"
    END_DATE   = "2026-03-15"     # e.g. "2026-02-21"

    # ── Day batch size for Step 3 ─────────────────────────────
    BATCH_DAYS = 2                # load N days per MySQL fetch (default 2)

    # ── Cleanup retention ─────────────────────────────────────
    MAX_DAYS = 30

   ### ─────────────────────────────────────────────────────────
    # if RUN_STEP_1:
    #     step1_inspect()

    # if RUN_STEP_2:
    #     step2_create()

    if RUN_STEP_3:
        step3_load(start_date=START_DATE, end_date=END_DATE, batch_days=BATCH_DAYS)

    # if RUN_CLEANUP:
    #     run_cleanup(max_days=MAX_DAYS)
