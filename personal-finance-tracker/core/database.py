"""SQLite persistence layer for Personal Finance Tracker.

All writes use parameterized queries. The legacy Flask schema
``transactions(id, date, category, amount, type, note)`` with English type
values (``income``/``expense``) is migrated in place to the new schema
``transactions(id, type, amount, category, date, note, created_at)`` with
Indonesian type values (``Pemasukan``/``Pengeluaran``).

Author: Avatar Putra Sigit
"""
from __future__ import annotations

import datetime
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "finance.db")
DB_PATH = os.path.abspath(DB_PATH)

# Legacy English -> Indonesian type mapping (one-time migration).
_TYPE_MIGRATION = {"income": "Pemasukan", "expense": "Pengeluaran"}


# ── Connection ───────────────────────────────────────────────────────────────
def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]


# ── Schema / migration ───────────────────────────────────────────────────────
_NEW_SCHEMA = """
    CREATE TABLE {name} (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        type       TEXT NOT NULL,
        amount     REAL NOT NULL,
        category   TEXT NOT NULL,
        date       TEXT NOT NULL,
        note       TEXT DEFAULT '',
        created_at TEXT NOT NULL
    )
"""


def init_db() -> None:
    """Create tables if missing and migrate the legacy schema/data.

    The legacy Flask table carries a ``CHECK(type IN ('income','expense'))``
    constraint that SQLite cannot drop in place, so when a legacy schema is
    detected the table is rebuilt and its rows are copied with type values
    normalized to Indonesian.
    """
    try:
        conn = _connect()
        c = conn.cursor()
        c.execute(_NEW_SCHEMA.format(name="transactions").replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS"))
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
            """
        )
        conn.commit()

        # ── Detect legacy schema (CHECK constraint or missing created_at) ──
        stored = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='transactions'"
        ).fetchone()
        stored_sql = (stored["sql"] if stored else "") or ""
        cols = _columns(conn, "transactions")
        needs_rebuild = ("CHECK" in stored_sql.upper()) or ("created_at" not in cols)

        now = datetime.datetime.now().isoformat(timespec="seconds")
        if needs_rebuild:
            c.execute("DROP TABLE IF EXISTS transactions_new")
            c.execute(_NEW_SCHEMA.format(name="transactions_new"))
            # Copy legacy rows, normalizing type and backfilling created_at.
            has_created = "created_at" in cols
            created_expr = (
                "CASE WHEN created_at IS NULL OR created_at='' THEN ? ELSE created_at END"
                if has_created else "?"
            )
            c.execute(
                f"""
                INSERT INTO transactions_new (type, amount, category, date, note, created_at)
                SELECT
                    CASE type WHEN 'income' THEN 'Pemasukan'
                              WHEN 'expense' THEN 'Pengeluaran'
                              ELSE type END,
                    amount, category, date, COALESCE(note, ''),
                    {created_expr}
                FROM transactions
                """,
                (now,),
            )
            c.execute("DROP TABLE transactions")
            c.execute("ALTER TABLE transactions_new RENAME TO transactions")
            conn.commit()
        else:
            # Already new schema -> just normalize any stray legacy values.
            for old, new in _TYPE_MIGRATION.items():
                c.execute("UPDATE transactions SET type = ? WHERE type = ?", (new, old))
            c.execute(
                "UPDATE transactions SET created_at = ? WHERE created_at IS NULL OR created_at = ''",
                (now,),
            )

        # Seed categories table.
        for name in [
            "Makan", "Transport", "Gaji", "Investasi",
            "Belanja", "Hiburan", "Kesehatan", "Lainnya",
        ]:
            c.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,))

        conn.commit()
        conn.close()
    except Exception as e:  # pragma: no cover - defensive
        print(f"[database] init_db error: {e}")


# ── Writes ───────────────────────────────────────────────────────────────────
def add_transaction(data: dict) -> int | None:
    """Insert a transaction. ``data`` keys: type, amount, category, date, note.

    Returns the new row id, or ``None`` on failure.
    """
    try:
        date = data["date"]
        if isinstance(date, (datetime.date, datetime.datetime)):
            date = date.isoformat()[:10]
        conn = _connect()
        cur = conn.execute(
            """
            INSERT INTO transactions (type, amount, category, date, note, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data["type"],
                float(data["amount"]),
                data["category"],
                str(date),
                data.get("note", ""),
                datetime.datetime.now().isoformat(timespec="seconds"),
            ),
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return new_id
    except Exception as e:
        print(f"[database] add_transaction error: {e}")
        return None


def delete_transaction(tx_id: int) -> bool:
    """Hard-delete a transaction by id (parameterized)."""
    try:
        conn = _connect()
        conn.execute("DELETE FROM transactions WHERE id = ?", (int(tx_id),))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[database] delete_transaction error: {e}")
        return False


# ── Reads ────────────────────────────────────────────────────────────────────
def get_transactions(filters: dict | None = None) -> list[dict]:
    """Return transactions as a list of dicts, newest first.

    Optional ``filters``: ``type``, ``category``, ``date_from``, ``date_to``.
    """
    filters = filters or {}
    clauses: list[str] = []
    params: list = []
    if filters.get("type"):
        clauses.append("type = ?")
        params.append(filters["type"])
    if filters.get("category"):
        clauses.append("category = ?")
        params.append(filters["category"])
    if filters.get("date_from"):
        clauses.append("date >= ?")
        params.append(str(filters["date_from"]))
    if filters.get("date_to"):
        clauses.append("date <= ?")
        params.append(str(filters["date_to"]))
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = f"SELECT * FROM transactions{where} ORDER BY date DESC, id DESC"
    try:
        conn = _connect()
        rows = conn.execute(sql, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[database] get_transactions error: {e}")
        return []


def get_summary(month: int | None = None, year: int | None = None) -> dict:
    """Aggregate income/expense/balance, optionally for a given month/year.

    Returns: income, expense, balance, max_expense, max_category, count.
    """
    clauses: list[str] = []
    params: list = []
    if year:
        clauses.append("strftime('%Y', date) = ?")
        params.append(f"{int(year):04d}")
    if month:
        clauses.append("strftime('%m', date) = ?")
        params.append(f"{int(month):02d}")
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    try:
        conn = _connect()
        income = conn.execute(
            f"SELECT COALESCE(SUM(amount),0) FROM transactions{where}"
            + (" AND" if where else " WHERE") + " type='Pemasukan'",
            params,
        ).fetchone()[0]
        expense = conn.execute(
            f"SELECT COALESCE(SUM(amount),0) FROM transactions{where}"
            + (" AND" if where else " WHERE") + " type='Pengeluaran'",
            params,
        ).fetchone()[0]
        top = conn.execute(
            f"SELECT category, COALESCE(SUM(amount),0) AS total FROM transactions{where}"
            + (" AND" if where else " WHERE")
            + " type='Pengeluaran' GROUP BY category ORDER BY total DESC LIMIT 1",
            params,
        ).fetchone()
        count = conn.execute(
            f"SELECT COUNT(*) FROM transactions{where}", params
        ).fetchone()[0]
        conn.close()
        return {
            "income": float(income or 0),
            "expense": float(expense or 0),
            "balance": float((income or 0) - (expense or 0)),
            "max_expense": float(top["total"]) if top else 0.0,
            "max_category": top["category"] if top else "—",
            "count": int(count or 0),
        }
    except Exception as e:
        print(f"[database] get_summary error: {e}")
        return {
            "income": 0.0, "expense": 0.0, "balance": 0.0,
            "max_expense": 0.0, "max_category": "—", "count": 0,
        }


def get_history(limit: int = 5) -> list[dict]:
    """Return the most recent ``limit`` transactions (by creation time)."""
    try:
        conn = _connect()
        rows = conn.execute(
            "SELECT * FROM transactions ORDER BY created_at DESC, id DESC LIMIT ?",
            (int(limit),),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[database] get_history error: {e}")
        return []


def find_recent_duplicate(amount, date, note: str, minutes: int = 1) -> bool:
    """Return True if a matching transaction was created within ``minutes``.

    Matches on amount + date + note. Used by ``security.check_duplicate``.
    """
    try:
        if isinstance(date, (datetime.date, datetime.datetime)):
            date = date.isoformat()[:10]
        cutoff = (
            datetime.datetime.now() - datetime.timedelta(minutes=minutes)
        ).isoformat(timespec="seconds")
        conn = _connect()
        row = conn.execute(
            """
            SELECT COUNT(*) FROM transactions
            WHERE amount = ? AND date = ? AND note = ? AND created_at >= ?
            """,
            (float(amount), str(date), note or "", cutoff),
        ).fetchone()
        conn.close()
        return (row[0] or 0) > 0
    except Exception as e:
        print(f"[database] find_recent_duplicate error: {e}")
        return False


def count_transactions() -> int:
    """Total number of transactions (used by the seeder / rate limiting)."""
    try:
        conn = _connect()
        n = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        conn.close()
        return int(n or 0)
    except Exception as e:
        print(f"[database] count_transactions error: {e}")
        return 0
