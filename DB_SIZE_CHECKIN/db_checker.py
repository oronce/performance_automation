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

DATABASES = ['performanceroute', 'prismis']

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
SQLITE_PATH = os.path.join(DATA_DIR, 'db_sizes.db')


def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS size_snapshots (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp     TEXT    NOT NULL,
            db_name       TEXT    NOT NULL,
            table_name    TEXT    NOT NULL,
            size_mb       REAL,
            size_bytes    INTEGER,
            row_count     INTEGER,
            data_length   INTEGER,
            index_length  INTEGER
        )
    ''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_ts    ON size_snapshots(timestamp)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_table ON size_snapshots(db_name, table_name)')
    conn.commit()
    conn.close()


def fetch_table_sizes():
    placeholders = ', '.join(['%s'] * len(DATABASES))
    query = f"""
        SELECT
            TABLE_SCHEMA  AS db_name,
            TABLE_NAME    AS table_name,
            COALESCE(DATA_LENGTH + INDEX_LENGTH, 0)              AS size_bytes,
            ROUND(COALESCE(DATA_LENGTH + INDEX_LENGTH, 0) / 1024 / 1024, 6) AS size_mb,
            COALESCE(TABLE_ROWS,   0) AS row_count,
            COALESCE(DATA_LENGTH,  0) AS data_length,
            COALESCE(INDEX_LENGTH, 0) AS index_length
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA IN ({placeholders})
        ORDER BY size_bytes DESC
    """
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, DATABASES)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def save_snapshot(data):
    conn = sqlite3.connect(SQLITE_PATH)
    c = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    c.executemany(
        '''INSERT INTO size_snapshots
           (timestamp, db_name, table_name, size_mb, size_bytes, row_count, data_length, index_length)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        [(timestamp,
          r['db_name'], r['table_name'],
          float(r['size_mb']), int(r['size_bytes']),
          int(r['row_count']), int(r['data_length']), int(r['index_length']))
         for r in data]
    )
    conn.commit()
    conn.close()
    return timestamp


def run_check():
    init_db()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now}] Fetching table sizes from MySQL...")
    rows = fetch_table_sizes()
    if rows:
        ts = save_snapshot(rows)
        print(f"[{now}] Saved {len(rows)} rows at {ts}")
    else:
        print(f"[{now}] No rows returned.")
    return rows
