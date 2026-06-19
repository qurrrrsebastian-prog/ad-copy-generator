"""Dummy data seeder for Personal Finance Tracker.

Generates 100 reproducible transactions (seed=42) over the last 90 days,
using Indonesian type values and the predefined category list.

Run standalone:  python -m data.seeder
Or import:       from data.seeder import seed_transactions

Author: Avatar Putra Sigit
"""
from __future__ import annotations

import datetime
import os
import random
import sqlite3

SEED = 42
N_TRANSACTIONS = 100
DAYS_BACK = 90

CATEGORIES = [
    "Makan", "Transport", "Gaji", "Investasi",
    "Belanja", "Hiburan", "Kesehatan", "Lainnya",
]
INCOME_CATEGORIES = {"Gaji", "Investasi"}

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "finance.db"))

_NOTES = {
    "Makan": ["Makan siang", "Kopi pagi", "Makan malam", "Jajan"],
    "Transport": ["Bensin", "Ojek online", "Parkir", "Tol"],
    "Gaji": ["Gaji bulanan", "Bonus", "THR"],
    "Investasi": ["Dividen", "Reksadana", "Saham"],
    "Belanja": ["Belanja bulanan", "Pakaian", "Elektronik"],
    "Hiburan": ["Nonton bioskop", "Langganan streaming", "Konser"],
    "Kesehatan": ["Apotek", "Periksa dokter", "Vitamin"],
    "Lainnya": ["Donasi", "Hadiah", "Lain-lain"],
}


def _make_rows(rng: random.Random) -> list[tuple]:
    today = datetime.date.today()
    rows: list[tuple] = []
    for _ in range(N_TRANSACTIONS):
        category = rng.choice(CATEGORIES)
        if category in INCOME_CATEGORIES:
            t_type = "Pemasukan"
            amount = rng.randint(50, 500) * 10_000          # 500k - 5jt
        else:
            t_type = "Pengeluaran"
            amount = rng.randint(1, 500) * 10_000            # 10k - 5jt
        amount = min(amount, 5_000_000)
        amount = max(amount, 10_000)
        day_offset = rng.randint(0, DAYS_BACK)
        date = (today - datetime.timedelta(days=day_offset)).isoformat()
        note = rng.choice(_NOTES[category])
        created = (
            datetime.datetime.now() - datetime.timedelta(days=day_offset)
        ).isoformat(timespec="seconds")
        rows.append((t_type, float(amount), category, date, note, created))
    return rows


def seed_transactions(force: bool = False) -> int:
    """Insert dummy transactions. Skips if data already exists unless ``force``.

    Returns the number of rows inserted.
    """
    rng = random.Random(SEED)
    rows = _make_rows(rng)
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                type       TEXT NOT NULL,
                amount     REAL NOT NULL,
                category   TEXT NOT NULL,
                date       TEXT NOT NULL,
                note       TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
            """
        )
        existing = c.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        if existing and not force:
            conn.close()
            print(f"[seeder] {existing} transactions already present; skipping.")
            return 0
        c.executemany(
            """
            INSERT INTO transactions (type, amount, category, date, note, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()
        inserted = c.rowcount
        conn.close()
        print(f"[seeder] inserted {inserted} transactions.")
        return inserted
    except Exception as e:  # pragma: no cover - defensive
        print(f"[seeder] error: {e}")
        return 0


if __name__ == "__main__":
    seed_transactions(force=True)
