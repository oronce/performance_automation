"""
Worst-Cell SQL Generator — fills placeholders in worst-cell SQL templates.

Placeholders used in SQL files:
    {outer_select_geo}  — geo columns in the outer SELECT (with trailing commas)
    {select_geo}        — geo columns in the inner SELECT (with trailing commas)
    {join_ept}          — LEFT JOIN EPT_2G clause or empty string
    {start_date}        — date range start  "YYYY-MM-DD"
    {end_date}          — date range end    "YYYY-MM-DD"
    {time_filter}       — optional AND time BETWEEN clause or empty string
    {group_by}          — GROUP BY clause or empty string
    {order_by}          — ORDER BY clause or empty string

Usage:
    from sql.worst_cell_generator import generate_worst_cell_sql

    sql = generate_worst_cell_sql(
        script="2g_ericsson_worst_cell",
        start_date="2026-03-10",
        end_date="2026-03-17",
        aggregation_level="cell_name",   # None | cell_name | site_name | commune |
                                         # arrondissement | departement | controller_name
        time_start="08:00",              # optional
        time_end="20:00",                # optional
    )
"""

import os

# SQL files live in the same directory as this module (sql/)
_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

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

    Parameters
    ----------
    script           : "2g_huawei_worst_cell" | "2g_ericsson_worst_cell"
    start_date       : "YYYY-MM-DD"
    end_date         : "YYYY-MM-DD"
    aggregation_level: None | cell_name | site_name | commune |
                       arrondissement | departement | controller_name
    time_start       : optional "HH:MM"
    time_end         : optional "HH:MM"

    Returns
    -------
    str — ready-to-execute SQL string
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

    # ── EPT join — only when geo aggregation needs it ─────────────────────────
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
