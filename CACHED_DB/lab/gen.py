"""
lab/gen.py
──────────
Generate 2 million rows of fake telecom KPI data → data.csv

Schema mirrors a real varchar_to_decimal hourly table:
  id       INTEGER  (primary key)
  date     DATE
  time     TIME
  site_id  VARCHAR
  cell_id  VARCHAR
  kpi_1..7 DECIMAL strings  ← VARCHAR in MySQL → object dtype in pandas
"""

import os
import time
import numpy as np
import pandas as pd

N        = 2_000_000
OUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.csv")
RNG      = np.random.default_rng(42)

print(f"Generating {N:,} rows...")
t0 = time.perf_counter()

dates    = pd.date_range("2025-01-01", periods=90).strftime("%Y-%m-%d").tolist()
times    = [f"{h:02d}:00:00" for h in range(24)]
site_ids = [f"SITE_{i:03d}" for i in range(1, 101)]
cell_ids = [f"CELL_{i:04d}" for i in range(1, 301)]

df = pd.DataFrame({
    "id":      np.arange(1, N + 1),
    "date":    RNG.choice(dates,    N),
    "time":    RNG.choice(times,    N),
    "site_id": RNG.choice(site_ids, N),
    "cell_id": RNG.choice(cell_ids, N),
    # KPI columns as decimal strings — simulates MySQL VARCHAR → pandas object dtype
    "kpi_1":   np.round(RNG.uniform(0,     100,   N), 6).astype(str),
    "kpi_2":   np.round(RNG.uniform(0,   50000,   N), 6).astype(str),
    "kpi_3":   np.round(RNG.uniform(95,    100,   N), 6).astype(str),
    "kpi_4":   np.round(RNG.uniform(0,    1000,   N), 6).astype(str),
    "kpi_5":   np.round(RNG.uniform(0,     200,   N), 6).astype(str),
    "kpi_6":   np.round(RNG.uniform(0,     500,   N), 6).astype(str),
    "kpi_7":   np.round(RNG.uniform(0,     100,   N), 6).astype(str),
})

df.to_csv(OUT_FILE, index=False)

elapsed = time.perf_counter() - t0
size_mb = __import__("os").path.getsize(OUT_FILE) / 1024 / 1024
print(f"Done in {elapsed:.2f}s")
print(f"File  : {OUT_FILE}  ({size_mb:.1f} MB)")
print(f"Shape : {df.shape}")
print(f"Cols  : {list(df.columns)}")