"""
schema_inspector.py
───────────────────
Connects to MySQL, runs DESC on each table, and generates
the DuckDB CREATE TABLE SQL based on per-table parameters.
"""

import re
import mysql.connector
from config import MYSQL_CONFIG


# ─────────────────────────────────────────────────────────────
#  MySQL type name → DuckDB type name
#
#  MySQL and DuckDB don't share the same type names.
#  This map translates each MySQL base type to its DuckDB equivalent.
#  Examples:
#    MySQL "mediumint"  → DuckDB doesn't have it   → INTEGER
#    MySQL "datetime"   → DuckDB doesn't have it   → TIMESTAMP
#    MySQL "longtext"   → DuckDB doesn't have it   → VARCHAR
#    MySQL "double"     → same concept, same name  → DOUBLE
# ─────────────────────────────────────────────────────────────
_TYPE_MAP = {
    "tinyint":    "TINYINT",
    "smallint":   "SMALLINT",
    "mediumint":  "INTEGER",
    "int":        "INTEGER",
    "bigint":     "BIGINT",
    "float":      "FLOAT",
    "double":     "DOUBLE",
    "real":       "DOUBLE",
    "date":       "DATE",
    "datetime":   "TIMESTAMP",
    "timestamp":  "TIMESTAMP",
    "time":       "TIME",
    "year":       "INTEGER",
    "text":       "VARCHAR",
    "tinytext":   "VARCHAR",
    "mediumtext": "VARCHAR",
    "longtext":   "VARCHAR",
    "blob":       "BLOB",
    "tinyblob":   "BLOB",
    "mediumblob": "BLOB",
    "longblob":   "BLOB",
    "bit":        "BIT",
    "boolean":    "BOOLEAN",
    "bool":       "BOOLEAN",
    "json":       "VARCHAR",
    "enum":       "VARCHAR",
    "set":        "VARCHAR",
}


def _mysql_type_to_duckdb(raw_mysql_type: str, varchar_to_decimal: bool) -> str:
    """
    Convert a raw MySQL type string (e.g. 'varchar(40)', 'int(11) unsigned')
    to the appropriate DuckDB type string.
    """
    t = raw_mysql_type.lower().strip()
    t = re.sub(r"\s*(unsigned|zerofill)\s*", "", t).strip()

    match = re.match(r"([a-z]+)\s*(?:\(([^)]+)\))?", t)
    if not match:
        return "VARCHAR"

    base = match.group(1)
    args = match.group(2)  # e.g. "40" or "10,2" or None

    if base in ("varchar", "char"):
        if varchar_to_decimal and args and args.strip() == "40":
            return "DECIMAL(38, 12)"
        return "VARCHAR"

    if base in ("decimal", "numeric"):
        if args:
            parts = [p.strip() for p in args.split(",")]
            return f"DECIMAL({parts[0]}, {parts[1]})" if len(parts) == 2 else f"DECIMAL({parts[0]}, 0)"
        return "DECIMAL(18, 4)"

    return _TYPE_MAP.get(base, "VARCHAR")


def _get_mysql_desc(table_name: str) -> list:
    """
    Run DESC <table_name> on MySQL and return raw rows.
    Each row: (Field, Type, Null, Key, Default, Extra)
    """
    conn   = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    cursor.execute(f"DESC `{table_name}`")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def generate_create_sql(table_config: dict) -> str:
    """
    Connect to MySQL, describe the table, return the DuckDB CREATE TABLE SQL.
    Table name in DuckDB is the same as in MySQL.

    auto_detect=True  → all columns VARCHAR, DuckDB infers real types on data load
    auto_detect=False → explicit MySQL → DuckDB type mapping via _TYPE_MAP

    Primary keys are read from the DESC Key column:
      - single PK   → PRIMARY KEY inline on the column
      - composite PK → PRIMARY KEY (col1, col2, ...) constraint at the end
    """
    table_name         = table_config["mysql_table"]
    varchar_to_decimal = table_config.get("varchar_to_decimal", False)
    auto_detect        = table_config.get("auto_detect", False)

    desc_rows = _get_mysql_desc(table_name)

    # collect primary key columns in order
    pk_cols = [field for field, _, _, key, _, _ in desc_rows if key == "PRI"]

    col_lines = []
    for field, mysql_type, nullable, key, default, extra in desc_rows:
        duck_type    = "VARCHAR" if auto_detect else _mysql_type_to_duckdb(mysql_type, varchar_to_decimal)
        nullable_str = "NULL" if nullable == "YES" else "NOT NULL"

        # inline PRIMARY KEY only when there is a single PK column
        pk_inline = " PRIMARY KEY" if (key == "PRI" and len(pk_cols) == 1) else ""

        col_lines.append(f"    {field:<40} {duck_type}  {nullable_str}{pk_inline}")

    # composite PK → add as a trailing constraint
    if len(pk_cols) > 1:
        pk_str = ", ".join(pk_cols)
        col_lines.append(f"    PRIMARY KEY ({pk_str})")

    columns_block = ",\n".join(col_lines)
    mode_comment  = (
        "-- auto_detect=True  : all VARCHAR, real types inferred on load"
        if auto_detect else
        f"-- auto_detect=False | varchar_to_decimal={varchar_to_decimal}"
    )

    return (
        f"-- MySQL table : {table_name}\n"
        f"{mode_comment}\n"
        f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        f"{columns_block}\n"
        f");"
    )


def generate_all(tables: list) -> dict:
    """
    Generate CREATE TABLE SQL for every table in the list.
    Returns { table_name: sql_string }
    """
    results = {}
    for cfg in tables:
        name = cfg["mysql_table"]
        print(f"  Inspecting MySQL table: {name} ...", end=" ", flush=True)
        try:
            results[name] = generate_create_sql(cfg)
            print("OK")
        except Exception as e:
            print(f"FAILED -> {e}")
            results[name] = None
    return results
