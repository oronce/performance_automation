"""
SQL Generator — fills placeholders in SQL_SCRIPTS templates.

Placeholders used in SQL files:
    {select_fields}  — dimension columns to SELECT (date, time, commune, etc.)
    {where_clause}   — date filter
    {group_by}       — GROUP BY columns matching select_fields

Usage:
    from sql_generator import generate_sql

    sql = generate_sql(
        script="2g_ericsson",
        start_date="2026-02-10",
        end_date="2026-02-20",
        granularity="DAILY",           # DAILY | HOURLY | MONTHLY
        aggregation_level="commune",   # None | "commune" | "arrondissement"
    )
    # Then execute `sql` on your MySQL connection
"""

import os

_SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SQL_SCRIPTS")

# ── Per-script column references ──────────────────────────────────────────────
#
# date_col   : the date column expression in the main table alias
# time_col   : the time column expression (for HOURLY granularity)
# agg_cols   : available aggregation levels and their SQL column reference
#
_SCRIPT_CONFIG = {
    "2g_ericsson": {
        "date_col": "e.DATE",
        "time_col": "e.TIME",
        "agg_cols": {
            "commune":        "ept.COMMUNE",
            "arrondissement": "ept.ARRONDISSEMENT",
        },
    },
    "3g_ericsson_packet_loss": {
        "date_col": "e.DATE",
        "time_col": "e.TIME",
        "agg_cols": {
            "commune":        "ept.COMMUNE",
            "arrondissement": "ept.ARRONDISSEMENT",
        },
    },
    "3g_huawei_packet_loss": {
        "date_col": "h.DATE",
        "time_col": "h.TIME",
        "agg_cols": {
            "commune":        "e.commune",
            "arrondissement": "e.arrondissement",
        },
    },
    "2g_huawei": {
        "date_col": "h.date",
        "time_col": "h.time",
        "agg_cols": {
            "commune":        "ept.COMMUNE",
            "arrondissement": "ept.ARRONDISSEMENT",
        },
    },
}


def generate_sql(
    script: str,
    start_date: str,
    end_date: str,
    granularity: str = "DAILY",
    aggregation_level: str = None,
) -> str:
    """
    Read a SQL template from SQL_SCRIPTS/<script>.sql and fill its placeholders.

    Parameters
    ----------
    script           : template name without extension (e.g. "2g_ericsson")
    start_date       : "YYYY-MM-DD"
    end_date         : "YYYY-MM-DD"
    granularity      : "DAILY" | "HOURLY" | "MONTHLY"
    aggregation_level: None | "commune" | "arrondissement"

    Returns
    -------
    str — ready-to-execute SQL string
    """
    granularity = granularity.upper()
    if aggregation_level:
        aggregation_level = aggregation_level.lower()

    config = _SCRIPT_CONFIG.get(script)
    if config is None:
        raise ValueError(
            f"Unknown script '{script}'. Available: {list(_SCRIPT_CONFIG.keys())}"
        )

    date_col = config["date_col"]
    time_col = config["time_col"]
    agg_cols = config["agg_cols"]

    # ── build select_fields ───────────────────────────────────────────────────
    select_parts = []

    if granularity == "MONTHLY":
        select_parts.append(f"DATE_FORMAT({date_col}, '%Y-%m') AS date")
    else:
        select_parts.append(f"{date_col} AS date")

    if granularity == "HOURLY":
        select_parts.append(f"{time_col} AS time")

    if aggregation_level:
        agg_col = agg_cols.get(aggregation_level)
        if agg_col is None:
            raise ValueError(
                f"Aggregation level '{aggregation_level}' not available for '{script}'. "
                f"Available: {list(agg_cols.keys())}"
            )
        select_parts.append(f"{agg_col} AS {aggregation_level}")

    select_fields = "\n      ".join(f"{p}," if i < len(select_parts) - 1 else p
                                    for i, p in enumerate(select_parts))

    # ── build where_clause ────────────────────────────────────────────────────
    if granularity == "MONTHLY":
        where_clause = (
            f"{date_col} >= '{start_date}' AND {date_col} <= '{end_date}'"
        )
    else:
        where_clause = f"{date_col} BETWEEN '{start_date}' AND '{end_date}'"

    # ── build group_by ────────────────────────────────────────────────────────
    group_parts = []

    if granularity == "MONTHLY":
        group_parts.append(f"DATE_FORMAT({date_col}, '%Y-%m')")
    else:
        group_parts.append(date_col)

    if granularity == "HOURLY":
        group_parts.append(time_col)

    if aggregation_level:
        group_parts.append(agg_cols[aggregation_level])

    group_by = ", ".join(group_parts)

    # ── load template and fill ─────────────────────────────────────────────────
    sql_path = os.path.join(_SCRIPTS_DIR, f"{script}.sql")
    if not os.path.exists(sql_path):
        raise FileNotFoundError(f"SQL template not found: {sql_path}")

    with open(sql_path, "r", encoding="utf-8") as f:
        template = f.read()

    return template.format(
        select_fields=select_fields,
        where_clause=where_clause,
        group_by=group_by,
    )


# ── Quick test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cases = [
        dict(script="2g_ericsson",             start_date="2026-02-10", end_date="2026-02-20",
             granularity="HOURLY",   aggregation_level=None),
        dict(script="2g_ericsson",             start_date="2026-02-10", end_date="2026-02-20",
             granularity="HOURLY",  aggregation_level="commune"),
        dict(script="3g_ericsson_packet_loss", start_date="2026-02-10", end_date="2026-02-20",
             granularity="DAILY",   aggregation_level="arrondissement"),
        dict(script="3g_huawei_packet_loss",   start_date="2026-02-10", end_date="2026-02-20",
             granularity="HOURLY",  aggregation_level="commune"),
    ]

    for c in cases:
        print("=" * 70)
        print(f"  {c['granularity']} | agg={c['aggregation_level']}")
        print("=" * 70)
        sql = generate_sql(**c)
        # Print only first 6 lines + last 4 lines to keep output short
        lines = sql.strip().splitlines()
        preview = lines[:6] + ["      ..."] + lines[-4:]
        print("\n".join(preview))
        print()
