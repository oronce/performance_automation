import mysql.connector
import pandas as pd
import os

# ── Config ────────────────────────────────────────────────────
MYSQL_CONFIG = {
    "host":     "10.22.33.116",
    "port":     3306,
    "user":     "root",
    "password": "performance",
    "database": "performanceroute",
}

DATE_START  = "2026-03-02"
DATE_END    = "2026-03-08"
OUTPUT_FILE = f"excel_output/availability_2g_huawei_{DATE_START}_{DATE_END}.xlsx"
MANUAL_FILE = "excel_output/huawei_availability.xlsx"

# ── Query 1: bad sites (CELL_SERV_OOS > 1800, no OM outage) ──
SQL_BAD = """
SELECT date, TIME, ept.SITE_NAME, avg(downtime_sec) avg_down_per_site
FROM (
    SELECT
        h.date,
        h.time,
        h.cell_name,
        sum(CELL_SERV_OOS) AS downtime_sec
    FROM hourly_huawei_2g_all_counters h
    WHERE h.date BETWEEN %s AND %s
    GROUP BY h.date, h.time, h.CELL_NAME
    HAVING sum(CELL_SERV_OOS) > 1800
       AND sum(`CELL_SERV_OOS_OM`) = 0
) t1
LEFT JOIN EPT_2G ept ON t1.CELL_NAME = ept.CELL_NAME AND ept.VENDOR = 'HUAWEI'
GROUP BY date, TIME, ept.SITE_NAME
"""

# ── Query 2: good candidates (CELL_SERV_OOS <= 1800, no OM outage)
SQL_GOOD = """
SELECT date, TIME, ept.SITE_NAME, avg(downtime_sec) avg_down_per_site
FROM (
    SELECT
        h.date,
        h.time,
        h.cell_name,
        sum(CELL_SERV_OOS) AS downtime_sec
    FROM hourly_huawei_2g_all_counters h
    WHERE h.date BETWEEN %s AND %s
    GROUP BY h.date, h.time, h.CELL_NAME
    HAVING sum(CELL_SERV_OOS) <= 1800
       AND sum(`CELL_SERV_OOS_OM`) = 0
) t1
LEFT JOIN EPT_2G ept ON t1.CELL_NAME = ept.CELL_NAME AND ept.VENDOR = 'HUAWEI'
GROUP BY date, TIME, ept.SITE_NAME
"""

# ── helper ────────────────────────────────────────────────────
def fmt_time(t):
    if hasattr(t, 'seconds'):
        h, rem = divmod(t.seconds, 3600)
        m, s   = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    return str(t)


def build_pivot(df_all):
    df_all['slot'] = pd.to_datetime(df_all['date']).dt.strftime('%d-%m-%Y') \
                     + ' ' + df_all['time'].astype(str)

    pivot = df_all.pivot_table(
        index='site_name',
        columns='slot',
        values='avg_down_per_site',
        aggfunc='mean'
    ).round(1)

    pivot = pivot[sorted(pivot.columns, key=lambda s: pd.to_datetime(s, dayfirst=True))]
    pivot.columns.name = f"Period: {DATE_START} to {DATE_END}"
    pivot.index.name   = 'SITE_NAME'
    return pivot


def compare(pivot, manual_path):
    try:
        manual = pd.read_excel(manual_path, index_col=0)
        manual.index = manual.index.astype(str).str.strip()
        manual.index.name = 'SITE_NAME'

        print(f"\n--- Comparison with {manual_path} ---")
        print(f"  Manual : {manual.shape[0]} sites x {manual.shape[1]} slots")
        print(f"  Ours   : {pivot.shape[0]} sites x {pivot.shape[1]} slots")

        manual_sites = set(manual.index.dropna())
        our_sites    = set(pivot.index.dropna())
        only_manual  = manual_sites - our_sites
        only_ours    = our_sites - manual_sites
        common       = manual_sites & our_sites
        print(f"  Common sites   : {len(common)}")
        print(f"  Only in manual : {len(only_manual)}  -> {sorted(only_manual)[:10]}")
        print(f"  Only in ours   : {len(only_ours)}  -> {sorted(only_ours)[:10]}")

        if common:
            # align and compare values
            shared_cols = [c for c in manual.columns.astype(str) if c in pivot.columns.astype(str)]
            m = manual.reindex(index=sorted(common))[shared_cols].fillna(0)
            o = pivot.reindex(index=sorted(common))[shared_cols].fillna(0)
            diff = (m - o).abs()
            print(f"\n  Value check (common sites x common slots):")
            print(f"    Max diff  : {diff.values.max():.4f}")
            print(f"    Mean diff : {diff.values.mean():.6f}")
            print(f"    Cells > 0.1 diff : {(diff > 0.1).values.sum()}")

    except FileNotFoundError:
        print(f"\n  (Manual file not found: {manual_path})")


def main():
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    try:
        print("Running Huawei query 1 (bad sites > 1800s, no OM) ...")
        df_bad = pd.read_sql(SQL_BAD, conn, params=(DATE_START, DATE_END))

        print("Running Huawei query 2 (good candidates <= 1800s, no OM) ...")
        df_good = pd.read_sql(SQL_GOOD, conn, params=(DATE_START, DATE_END))
    finally:
        conn.close()

    for df in (df_bad, df_good):
        df.columns = df.columns.str.lower()
        df['time'] = df['time'].apply(fmt_time)

    bad_sites = set(df_bad['site_name'].dropna().unique())
    print(f"  Bad sites  (> 1800s): {len(bad_sites)}")

    df_good_filtered = df_good[
        df_good['site_name'].notna() &
        (~df_good['site_name'].isin(bad_sites))
    ].copy()
    print(f"  Good sites after exclusion: {df_good_filtered['site_name'].nunique()}")

    df_bad_clean = df_bad[df_bad['site_name'].notna()].copy()
    df_all       = pd.concat([df_bad_clean, df_good_filtered], ignore_index=True)
    print(f"  Total sites in pivot : {df_all['site_name'].nunique()}")

    if df_all.empty:
        print("No data to pivot. Exiting.")
        return

    pivot = build_pivot(df_all)
    print(f"\nPivot  ->  {pivot.shape[0]} sites  x  {pivot.shape[1]} time slots")

    os.makedirs("excel_output", exist_ok=True)
    pivot.to_excel(OUTPUT_FILE, sheet_name='Availability_2G_Huawei', engine='openpyxl')
    print(f"\nSaved -> {OUTPUT_FILE}")

    compare(pivot, MANUAL_FILE)


if __name__ == "__main__":
    main()