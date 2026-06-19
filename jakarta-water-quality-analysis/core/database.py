"""SQLite persistence: water readings cache + filter history.

Author: Avatar Putra Sigit
"""
from __future__ import annotations

import os
import sqlite3
from datetime import datetime

import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "monitor.db")
DB_PATH = os.path.abspath(DB_PATH)


def _connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    """Create tables if they do not exist."""
    try:
        with _connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS water_readings (
                    id INTEGER PRIMARY KEY,
                    station_name TEXT,
                    location TEXT,
                    pH REAL,
                    turbidity REAL,
                    TDS REAL,
                    temperature REAL,
                    date TEXT,
                    status TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS filters_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    filters TEXT,
                    created_at TEXT
                )
                """
            )
            conn.commit()
    except sqlite3.Error as exc:  # pragma: no cover - defensive
        print(f"[database] init_db error: {exc}")


def save_filter(session_id: str, filters: str) -> None:
    """Persist a filter selection (parameterized to prevent SQL injection)."""
    try:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO filters_history (session_id, filters, created_at) VALUES (?, ?, ?)",
                (session_id, str(filters)[:500], datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )
            conn.commit()
    except sqlite3.Error as exc:  # pragma: no cover - defensive
        print(f"[database] save_filter error: {exc}")


def get_history(session_id: str, limit: int = 5) -> list[dict]:
    """Return the last ``limit`` filter entries for a session."""
    try:
        with _connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT filters, created_at FROM filters_history
                WHERE session_id = ?
                ORDER BY id DESC LIMIT ?
                """,
                (session_id, int(limit)),
            ).fetchall()
            return [dict(r) for r in rows]
    except sqlite3.Error as exc:  # pragma: no cover - defensive
        print(f"[database] get_history error: {exc}")
        return []


def get_dummy_data(table: str = "water_readings") -> pd.DataFrame:
    """Return a small fallback DataFrame when real data is unavailable."""
    if table == "filters_history":
        return pd.DataFrame(columns=["filters", "created_at"])
    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "station_name": ["Sample-01", "Sample-02", "Sample-03"],
            "location": ["Jakarta Pusat", "Jakarta Selatan", "Jakarta Utara"],
            "pH": [7.1, 6.4, 9.2],
            "turbidity": [12.0, 30.0, 60.0],
            "TDS": [320.0, 700.0, 1200.0],
            "temperature": [28.5, 29.1, 30.3],
            "date": ["2026-01-15", "2026-02-20", "2026-03-10"],
            "status": ["Safe", "Alert", "Critical"],
        }
    )
