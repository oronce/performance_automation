import mysql.connector
import pandas as pd

# ── Config ────────────────────────────────────────────────────
MYSQL_CONFIG = {
    "host":     "10.22.33.116",
    "port":     3306,
    "user":     "root",
    "password": "performance",
    "database": "performanceroute",
}

DATE_START  = "2026-02-23"
DATE_END    = "2026-03-01"
OUTPUT_FILE = f"excel_output/availability_2g_{DATE_START}_{DATE_END}.xlsx"

# ── Query 1: sites with avg downtime > 1800 (bad sites) ───────
SQL_BAD = """
SELECT date, time, ept.SITE_NAME, avg(downtime_sec) avg_down_per_site
FROM (
    SELECT
        e.DATE,
        e.TIME,
        e.CELL_NAME,
        CASE
            WHEN SUM(CAST(TDWNSCAN AS DOUBLE)) < 8642
             THEN SUM(CAST(TDWNACC AS DOUBLE)) * 10
             ELSE SUM(CAST(TDWNACC AS DOUBLE)) * 86400.0 / SUM(CAST(TDWNSCAN AS DOUBLE))
        END AS downtime_sec
    FROM hourly_ericsson_arcep_2g_counters e
    WHERE e.DATE BETWEEN %s AND %s
    GROUP BY e.DATE, e.TIME, e.CELL_NAME
    HAVING CASE
        WHEN SUM(CAST(TDWNSCAN AS DOUBLE)) < 8642
         THEN SUM(CAST(TDWNACC AS DOUBLE)) * 10
         ELSE SUM(CAST(TDWNACC AS DOUBLE)) * 86400.0 / SUM(CAST(TDWNSCAN AS DOUBLE))
    END > 1800
) t1
LEFT JOIN EPT_2G ept ON t1.CELL_NAME = ept.CELL_NAME AND ept.VENDOR = 'ERICSSON'
GROUP BY date, time, ept.SITE_NAME
"""

# ── Query 2: sites with avg downtime <= 1800 (good candidates)
SQL_GOOD = """
SELECT date, time, ept.SITE_NAME, avg(downtime_sec) avg_down_per_site
FROM (
    SELECT
        e.DATE,
        e.TIME,
        e.CELL_NAME,
        CASE
            WHEN SUM(CAST(TDWNSCAN AS DOUBLE)) < 8642
             THEN SUM(CAST(TDWNACC AS DOUBLE)) * 10
             ELSE SUM(CAST(TDWNACC AS DOUBLE)) * 86400.0 / SUM(CAST(TDWNSCAN AS DOUBLE))
        END AS downtime_sec
    FROM hourly_ericsson_arcep_2g_counters e
    WHERE e.DATE BETWEEN %s AND %s
    GROUP BY e.DATE, e.TIME, e.CELL_NAME
    HAVING CASE
        WHEN SUM(CAST(TDWNSCAN AS DOUBLE)) < 8642
         THEN SUM(CAST(TDWNACC AS DOUBLE)) * 10
         ELSE SUM(CAST(TDWNACC AS DOUBLE)) * 86400.0 / SUM(CAST(TDWNSCAN AS DOUBLE))
    END <= 1800
) t1
LEFT JOIN EPT_2G ept ON t1.CELL_NAME = ept.CELL_NAME AND ept.VENDOR = 'ERICSSON'
GROUP BY date, time, ept.SITE_NAME
"""

# ── helper ────────────────────────────────────────────────────
def fmt_time(t):
    if hasattr(t, 'seconds'):
        h, rem = divmod(t.seconds, 3600)
        m, s   = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    return str(t)


def main():
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    try:
        print("Running query 1 (bad sites > 1800s) …")
        df_bad = pd.read_sql(SQL_BAD, conn, params=(DATE_START, DATE_END))

        print("Running query 2 (good candidates <= 1800s) …")
        df_good = pd.read_sql(SQL_GOOD, conn, params=(DATE_START, DATE_END))
    finally:
        conn.close()

    # fix TIME columns
    for df in (df_bad, df_good):
        df['time'] = df['time'].apply(fmt_time)

    # ── extract bad site names from query 1 ───────────────────
    bad_sites = set(df_bad['SITE_NAME'].dropna().unique())
    print(f"  Bad sites  (> 1800s): {len(bad_sites)}")

    # ── remove bad sites from query 2 results (pandas) ────────
    df_good_filtered = df_good[
        df_good['SITE_NAME'].notna() &
        (~df_good['SITE_NAME'].isin(bad_sites))
    ].copy()
    print(f"  Good sites after exclusion: {df_good_filtered['SITE_NAME'].nunique()}")

    # ── combine ALL sites (bad + good) for the pivot ──────────
    df_bad_clean  = df_bad[df_bad['SITE_NAME'].notna()].copy()
    df_all        = pd.concat([df_bad_clean, df_good_filtered], ignore_index=True)
    print(f"  Total sites in pivot : {df_all['SITE_NAME'].nunique()}")

    if df_all.empty:
        print("No data to pivot. Exiting.")
        return

    # ── date format: DD-MM-YYYY HH:MM:SS  (matches manual file) ─
    df_all['slot'] = pd.to_datetime(df_all['date']).dt.strftime('%d-%m-%Y') \
                     + ' ' + df_all['time'].astype(str)

    pivot = df_all.pivot_table(
        index='SITE_NAME',
        columns='slot',
        values='avg_down_per_site',
        aggfunc='mean'
    ).round(1)

    # sort columns chronologically
    pivot = pivot[sorted(pivot.columns, key=lambda s: pd.to_datetime(s, dayfirst=True))]

    period = f"Period: {DATE_START} to {DATE_END}"
    pivot.columns.name = period
    pivot.index.name   = 'SITE_NAME'

    print(f"\nPivot  ->  {pivot.shape[0]} sites  x  {pivot.shape[1]} time slots")

    # ── export ────────────────────────────────────────────────
    import os
    os.makedirs("excel_output", exist_ok=True)
    pivot.to_excel(OUTPUT_FILE, sheet_name='Availability_2G', engine='openpyxl')
    print(f"\nSaved -> {OUTPUT_FILE}")

    # ── compare with manual file ───────────────────────────────
    MANUAL = "excel_output/availability_study_10_10.xlsx"
    try:
        manual = pd.read_excel(MANUAL, index_col=0)
        manual.index.name = 'SITE_NAME'
        print(f"\n--- Comparison with {MANUAL} ---")
        print(f"  Manual : {manual.shape[0]} sites x {manual.shape[1]} slots")
        print(f"  Ours   : {pivot.shape[0]} sites x {pivot.shape[1]} slots")

        manual_sites = set(manual.index.dropna())
        our_sites    = set(pivot.index.dropna())
        only_manual  = manual_sites - our_sites
        only_ours    = our_sites - manual_sites
        common       = manual_sites & our_sites
        print(f"  Common sites     : {len(common)}")
        print(f"  Only in manual   : {len(only_manual)}  -> {sorted(only_manual)[:10]}")
        print(f"  Only in ours     : {len(only_ours)}   -> {sorted(only_ours)[:10]}")
    except FileNotFoundError:
        print(f"\n  (Manual file not found for comparison: {MANUAL})")


if __name__ == "__main__":
    main()