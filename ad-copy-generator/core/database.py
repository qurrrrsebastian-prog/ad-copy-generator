"""SQLite persistence for AI Ad Copy Generator. Author: Avatar Putra Sigit

Stores generation history with parameterized queries (no string formatting
into SQL). Also exposes a CSV-backed dummy data loader used by analytics and
the empty-state preview.
"""
import os
import sqlite3
from datetime import datetime

import pandas as pd

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_BASE_DIR, "data")
DB_PATH = os.path.join(_DATA_DIR, "history.db")


def _connect() -> sqlite3.Connection:
    os.makedirs(_DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the generations table if it does not exist."""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS generations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                audience TEXT,
                framework TEXT,
                tone TEXT,
                generated_copy TEXT,
                cta TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_generation(session_id: str, data: dict) -> None:
    """Insert one generation record (parameterized)."""
    try:
        with _connect() as conn:
            conn.execute(
                """
                INSERT INTO generations
                    (session_id, product_name, audience, framework, tone, generated_copy, cta, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    data.get("product_name", ""),
                    data.get("audience", ""),
                    data.get("framework", ""),
                    data.get("tone", ""),
                    data.get("generated_copy", ""),
                    data.get("cta", ""),
                    data.get("created_at", datetime.now().isoformat(timespec="seconds")),
                ),
            )
            conn.commit()
    except sqlite3.Error as e:
        # Persistence failure must not crash the UI.
        print(f"[database] save_generation failed: {e}")


def get_history(session_id: str, limit: int = 5) -> list:
    """Return the most recent generations for a session as list of dicts."""
    try:
        with _connect() as conn:
            rows = conn.execute(
                """
                SELECT product_name, audience, framework, tone, generated_copy, cta, created_at
                FROM generations
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (session_id, int(limit)),
            ).fetchall()
            return [dict(r) for r in rows]
    except sqlite3.Error as e:
        print(f"[database] get_history failed: {e}")
        return []


def get_all_history(session_id: str) -> pd.DataFrame:
    """Return all generations for a session as a DataFrame (for the History tab)."""
    try:
        with _connect() as conn:
            df = pd.read_sql_query(
                """
                SELECT product_name, audience, framework, tone, cta, created_at
                FROM generations
                WHERE session_id = ?
                ORDER BY id DESC
                """,
                conn,
                params=(session_id,),
            )
            return df
    except Exception as e:
        print(f"[database] get_all_history failed: {e}")
        return pd.DataFrame(
            columns=["product_name", "audience", "framework", "tone", "cta", "created_at"]
        )


def get_dummy_data(table: str = "ad_copies") -> pd.DataFrame:
    """Load CSV dummy data from data/<table>.csv; seed it if missing."""
    csv_path = os.path.join(_DATA_DIR, f"{table}.csv")
    if not os.path.exists(csv_path):
        try:
            from data.seeder import seed  # local import to avoid cycles
            seed()
        except Exception as e:
            print(f"[database] seeding failed: {e}")
            return pd.DataFrame()
    try:
        return pd.read_csv(csv_path)
    except Exception as e:
        print(f"[database] read csv failed: {e}")
        return pd.DataFrame()
