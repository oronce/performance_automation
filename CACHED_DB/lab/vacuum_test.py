"""
lab/vacuum_test.py
──────────────────
Test VACUUM effectiveness:
  1. Create DuckDB table with 20k rows/day × 3 days (60k total)
  2. Reload same date range 5 times (DELETE + INSERT each time)
  3. Print DB size after each reload  →  should grow (dead rows accumulate)
  4. Run VACUUM + CHECKPOINT
  5. Print DB size after VACUUM       →  should shrink back

Run: python vacuum_test.py
"""

import os
import time
import tempfile
import duckdb
import numpy as np
import pandas as pd

# ── paths ──────────────────────────────────────────────────────────────────────
LAB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(LAB_DIR, "vacuum_test.db")

ROWS_PER_DAY = 20_000
DATES        = ["2026-03-01", "2026-03-02", "2026-03-03"]
RELOAD_TIMES = 20          # how many times we reload the same range
RNG          = np.random.default_rng(42)

DIVIDER = "-" * 60


# ── helpers ────────────────────────────────────────────────────────────────────

def db_size_mb() -> float:
    return os.path.getsize(DB_PATH) / 1024 / 1024


def generate_df(seed_offset: int = 0) -> pd.DataFrame:
    """Generate ROWS_PER_DAY × len(DATES) rows of fake KPI data."""
    rng   = np.random.default_rng(42 + seed_offset)
    n     = ROWS_PER_DAY * len(DATES)
    times = [f"{h:02d}:00:00" for h in range(24)]
    dates_col = []
    for d in DATES:
        dates_col.extend([d] * ROWS_PER_DAY)

    return pd.DataFrame({
        "date":  dates_col,
        "time":  rng.choice(times, n),
        "site":  [f"SITE_{i % 100:03d}" for i in range(n)],
        "kpi_1": np.round(rng.uniform(0, 100,   n), 6).astype(str),
        "kpi_2": np.round(rng.uniform(0, 50000, n), 6).astype(str),
        "kpi_3": np.round(rng.uniform(95, 100,  n), 6).astype(str),
    })


def load_data(con, df: pd.DataFrame, reload_num: int):
    """DELETE date range then INSERT from temp CSV (our production technique)."""
    csv_path = None
    try:
        # write temp CSV
        tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w")
        df.to_csv(tmp.name, index=False)
        tmp.close()
        csv_path = tmp.name

        # DELETE existing range
        con.execute(
            "DELETE FROM kpi_lab WHERE date BETWEEN '2026-03-01' AND '2026-03-03'"
        )

        # INSERT from CSV (our production technique)
        con.execute(
            f"INSERT INTO kpi_lab SELECT * FROM read_csv('{csv_path}', all_varchar=true)"
        )

        con.execute("CHECKPOINT")

    finally:
        if csv_path and os.path.exists(csv_path):
            os.unlink(csv_path)


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    # clean slate
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    wal = DB_PATH + ".wal"
    if os.path.exists(wal):
        os.remove(wal)

    con = duckdb.connect(DB_PATH)

    # create table
    con.execute("""
        CREATE TABLE kpi_lab (
            date  VARCHAR,
            time  VARCHAR,
            site  VARCHAR,
            kpi_1 DECIMAL(38,12),
            kpi_2 DECIMAL(38,12),
            kpi_3 DECIMAL(38,12)
        )
    """)

    # initial load
    print(f"\n{DIVIDER}")
    print("  INITIAL LOAD")
    print(DIVIDER)
    df = generate_df(seed_offset=0)
    load_data(con, df, reload_num=0)
    row_count = con.execute("SELECT COUNT(*) FROM kpi_lab").fetchone()[0]
    print(f"  Rows     : {row_count:,}")
    print(f"  DB size  : {db_size_mb():.3f} MB  <- baseline")

    # reload same range multiple times
    print(f"\n{DIVIDER}")
    print(f"  RELOAD × {RELOAD_TIMES}  (DELETE + INSERT each time)")
    print(DIVIDER)

    for i in range(1, RELOAD_TIMES + 1):
        t0 = time.perf_counter()
        df = generate_df(seed_offset=i)
        load_data(con, df, reload_num=i)
        elapsed = time.perf_counter() - t0
        row_count = con.execute("SELECT COUNT(*) FROM kpi_lab").fetchone()[0]
        print(f"  Reload #{i}  rows={row_count:,}  size={db_size_mb():.3f} MB  ({elapsed:.2f}s)")

    size_before = db_size_mb()
    print(f"\n{DIVIDER}")
    print(f"  BEFORE VACUUM : {size_before:.3f} MB")
    print(DIVIDER)

    # VACUUM + CHECKPOINT
    print("  Running VACUUM ...")
    t0 = time.perf_counter()
    con.execute("VACUUM")
    print(f"  VACUUM done    : {time.perf_counter()-t0:.3f}s")

    print("  Running CHECKPOINT ...")
    t0 = time.perf_counter()
    con.execute("CHECKPOINT")
    print(f"  CHECKPOINT done: {time.perf_counter()-t0:.3f}s")

    size_after = db_size_mb()
    saved      = size_before - size_after

    print(f"\n{DIVIDER}")
    print(f"  AFTER  VACUUM : {size_after:.3f} MB")
    print(f"  SAVED         : {saved:.3f} MB  ({saved/size_before*100:.1f}%)")
    print(DIVIDER)

    row_count = con.execute("SELECT COUNT(*) FROM kpi_lab").fetchone()[0]
    print(f"  Final rows    : {row_count:,}  (should be {ROWS_PER_DAY * len(DATES):,})")

    con.close()

    print(f"\n  DB file: {DB_PATH}")
    print(f"  Done.\n")


if __name__ == "__main__":
    main()