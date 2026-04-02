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

DATE_START  = "2026-03-23"
DATE_END    = "2026-03-29"
OUTPUT_FILE = f"excel_output/availability_2g_{DATE_START}_{DATE_END}.xlsx"

# ── Ericsson queries ───────────────────────────────────────────
ERICSSON_BAD = """
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

ERICSSON_GOOD = """
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

# ── Huawei queries ─────────────────────────────────────────────
HUAWEI_BAD = """
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

HUAWEI_GOOD = """
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

# ── helpers ────────────────────────────────────────────────────
def fmt_time(t):
    if hasattr(t, 'seconds'):
        h, rem = divmod(t.seconds, 3600)
        m, s   = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    return str(t)


def fetch_vendor(conn, sql_bad, sql_good, vendor_label):
    df_bad  = pd.read_sql(sql_bad,  conn, params=(DATE_START, DATE_END))
    df_good = pd.read_sql(sql_good, conn, params=(DATE_START, DATE_END))

    for df in (df_bad, df_good):
        df.columns = df.columns.str.lower()
        df['time'] = df['time'].apply(fmt_time)

    bad_sites = set(df_bad['site_name'].dropna().unique())

    df_good_filtered = df_good[
        df_good['site_name'].notna() &
        (~df_good['site_name'].isin(bad_sites))
    ].copy()

    df_all = pd.concat(
        [df_bad[df_bad['site_name'].notna()], df_good_filtered],
        ignore_index=True
    )
    df_all['vendor'] = vendor_label
    print(f"  {vendor_label}: {len(bad_sites)} bad + "
          f"{df_good_filtered['site_name'].nunique()} good = "
          f"{df_all['site_name'].nunique()} total sites")
    return df_all


def build_pivot(df, index_cols):
    df['slot'] = pd.to_datetime(df['date']).dt.strftime('%d-%m-%Y') \
                 + ' ' + df['time'].astype(str)

    pivot = df.pivot_table(
        index=index_cols,
        columns='slot',
        values='avg_down_per_site',
        aggfunc='mean'
    ).round(1)

    pivot = pivot[sorted(pivot.columns, key=lambda s: pd.to_datetime(s, dayfirst=True))]
    pivot.columns.name = f"Period: {DATE_START} to {DATE_END}"
    return pivot


def main():
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    try:
        print("Fetching Ericsson data ...")
        df_ericsson = fetch_vendor(conn, ERICSSON_BAD, ERICSSON_GOOD, 'ERICSSON')

        print("Fetching Huawei data ...")
        df_huawei   = fetch_vendor(conn, HUAWEI_BAD,   HUAWEI_GOOD,   'HUAWEI')
    finally:
        conn.close()

    # ── per-vendor pivots (index = site_name only) ─────────────
    pivot_ericsson = build_pivot(df_ericsson, index_cols='site_name')
    pivot_ericsson.index.name = 'SITE_NAME'

    pivot_huawei   = build_pivot(df_huawei,   index_cols='site_name')
    pivot_huawei.index.name = 'SITE_NAME'

    # ── combined pivot (index = [vendor, site_name]) ───────────
    df_combined       = pd.concat([df_ericsson, df_huawei], ignore_index=True)
    pivot_combined    = build_pivot(df_combined, index_cols=['vendor', 'site_name'])
    pivot_combined.index.names = ['VENDOR', 'SITE_NAME']

    print(f"\nEricsson pivot : {pivot_ericsson.shape[0]} sites x {pivot_ericsson.shape[1]} slots")
    print(f"Huawei pivot   : {pivot_huawei.shape[0]} sites x {pivot_huawei.shape[1]} slots")
    print(f"Combined pivot : {pivot_combined.shape[0]} rows x {pivot_combined.shape[1]} slots")

    # ── export ─────────────────────────────────────────────────
    os.makedirs("excel_output", exist_ok=True)
    with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
        pivot_ericsson.to_excel(writer, sheet_name='Ericsson')
        pivot_huawei.to_excel(writer,   sheet_name='Huawei')
        pivot_combined.to_excel(writer, sheet_name='All_Vendors')

    print(f"\nSaved -> {OUTPUT_FILE}")
    print("  Sheets: Ericsson | Huawei | All_Vendors")


if __name__ == "__main__":
    main()