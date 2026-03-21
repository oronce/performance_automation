"""
test_db.py
──────────
Quick sanity checks on the DuckDB cache:
  1. Check if cache.db exists
  2. List all tables
  3. Show row count per table
  4. Show first 3 rows of each table

Run:  python test_db.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from .config import DUCKDB_PATH, TABLES
except ImportError:
    from config import DUCKDB_PATH, TABLES

import duckdb

DIVIDER = "=" * 70


def run_checks() -> None:

    # ── 1. Does the file exist? ───────────────────────────────
    print(f"\n{DIVIDER}")
    print("  CHECK 1 — DuckDB file")
    print(DIVIDER)
    print(f"  Path : {DUCKDB_PATH}")

    if not os.path.exists(DUCKDB_PATH):
        print("  STATUS: FILE NOT FOUND — run Step 2 first to create tables.")
        return

    size_mb = os.path.getsize(DUCKDB_PATH) / (1024 * 1024)
    print(f"  STATUS: EXISTS  ({size_mb:.2f} MB)")

    con = duckdb.connect(DUCKDB_PATH, read_only=True)

    try:
        # ── 2. List all tables ────────────────────────────────
        print(f"\n{DIVIDER}")
        print("  CHECK 2 — Tables in DuckDB")
        print(DIVIDER)

        tables_in_db = con.execute("SHOW TABLES").fetchall()

        if not tables_in_db:
            print("  No tables found — run Step 2 to create them.")
            return

        for (tbl,) in tables_in_db:
            print(f"  - {tbl}")

        # ── 3. Row count per table ────────────────────────────
        print(f"\n{DIVIDER}")
        print("  CHECK 3 — Row counts")
        print(DIVIDER)

        for (tbl,) in tables_in_db:
            count = con.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
            status = f"{count:,} rows" if count > 0 else "EMPTY"
            print(f"  {tbl:<45} {status}")

        # ── 4. First 3 rows per table ─────────────────────────
        print(f"\n{DIVIDER}")
        print("  CHECK 4 — First 3 rows per table")
        print(DIVIDER)

        for (tbl,) in tables_in_db:
            print(f"\n  Table: {tbl}")
            print(f"  {'-' * 60}")
            rows = con.execute(f"SELECT * FROM {tbl} LIMIT 3").fetchall()
            cols = [d[0] for d in con.execute(f"SELECT * FROM {tbl} LIMIT 0").description]
            print(f"  Columns: {cols}")
            if rows:
                for row in rows:
                    print(f"  {row}")
            else:
                print("  (no data)")

    finally:
        con.close()

    print(f"\n{DIVIDER}")
    print("  Done.")
    print(DIVIDER)


def run_checks_():

    con = duckdb.connect(DUCKDB_PATH, read_only=True)

    try:
        df = con.execute(

        """

desc hourly_huawei_3g_packet_loss

        """

    ).fetchdf()
        
        print(df)

    except Exception as e:
        print(e)
    finally :
        con.close()   

    print()

    # cols = [d[0] for d in con.execute(f"SELECT * FROM {tbl} LIMIT 0").description]
    # print(f"  Columns: {cols}")
    # if rows:
    #     for row in rows:
    #         print(f"  {row}")
    # else:
    #         print("  (no data)")

if __name__ == "__main__":
    run_checks_()
