"""
lab/bench.py
────────────
Benchmark different strategies for refreshing a date range in DuckDB.

Setup
-----
  Table : kpi_lab  — 2M rows, schema mirrors a varchar_to_decimal hourly table
                     DECIMAL(38,12) KPI columns, INTEGER primary key
  Refresh range : REFRESH_START → REFRESH_END  (~200k rows)

Methods tested
--------------
  A — Baseline  : pandas DataFrame (object dtype) + register + DELETE + INSERT
  B — Numeric   : pandas DataFrame + pd.to_numeric + DELETE + INSERT
  C — CSV+DEL   : DELETE range  +  INSERT INTO ... SELECT * FROM read_csv(...)
  D — Swap      : CREATE TABLE _new AS (kept rows UNION ALL read_csv)  →  DROP + RENAME
  E — OR REPLACE: INSERT OR REPLACE INTO ... SELECT * FROM read_csv(...)  (no DELETE)

Run
---
  cd lab
  python gen.py        # only once — creates data.csv
  python bench.py
"""

import os
import time
import tempfile
import contextlib

import duckdb
import pandas as pd
import numpy as np

# ── Config ────────────────────────────────────────────────────────────────────

_HERE         = os.path.dirname(os.path.abspath(__file__))
LAB_DB        = os.path.join(_HERE, "lab.db")
DATA_CSV      = os.path.join(_HERE, "data.csv")
TABLE         = "kpi_lab"
REFRESH_START = "2025-03-01"
REFRESH_END   = "2025-03-20"   # ~20 days → roughly 440k rows out of 2M

KPI_COLS = [f"kpi_{i}" for i in range(1, 8)]

# Mirrors the real varchar_to_decimal schema  (DECIMAL(38,12) is the slow part)
DDL = f"""
CREATE TABLE {TABLE} (
    id      INTEGER PRIMARY KEY,
    date    DATE,
    time    TIME,
    site_id VARCHAR,
    cell_id VARCHAR,
    kpi_1   DECIMAL(38,12),
    kpi_2   DECIMAL(38,12),
    kpi_3   DECIMAL(38,12),
    kpi_4   DECIMAL(38,12),
    kpi_5   DECIMAL(38,12),
    kpi_6   DECIMAL(38,12),
    kpi_7   DECIMAL(38,12)
)
"""

# ── Helpers ───────────────────────────────────────────────────────────────────

@contextlib.contextmanager
def step(label: str):
    """Print elapsed time for a labelled step."""
    t0 = time.perf_counter()
    yield
    print(f"      {label:<42} {time.perf_counter() - t0:>7.3f} s")


def connect():
    return duckdb.connect(LAB_DB)


def reset_table():
    """
    Drop and recreate the table, then bulk-load all 2M rows from CSV
    using read_csv (fastest known path — used as neutral baseline reset).
    """
    print("  [reset] rebuilding table from data.csv ...")
    t0 = time.perf_counter()
    con = connect()
    con.execute(f"DROP TABLE IF EXISTS {TABLE}")
    con.execute(DDL)
    con.execute(f"INSERT INTO {TABLE} SELECT * FROM read_csv_auto('{DATA_CSV}')")
    rows = con.execute(f"SELECT COUNT(*) FROM {TABLE}").fetchone()[0]
    con.close()
    print(f"  [reset] {rows:,} rows  in  {time.perf_counter()-t0:.3f}s\n")
    return rows


def make_refresh_df():
    """
    Return a pandas DataFrame (object dtype) for the refresh range.
    Simulates what pd.read_sql() returns from MySQL for varchar_to_decimal tables.
    """
    con = connect()
    df  = con.execute(
        f"SELECT * FROM {TABLE} WHERE date BETWEEN ? AND ?",
        [REFRESH_START, REFRESH_END],
    ).df()
    con.close()
    # Force KPI columns back to object (string) — as MySQL connector would return them
    for col in KPI_COLS:
        df[col] = df[col].astype(str)
    return df


