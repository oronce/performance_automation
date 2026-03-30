import os
_HERE    = os.path.dirname(os.path.abspath(__file__))
_ENV     = os.path.join(_HERE, "..", ".env")

# load .env manually (no dependency on python-dotenv)
if os.path.exists(_ENV):
    with open(_ENV, encoding="utf-8") as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

# ─────────────────────────────────────────────────────────────
#  MySQL source database connection
# ─────────────────────────────────────────────────────────────
MYSQL_CONFIG = {
    "host":     "10.22.33.116",
    "port":     3306,
    "user":     "remote",
    "password": "Re8!Qrj]",
    "database": "performanceroute",
}

# ─────────────────────────────────────────────────────────────
#  DuckDB cache file path
# ─────────────────────────────────────────────────────────────
DUCKDB_PATH   = os.environ.get("DUCKDB_PATH", os.path.join(_HERE, "assets", "cache.db"))

# ─────────────────────────────────────────────────────────────
#  SQL output file — Step 1 writes here, Step 2 reads from here
#  Edit this file between steps if you need to adjust any type
# ─────────────────────────────────────────────────────────────
SQL_FILE_PATH = os.path.join(_HERE, "assets", "create_tables.sql")

# ─────────────────────────────────────────────────────────────
#  Batch size for fetching rows from MySQL
# ─────────────────────────────────────────────────────────────
FETCH_BATCH_SIZE = 50_000
LOAD_BATCH_DAYS  = 2       # days per batch when loading a multi-day range

# ─────────────────────────────────────────────────────────────
#  Table list
#
#  mysql_table        : table name in MySQL (same name used in DuckDB)
#  varchar_to_decimal : True  → every VARCHAR/CHAR col becomes DECIMAL(55, 12)
#                       False → VARCHAR stays VARCHAR
#  auto_detect        : True  → skip type mapping, DuckDB infers types from data
#                       False → use explicit MySQL → DuckDB type mapping
#  date_col           : name of the date column (default: "date")
#                       set to None if the table has no date column
#  cleanup            : True  → remove rows older than 30 days (requires date_col)
#                       False → never cleanup this table
#  time_cols          : list of column names that are MySQL TIME (returned as timedelta)
#                       those will be converted to datetime.time before insert
#                       omit or set to [] if the table has no TIME columns
# ─────────────────────────────────────────────────────────────
_HOURLY = {"varchar_to_decimal": True, "auto_detect": False, "date_col": "date", "cleanup": True, "time_cols": ["time"]}
_HOURLY_WITH_TIME_UPPERCASE = {"varchar_to_decimal": True, "auto_detect": False, "date_col": "date", "cleanup": True, "time_cols": ["TIME"]}
_EPT    = {"varchar_to_decimal": True, "auto_detect": True , "cleanup": True}

TABLES = [
   ## #── Huawei hourly ─────────────────────────────────────────
    {"mysql_table": "hourly_huawei_2g_all_counters",              **_HOURLY},
    {"mysql_table": "hourly_huawei_3g_all_counters_1",            **_HOURLY},
    {"mysql_table": "hourly_huawei_3g_all_counters_2",            **_HOURLY},
    {"mysql_table": "hourly_huawei_3g_packet_loss",               **_HOURLY},
    {"mysql_table": "hourly_huawei_4g_all_counters_1",            **_HOURLY},
    #{"mysql_table": "hourly_huawei_4g_all_counters_2",            **_HOURLY},
    {"mysql_table": "hourly_huawei_4g_packet_loss",               **_HOURLY},
    ## ── Huawei ARCEP hourly ───────────────────────────────────
    # {"mysql_table": "hourly_arcep_huawei_2g",                     **_HOURLY},
    # {"mysql_table": "hourly_arcep_huawei_3g",                     **_HOURLY},
    # {"mysql_table": "hourly_arcep_huawei_4g",                     **_HOURLY},
   ## #── Ericsson ARCEP hourly ─────────────────────────────────
    {"mysql_table": "hourly_ericsson_arcep_2g_counters",          **_HOURLY_WITH_TIME_UPPERCASE},
    {"mysql_table": "hourly_ericsson_arcep_3g_counters",          **_HOURLY_WITH_TIME_UPPERCASE},
    {"mysql_table": "hourly_ericsson_arcep_4g_counters",          **_HOURLY_WITH_TIME_UPPERCASE},
    ##### ── Ericsson packet loss hourly ───────────────────────────
    {"mysql_table": "hourly_ericsson_packet_loss_bb_3g_counters", **_HOURLY_WITH_TIME_UPPERCASE},
    {"mysql_table": "hourly_ericsson_packet_loss_bb_4g_counters", **_HOURLY_WITH_TIME_UPPERCASE},
    {"mysql_table": "hourly_ericsson_packet_loss_du_3g_counters", **_HOURLY_WITH_TIME_UPPERCASE},
    {"mysql_table": "hourly_ericsson_packet_loss_du_4g_counters", **_HOURLY_WITH_TIME_UPPERCASE},

    #### ── huawei packet loss hourly ───────────────────────────
    {"mysql_table": "hourly_huawei_4g_packet_loss", **_HOURLY},
    {"mysql_table": "hourly_huawei_3g_packet_loss", **_HOURLY},
    {"mysql_table": "huawei_adjacent_node_id_3g", **_EPT},


   #### # ── EPT ───────────────────────────────────────────────────
    {"mysql_table": "ept_2g",                                     **_EPT},
    {"mysql_table": "ept_3g",                                     **_EPT},
   {"mysql_table": "ept_4g",                                     **_EPT},
    ####── example: table with no date column, no cleanup needed ─
    ############{"mysql_table": "ref_sites", "varchar_to_decimal": False, "auto_detect": False, "date_col": None, "cleanup": False},
]
