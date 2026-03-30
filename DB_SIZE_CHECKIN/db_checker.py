import mysql.connector
import sqlite3
import datetime
import os

DB_CONFIG = {
    'host': '10.22.33.116',
    'user': 'remote',
    'password': 'Re8!Qrj]',
    'connect_timeout': 10,
}

DATA_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
SQLITE_DB = os.path.join(DATA_DIR, 'db_sizes.db')

QUERIES = {
    'prismis': """
        SELECT table_name,
               ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb,
               table_rows
        FROM information_schema.tables
        WHERE table_schema = 'prismis'
        ORDER BY size_mb DESC
    """,
    'performanceroute': """
        SELECT table_name,
               ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb,
               table_rows
        FROM information_schema.tables
        WHERE table_schema = 'performanceroute'
        ORDER BY size_mb DESC
    """,
}


def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(SQLITE_DB)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS snapshots (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp  TEXT    NOT NULL,
            db_name    TEXT    NOT NULL,
            table_name TEXT    NOT NULL,
            size_mb    REAL,
            table_rows INTEGER
        )
    ''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_ts  ON snapshots(timestamp)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_tbl ON snapshots(db_name, table_name)')
    conn.commit()
    conn.close()


def run_check():
    init_db()
    timestamp = datetime.datetime.now().isoformat()
    conn_my = mysql.connector.connect(**DB_CONFIG)
    cur     = conn_my.cursor()
    rows_to_insert = []

    for db_name, sql in QUERIES.items():
        cur.execute(sql)
        for table_name, size_mb, table_rows in cur.fetchall():
            rows_to_insert.append((timestamp, db_name, table_name,
                                   float(size_mb or 0), int(table_rows or 0)))

    cur.close()
    conn_my.close()

    conn_sq = sqlite3.connect(SQLITE_DB)
    conn_sq.executemany(
        'INSERT INTO snapshots (timestamp, db_name, table_name, size_mb, table_rows) VALUES (?,?,?,?,?)',
        rows_to_insert
    )
    conn_sq.commit()
    conn_sq.close()

    print(f"[{timestamp[:19]}] Saved {len(rows_to_insert)} rows")
    return timestamp
