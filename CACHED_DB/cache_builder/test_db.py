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

      
SELECT
    cell_name,
    controller_name,
    site_name,
    arrondissement,
    commune,
    departement,
    longitude,
    latitude,
    azimuth,
    sum_cssr_failure                                                                                        AS CSR_FAILURES,
    ROUND(100 * sum_cssr_failure        / NULLIF(SUM(sum_cssr_failure)        OVER (), 0), 4)               AS Weight_CSR_FAILURES,

    SUM_SDCCH_ASSIGN_FAILS                                                                                  AS SDCCH_ASSIGN_FAILS,
   -- ROUND(100 * SDCCH_ASSIGN_FAILS / CSR_FAILURES, 2) AS 'WEIGHT_SDCCH_ASSIGN_IN_CELL(%)',
    ROUND(100 * SUM_SDCCH_ASSIGN_FAILS  / NULLIF(SUM(SUM_SDCCH_ASSIGN_FAILS)  OVER (), 0), 4)               AS 'GLOBAL_WEIGHT_SDCCH_ASSIGN(%)',

    SUM_SDCCH_DROPS                                                                                         AS SDCCH_DROPS,
   -- ROUND(100 * SDCCH_DROPS / CSR_FAILURES, 2) AS 'WEIGHT_SDCCH_DROPS_IN_CELL(%)',
    ROUND(100 * SUM_SDCCH_DROPS         / NULLIF(SUM(SUM_SDCCH_DROPS)         OVER (), 0), 4)               AS 'GLOBAL_WEIGHT_SDCCH_DROPS(%)',

    SUM_TCH_ASSIGN_FAILS                                                                                    AS TCH_ASSIGN_FAILS,
   -- ROUND(100 * TCH_ASSIGN_FAILS / CSR_FAILURES, 2) AS 'WEIGHT_TCH_ASSIGN_IN_CELL(%)',
    ROUND(100 * SUM_TCH_ASSIGN_FAILS    / NULLIF(SUM(SUM_TCH_ASSIGN_FAILS)    OVER (), 0), 4)               AS 'GLOBAL_WEIGHT_TCH_ASSIGN(%)',

    SUM_TCH_DROPS                                                                                           AS TCH_DROPS,
   -- ROUND(100 * TCH_DROPS / CSR_FAILURES, 2) AS 'WEIGHT_TCH_DROPS_IN_CELL(%)',
    ROUND(100 * SUM_TCH_DROPS           / NULLIF(SUM(SUM_TCH_DROPS)           OVER (), 0), 4)               AS 'GLOBAL_WEIGHT_TCH_DROPS(%)',

    ROUND(CSSR_HUAWEI,                      4)  AS CSSR_HUAWEI,
    ROUND(CDR_HUAWEI,                       4)  AS CDR_HUAWEI,
    ROUND(CBR_HUAWEI,                       4)  AS CBR_HUAWEI,
    ROUND(TCH_CONGESTION_RATE_HUAWEI,       4)  AS TCH_CONGESTION_RATE_HUAWEI,
    ROUND(SDCCH_CONGESTION_RATE_HUAWEI,     4)  AS SDCCH_CONGESTION_RATE_HUAWEI,
    ROUND(SDCCH_DROP_RATE_HUAWEI,           4)  AS SDCCH_DROP_RATE_HUAWEI,
    ROUND(TCH_ASSIGNMENT_SUCCESS_RATE_HUAWEI, 4) AS TCH_ASSIGNMENT_SUCCESS_RATE_HUAWEI,
    ROUND(SDCCH_TRAFFIC_HUAWEI,             4)  AS SDCCH_TRAFFIC_HUAWEI,
    ROUND(CELL_AVAILABILITY_RATE_HUAWEI,    4)  AS CELL_AVAILABILITY_RATE_HUAWEI,
    ROUND(TRAFFIC_VOIX_HUAWEI,              4)  AS TRAFFIC_VOIX_HUAWEI,
    ROUND(HANDOVER_SUCCESS_RATE_HUAWEI,     4)  AS HANDOVER_SUCCESS_RATE_HUAWEI

