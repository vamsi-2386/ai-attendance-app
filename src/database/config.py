import sqlite3
import os

DB_PATH = os.environ.get('DATABASE_PATH', os.path.join(os.path.dirname(__file__), 'app.db'))

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn