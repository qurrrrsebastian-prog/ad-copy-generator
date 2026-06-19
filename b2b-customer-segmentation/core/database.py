"""SQLite persistence for segmentation runs and history.

Uses parameterized queries everywhere to avoid SQL injection. The DB lives
next to the app under data/segmentation.db.
"""
import json
import os
import sqlite3
from datetime import datetime

import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "segmentation.db")


def _connect() -> sqlite3.Connection:
    """Open a connection with row access by column name."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables: clients, segments, filter_history (idempotent)."""
    try:
        with _connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY,
                    company_name TEXT,
                    industry TEXT,
                    revenue REAL,
                    employees INTEGER,
                    contract_value REAL,
                    engagement_score REAL,
                    last_purchase INTEGER,
                    churn_risk TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS segments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    segment TEXT,
                    count INTEGER,
                    created_at TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS filter_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    filter_summary TEXT,
                    segment_counts TEXT,
                    created_at TEXT
                )
                """
            )
            conn.commit()
    except sqlite3.Error as e:
        # DB is non-critical (history only); never crash the app over it.
        print(f"[database] init_db error: {e}")


def save_segmentation(session_id: str, filters: str, segment_counts: dict) -> bool:
    """Persist one segmentation run (filter summary + per-segment counts)."""
    try:
        created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        counts = dict(segment_counts or {})
        with _connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO filter_history (session_id, filter_summary, segment_counts, created_at)"
                " VALUES (?, ?, ?, ?)",
                (str(session_id), str(filters)[:500], json.dumps(counts), created),
            )
            for seg, cnt in counts.items():
                cur.execute(
                    "INSERT INTO segments (session_id, segment, count, created_at)"
                    " VALUES (?, ?, ?, ?)",
                    (str(session_id), str(seg), int(cnt), created),
                )
            conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[database] save_segmentation error: {e}")
        return False


def get_history(session_id: str, limit: int = 5) -> list:
    """Return the last `limit` runs for a session as list of dicts."""
    try:
        with _connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT filter_summary, segment_counts, created_at FROM filter_history"
                " WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (str(session_id), int(limit)),
            )
            return [dict(row) for row in cur.fetchall()]
    except sqlite3.Error as e:
        print(f"[database] get_history error: {e}")
        return []


def get_dummy_data(table: str = "clients") -> pd.DataFrame:
    """Return a table as a DataFrame (whitelisted table names only)."""
    allowed = {"clients", "segments", "filter_history"}
    if table not in allowed:
        return pd.DataFrame()
    try:
        with _connect() as conn:
            return pd.read_sql_query(f"SELECT * FROM {table}", conn)
    except Exception as e:  # pandas/sqlite errors
        print(f"[database] get_dummy_data error: {e}")
        return pd.DataFrame()