FROM (

    SELECT
        h.cell_name AS cell_name,
    h.controller_name AS controller_name,
    ept.SITE_NAME AS site_name,
    ept.ARRONDISSEMENT AS arrondissement,
    ept.COMMUNE AS commune,
    ept.DEPARTEMENT AS departement,
    ept.LONGITUDE AS longitude,
    ept.LATITUDE AS latitude,
    ept.AZIMUTH AS azimuth,

SUM((CELL_KPI_SD_REQ - CELL_KPI_SD_SUCC) + CELL_SD_CALL_DROPS +
               (CELL_KPI_TCH_REQ_SIG + CELL_KPI_TCH_ASS_REQ_TRAF + CELL_KPI_TCH_HO_REQ_TRAF) -
               (CELL_KPI_TCH_SUCC_SIG + CELL_KPI_TCH_ASS_SUCC_TRAF + CELL_KPI_TCH_HO_SUCC_TRAF) + (CELL_KPI_TCH_DROPS_SIG+CELL_KPI_TCH_STATIC_DROPS_TRAF+CELL_KPI_TCH_HO_DROPS_TRAF)) sum_cssr_failure ,

 SUM(CELL_KPI_SD_REQ - CELL_KPI_SD_SUCC) SUM_SDCCH_ASSIGN_FAILS ,

 SUM(CELL_SD_CALL_DROPS) SUM_SDCCH_DROPS ,

 SUM((CELL_KPI_TCH_REQ_SIG + CELL_KPI_TCH_ASS_REQ_TRAF + CELL_KPI_TCH_HO_REQ_TRAF) -
               (CELL_KPI_TCH_SUCC_SIG + CELL_KPI_TCH_ASS_SUCC_TRAF + CELL_KPI_TCH_HO_SUCC_TRAF)) SUM_TCH_ASSIGN_FAILS ,

SUM((CELL_KPI_TCH_DROPS_SIG+CELL_KPI_TCH_STATIC_DROPS_TRAF+CELL_KPI_TCH_HO_DROPS_TRAF)) SUM_TCH_DROPS

   ,100 * (SUM(CELL_KPI_SD_SUCC
      ) / SUM(CELL_KPI_SD_REQ)) *
  (1 - (SUM(CELL_SD_CALL_DROPS) / SUM(CELL_KPI_SD_SUCC))) *
  (SUM(CELL_KPI_TCH_SUCC_SIG) + SUM(CELL_KPI_TCH_ASS_SUCC_TRAF) + SUM(CELL_KPI_TCH_HO_SUCC_TRAF)) /
  (SUM(CELL_KPI_TCH_REQ_SIG) + SUM(CELL_KPI_TCH_ASS_REQ_TRAF) + SUM(CELL_KPI_TCH_HO_REQ_TRAF)) *
  (1 - (((sum(CELL_KPI_TCH_DROPS_SIG)+sum(CELL_KPI_TCH_STATIC_DROPS_TRAF)+sum(CELL_KPI_TCH_HO_DROPS_TRAF))) /     
    ((sum(CELL_KPI_TCH_SUCC_SIG)+sum(CELL_KPI_TCH_ASS_SUCC_TRAF)+sum(CELL_KPI_TCH_HO_SUCC_TRAF))))) AS  CSSR_HUAWEI,

      -- ARCEP 2G CALL DROP RATE - HUAWEI
      100.0 * (
        COALESCE(SUM(CAST(CELL_KPI_TCH_DROPS_SIG AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(CELL_TRAF_CH_CALL_DROPS AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_DROPS_TRAF AS DOUBLE)), 0)
      ) / NULLIF(
        COALESCE(SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)), 0),
        0
      ) AS CDR_HUAWEI,

      -- ARCEP 2G CALL BLOCKING RATE - HUAWEI
      100.0 * (
        COALESCE(SUM(CAST(CELL_KPI_TCH_CONG_SIG AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_CONG_TRAF AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_CONGEST_TRAF AS DOUBLE)), 0)
      ) / NULLIF(
        COALESCE(SUM(CAST(CELL_KPI_TCH_REQ_SIG AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0),
        0
      ) AS CBR_HUAWEI,

      -- TCH Congestion Rate - HUAWEI
      100.0 * (
        COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_CONG_TRAF AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_CONGEST_TRAF AS DOUBLE)), 0)
      ) / NULLIF(
        COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0),
        0
      ) AS TCH_CONGESTION_RATE_HUAWEI,

      -- SDCCH Congestion Rate - HUAWEI
      100.0 * COALESCE(SUM(CAST(CELL_KPI_SD_CONGEST AS DOUBLE)), 0) /
        NULLIF(COALESCE(SUM(CAST(CELL_KPI_SD_REQ AS DOUBLE)), 0), 0) AS SDCCH_CONGESTION_RATE_HUAWEI,

      -- SDCCH Drop Rate - HUAWEI
      100.0 * COALESCE(SUM(CAST(CELL_SD_CALL_DROPS AS DOUBLE)), 0) /
        NULLIF(COALESCE(SUM(CAST(CELL_IMM_ASS_SUCC_SD AS DOUBLE)), 0), 0) AS SDCCH_DROP_RATE_HUAWEI,

      -- ARCEP TCH Assignment Success Rate - HUAWEI (Vendor-specific)
      100.0 * (
        COALESCE(SUM(CAST(CELL_KPI_TCH_SUCC_SIG AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_SUCC_TRAF AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_SUCC_TRAF AS DOUBLE)), 0)
      ) / NULLIF(
        COALESCE(SUM(CAST(CELL_KPI_TCH_REQ_SIG AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(CELL_KPI_TCH_ASS_REQ_TRAF AS DOUBLE)), 0)
        + COALESCE(SUM(CAST(CELL_KPI_TCH_HO_REQ_TRAF AS DOUBLE)), 0),
        0
      ) AS TCH_ASSIGNMENT_SUCCESS_RATE_HUAWEI,

      -- SDCCH Traffic (Erlangs) - HUAWEI
      COALESCE(SUM(CAST(CELL_KPI_SD_TRAF_ERL AS DOUBLE)), 0) AS SDCCH_TRAFFIC_HUAWEI,

      -- 2G Availability Rate - HUAWEI
      100.0 * COALESCE(SUM(CAST(CELL_KPI_TCH_AVAIL_NUM AS DOUBLE)), 0) /
        NULLIF(COALESCE(SUM(CAST(CELL_KPI_TCH_CFG_NUM AS DOUBLE)), 0), 0) AS CELL_AVAILABILITY_RATE_HUAWEI,       

        COALESCE(SUM(CAST(CELL_KPI_TCH_TRAF_ERL_TRAF AS DOUBLE)), 0) TRAFFIC_VOIX_HUAWEI,
        -- handover sr
        100.0 * (
  (COALESCE(SUM(CAST(CELL_INTRABSC_OUTCELL_HO_SUCC AS DOUBLE)), 0)
   + COALESCE(SUM(CAST(CELL_INTERBSC_OUTCELL_HO_SUCC AS DOUBLE)), 0))
  / NULLIF(
      COALESCE(SUM(CAST(CELL_INTRABSC_OUTCELL_HO_CMD AS DOUBLE)), 0)
      + COALESCE(SUM(CAST(CELL_INTERBSC_OUTCELL_HO_CMD AS DOUBLE)), 0),
      0
    )
) AS HANDOVER_SUCCESS_RATE_HUAWEI

    FROM hourly_huawei_2g_all_counters h
    LEFT JOIN EPT_2G ept ON h.cell_name = ept.CELL_NAME AND ept.VENDOR = 'HUAWEI'
    WHERE h.date BETWEEN '2026-02-19' AND '2026-02-19'

    GROUP BY h.cell_name, h.controller_name,
         ept.SITE_NAME, ept.ARRONDISSEMENT, ept.COMMUNE,
         ept.DEPARTEMENT, ept.LONGITUDE, ept.LATITUDE, ept.AZIMUTH
) AS T1
ORDER BY CSR_FAILURES DESC


        """

    ).fetchdf()
        
        print(df)
        df.to_csv("excel_output/from_test_db.csv" , index=False)

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
