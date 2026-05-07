import sqlite3
from sqlalchemy import create_engine, MetaData

DB_URL = "sqlite:///app.db"
engine = create_engine(DB_URL)
metadata = MetaData()

def get_db():
    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price REAL NOT NULL,
            count INTEGER NOT NULL,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()
