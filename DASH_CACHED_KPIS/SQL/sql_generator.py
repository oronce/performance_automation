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


# =============================================================================
# WORST CELL / SITE / GEO QUERY GENERATOR
# =============================================================================

_WORST_CELL_SCRIPT_CONFIG = {
    "2g_huawei_worst_cell": {
        "main_alias":     "h",
        "cell_col":       "h.cell_name",
        "controller_col": "h.controller_name",
        "vendor":         "HUAWEI",
    },
    "2g_ericsson_worst_cell": {
        "main_alias":     "e",
        "cell_col":       "e.CELL_NAME",
        "controller_col": "e.controller_name",
        "vendor":         "ERICSSON",
    },
}

_VALID_WORST_CELL_LEVELS = (
    None, "cell_name", "site_name", "commune",
    "arrondissement", "departement", "controller_name",
)


def generate_worst_cell_sql(
    script: str,
    start_date: str,
    end_date: str,
    aggregation_level: str = None,
    time_start: str = None,
    time_end: str = None,
) -> str:
    """
    Fill placeholders in a worst-cell SQL template.

    Placeholders used in the SQL files:
        {outer_select_geo}  — geo columns in the outer SELECT  (with trailing commas)
        {select_geo}        — geo columns in the inner SELECT  (with trailing commas)
        {join_ept}          — LEFT JOIN EPT_2G or empty
        {start_date}        — date range start
        {end_date}          — date range end
        {time_filter}       — optional AND time BETWEEN clause
        {group_by}          — GROUP BY clause or empty
        {order_by}          — ORDER BY clause or empty

    Parameters
    ----------
    script           : "2g_huawei_worst_cell" | "2g_ericsson_worst_cell"
    start_date       : "YYYY-MM-DD"
    end_date         : "YYYY-MM-DD"
    aggregation_level: None | cell_name | site_name | commune |
                       arrondissement | departement | controller_name
    time_start       : optional "HH:MM"
    time_end         : optional "HH:MM"
    """
    cfg = _WORST_CELL_SCRIPT_CONFIG.get(script)
    if cfg is None:
        raise ValueError(
            f"Unknown script '{script}'. "
            f"Available: {list(_WORST_CELL_SCRIPT_CONFIG.keys())}"
        )
    if aggregation_level not in _VALID_WORST_CELL_LEVELS:
        raise ValueError(
            f"Unknown aggregation_level '{aggregation_level}'. "
            f"Available: {list(_VALID_WORST_CELL_LEVELS)}"
        )

    a        = cfg["main_alias"]
    cell_col = cfg["cell_col"]
    ctrl_col = cfg["controller_col"]
    vendor   = cfg["vendor"]

    # ── EPT join — only when geo aggregation is needed ────────────────────────
    needs_ept = aggregation_level not in (None, "controller_name")
    join_ept  = (
        f"LEFT JOIN EPT_2G ept ON {cell_col} = ept.CELL_NAME AND ept.VENDOR = '{vendor}'"
        if needs_ept else ""
    )

    # ── Geo SELECT blocks + GROUP BY ──────────────────────────────────────────
    if aggregation_level is None:
        select_geo       = ""
        outer_select_geo = ""
        group_by         = ""
        order_by         = ""

    elif aggregation_level == "cell_name":
        select_geo = (
            f"    {cell_col} AS cell_name,\n"
            f"    {ctrl_col} AS controller_name,\n"
            f"    ept.SITE_NAME AS site_name,\n"
            f"    ept.ARRONDISSEMENT AS arrondissement,\n"
            f"    ept.COMMUNE AS commune,\n"
            f"    ept.DEPARTEMENT AS departement,\n"
            f"    ept.LONGITUDE AS longitude,\n"
            f"    ept.LATITUDE AS latitude,\n"
        )
        outer_select_geo = (
            "    cell_name,\n"
            "    controller_name,\n"
            "    site_name,\n"
            "    arrondissement,\n"
            "    commune,\n"
            "    departement,\n"
            "    longitude,\n"
            "    latitude,\n"
        )
        group_by = (
            f"GROUP BY {cell_col}, {ctrl_col},\n"
            f"         ept.SITE_NAME, ept.ARRONDISSEMENT, ept.COMMUNE,\n"
            f"         ept.DEPARTEMENT, ept.LONGITUDE, ept.LATITUDE"
        )
        order_by = "ORDER BY CSR_FAILURES DESC"

    elif aggregation_level == "site_name":
        select_geo = (
            f"    ept.SITE_NAME AS site_name,\n"
            f"    {ctrl_col} AS controller_name,\n"
            f"    ept.ARRONDISSEMENT AS arrondissement,\n"
            f"    ept.COMMUNE AS commune,\n"
            f"    ept.DEPARTEMENT AS departement,\n"
            f"    MIN(ept.LONGITUDE) AS longitude,\n"
            f"    MIN(ept.LATITUDE) AS latitude,\n"
        )
        outer_select_geo = (
            "    site_name,\n"
            "    controller_name,\n"
            "    arrondissement,\n"
            "    commune,\n"
            "    departement,\n"
            "    longitude,\n"
            "    latitude,\n"
        )
        group_by = (
            f"GROUP BY ept.SITE_NAME, {ctrl_col},\n"
            f"         ept.ARRONDISSEMENT, ept.COMMUNE, ept.DEPARTEMENT"
        )
        order_by = "ORDER BY CSR_FAILURES DESC"

    elif aggregation_level == "commune":
        select_geo = (
            "    ept.COMMUNE AS commune,\n"
            "    ept.ARRONDISSEMENT AS arrondissement,\n"
            "    ept.DEPARTEMENT AS departement,\n"
        )
        outer_select_geo = (
            "    commune,\n"
            "    arrondissement,\n"
            "    departement,\n"
        )
        group_by = "GROUP BY ept.COMMUNE, ept.ARRONDISSEMENT, ept.DEPARTEMENT"
        order_by = "ORDER BY CSR_FAILURES DESC"

    elif aggregation_level == "arrondissement":
        select_geo = (
            "    ept.ARRONDISSEMENT AS arrondissement,\n"
            "    ept.DEPARTEMENT AS departement,\n"
        )
        outer_select_geo = (
            "    arrondissement,\n"
            "    departement,\n"
        )
        group_by = "GROUP BY ept.ARRONDISSEMENT, ept.DEPARTEMENT"
        order_by = "ORDER BY CSR_FAILURES DESC"

    elif aggregation_level == "departement":
        select_geo       = "    ept.DEPARTEMENT AS departement,\n"
        outer_select_geo = "    departement,\n"
        group_by         = "GROUP BY ept.DEPARTEMENT"
        order_by         = "ORDER BY CSR_FAILURES DESC"

    elif aggregation_level == "controller_name":
        select_geo       = f"    {ctrl_col} AS controller_name,\n"
        outer_select_geo = "    controller_name,\n"
        group_by         = f"GROUP BY {ctrl_col}"
        order_by         = "ORDER BY CSR_FAILURES DESC"

    # ── Optional time filter ──────────────────────────────────────────────────
    if time_start and time_end:
        time_filter = f"AND {a}.time BETWEEN '{time_start}' AND '{time_end}'"
    elif time_start:
        time_filter = f"AND {a}.time = '{time_start}'"
    else:
        time_filter = ""

    # ── Load template and fill ────────────────────────────────────────────────
    sql_path = os.path.join(_SCRIPTS_DIR, f"{script}.sql")
    if not os.path.exists(sql_path):
        raise FileNotFoundError(f"SQL template not found: {sql_path}")

    with open(sql_path, "r", encoding="utf-8") as f:
        template = f.read()

    return template.format(
        outer_select_geo = outer_select_geo,
        select_geo       = select_geo,
        join_ept         = join_ept,
        start_date       = start_date,
        end_date         = end_date,
        time_filter      = time_filter,
        group_by         = group_by,
        order_by         = order_by,
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