def make_refresh_csv(df: pd.DataFrame) -> str:
    """Write the refresh DataFrame to a temp CSV, return the file path."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w")
    df.to_csv(tmp.name, index=False)
    tmp.close()
    return tmp.name


def verify(con, expected_total: int, method: str):
    count = con.execute(f"SELECT COUNT(*) FROM {TABLE}").fetchone()[0]
    ok    = "✓" if count == expected_total else f"✗ expected {expected_total:,}"
    print(f"      row count after: {count:,}  {ok}")


# ── Methods ───────────────────────────────────────────────────────────────────

def method_a(df_obj: pd.DataFrame, total_rows: int):
    """
    A — Baseline (current duck_manager.py approach)
    pandas DataFrame object dtype → register → DELETE + INSERT INTO
    """
    print("  METHOD A — pandas object + register + DELETE + INSERT")
    con = connect()
    t_total = time.perf_counter()

    with step("DELETE range"):
        con.execute(
            f"DELETE FROM {TABLE} WHERE date BETWEEN ? AND ?",
            [REFRESH_START, REFRESH_END],
        )
    with step("register DataFrame (object dtype)"):
        con.register("_tmp", df_obj)
    with step("INSERT INTO ... SELECT * FROM _tmp"):
        con.execute(f"INSERT INTO {TABLE} SELECT * FROM _tmp")
        con.unregister("_tmp")

    print(f"      {'TOTAL':<42} {time.perf_counter()-t_total:>7.3f} s")
    verify(con, total_rows, "A")
    con.close()


def method_b(df_obj: pd.DataFrame, total_rows: int):
    """
    B — pd.to_numeric conversion before insert
    pandas object → pd.to_numeric → register → DELETE + INSERT INTO
    """
    print("  METHOD B — pd.to_numeric + register + DELETE + INSERT")
    con = connect()
    t_total = time.perf_counter()

    with step("pd.to_numeric on KPI cols"):
        df_num = df_obj.copy()
        for col in KPI_COLS:
            df_num[col] = pd.to_numeric(df_num[col], errors="coerce")

    with step("DELETE range"):
        con.execute(
            f"DELETE FROM {TABLE} WHERE date BETWEEN ? AND ?",
            [REFRESH_START, REFRESH_END],
        )
    with step("register DataFrame (float64 dtype)"):
        con.register("_tmp", df_num)
    with step("INSERT INTO ... SELECT * FROM _tmp"):
        con.execute(f"INSERT INTO {TABLE} SELECT * FROM _tmp")
        con.unregister("_tmp")

    print(f"      {'TOTAL':<42} {time.perf_counter()-t_total:>7.3f} s")
    verify(con, total_rows, "B")
    con.close()


def method_c(csv_path: str, total_rows: int):
    """
    C — DELETE + read_csv INSERT
    DELETE range  →  INSERT INTO ... SELECT * FROM read_csv(csv)
    No pandas involved in the insert path.
    """
    print("  METHOD C — DELETE + INSERT from read_csv")
    con = connect()
    t_total = time.perf_counter()

    with step("DELETE range"):
        con.execute(
            f"DELETE FROM {TABLE} WHERE date BETWEEN ? AND ?",
            [REFRESH_START, REFRESH_END],
        )
    with step("INSERT INTO ... SELECT * FROM read_csv"):
        con.execute(f"INSERT INTO {TABLE} SELECT * FROM read_csv_auto('{csv_path}')")

    print(f"      {'TOTAL':<42} {time.perf_counter()-t_total:>7.3f} s")
    verify(con, total_rows, "C")
    con.close()


def method_d(csv_path: str, total_rows: int):
    """
    D — Table swap
    CREATE _new AS (kept rows UNION ALL read_csv)  →  DROP + RENAME
    No DELETE, produces a clean compacted table with no dead rows.
    """
    print("  METHOD D — Table swap (CREATE AS + DROP + RENAME)")
    con = connect()
    t_total = time.perf_counter()

    with step("CREATE _new_kpi_lab AS kept + read_csv"):
        con.execute(f"""
            CREATE TABLE _new_{TABLE} AS
                SELECT * FROM {TABLE}
                WHERE date NOT BETWEEN '{REFRESH_START}' AND '{REFRESH_END}'
                UNION ALL
                SELECT * FROM read_csv_auto('{csv_path}')
        """)
    with step("DROP + RENAME (atomic swap)"):
        con.execute("BEGIN")
        con.execute(f"DROP TABLE {TABLE}")
        con.execute(f"ALTER TABLE _new_{TABLE} RENAME TO {TABLE}")
        con.execute("COMMIT")

    print(f"      {'TOTAL':<42} {time.perf_counter()-t_total:>7.3f} s")
    verify(con, total_rows, "D")
    con.close()


def method_e(csv_path: str, total_rows: int):
    """
    E — INSERT OR REPLACE from read_csv
    Uses the primary key — no explicit DELETE needed.
    DuckDB resolves conflicts row by row via PK lookup.
    """
    print("  METHOD E — INSERT OR REPLACE from read_csv (no DELETE)")
    con = connect()
    t_total = time.perf_counter()

    with step("INSERT OR REPLACE ... SELECT * FROM read_csv"):
        con.execute(
            f"INSERT OR REPLACE INTO {TABLE} SELECT * FROM read_csv_auto('{csv_path}')"
        )

    print(f"      {'TOTAL':<42} {time.perf_counter()-t_total:>7.3f} s")
    verify(con, total_rows, "E")
    con.close()


def method_f(csv_path: str, total_rows: int):
    """
    F — DELETE + read_csv with all_varchar=true
    Same as C but forces all columns to be read as strings so DuckDB
    casts string→DECIMAL directly — no float64 intermediate, full precision.
    """
    print("  METHOD F — DELETE + INSERT from read_csv (all_varchar=true)")
    con = connect()
    t_total = time.perf_counter()

    with step("DELETE range"):
        con.execute(
            f"DELETE FROM {TABLE} WHERE date BETWEEN ? AND ?",
            [REFRESH_START, REFRESH_END],
        )
    with step("INSERT INTO ... read_csv all_varchar=true"):
        con.execute(f"INSERT INTO {TABLE} SELECT * FROM read_csv('{csv_path}', all_varchar=true)")

    print(f"      {'TOTAL':<42} {time.perf_counter()-t_total:>7.3f} s")
    verify(con, total_rows, "F")
    con.close()


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not os.path.exists(DATA_CSV):
        print(f"ERROR: {DATA_CSV} not found — run gen.py first")
        raise SystemExit(1)

    print("=" * 60)
    print("  DuckDB load strategy benchmark")
    print(f"  Refresh range : {REFRESH_START} → {REFRESH_END}")
    print("=" * 60 + "\n")

    # ── Initial setup ─────────────────────────────────────────
    total_rows = reset_table()

    # ── Prepare inputs (shared across methods) ─────────────────
    print("  Preparing refresh inputs...")
    df_obj   = make_refresh_df()
    csv_path = make_refresh_csv(df_obj)
    refresh_rows = len(df_obj)
    csv_mb   = os.path.getsize(csv_path) / 1024 / 1024
    print(f"  Refresh rows  : {refresh_rows:,}")
    print(f"  Temp CSV size : {csv_mb:.1f} MB\n")

    results = {}

    # ── Run each method (reset table between each) ─────────────

    reset_table()
    t = time.perf_counter()
    method_a(df_obj, total_rows)
    results["A  pandas object + register + DELETE + INSERT"] = time.perf_counter() - t
    print()

    reset_table()
    t = time.perf_counter()
    method_b(df_obj, total_rows)
    results["B  pd.to_numeric + register + DELETE + INSERT"] = time.perf_counter() - t
    print()

    reset_table()
    t = time.perf_counter()
    method_c(csv_path, total_rows)
    results["C  DELETE + INSERT from read_csv             "] = time.perf_counter() - t
    print()

    reset_table()
    t = time.perf_counter()
    method_d(csv_path, total_rows)
    results["D  Table swap (CREATE AS + DROP + RENAME)    "] = time.perf_counter() - t
    print()

    reset_table()
    t = time.perf_counter()
    method_e(csv_path, total_rows)
    results["E  INSERT OR REPLACE from read_csv           "] = time.perf_counter() - t
    print()

    reset_table()
    t = time.perf_counter()
    method_f(csv_path, total_rows)
    results["F  DELETE + read_csv (all_varchar, precision) "] = time.perf_counter() - t
    print()

    # ── Summary ───────────────────────────────────────────────
    os.unlink(csv_path)

    print("=" * 60)
    print("  RESULTS SUMMARY")
    print("=" * 60)
    best = min(results.values())
    for label, elapsed in results.items():
        bar    = "█" * int(elapsed / best * 20)
        marker = " ← fastest" if elapsed == best else ""
        print(f"  {label}  {elapsed:6.2f}s  {bar}{marker}")
    print("=" * 60)