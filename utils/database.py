import sqlite3
from pathlib import Path

DB_FILE = Path("data/app.db")

def get_connection():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_FILE)

def init_database():
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                datetime TEXT NOT NULL,
                file_name TEXT NOT NULL,
                sessions_count INTEGER NOT NULL,
                anomalies_count INTEGER NOT NULL
            )
        """)

        connection.commit()