"""SQLite database helper for finance tracker. Author: Avatar Putra Sigit"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "finance.db")

def init_db() -> None:
    """Initialize SQLite database with transactions table."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                note TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error initializing database: {e}")

def add_transaction(date: str, category: str, amount: float, t_type: str, note: str = "") -> bool:
    """Add a transaction to database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO transactions (date, category, amount, type, note) VALUES (?, ?, ?, ?, ?)",
                  (date, category, amount, t_type, note))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding transaction: {e}")
        return False

def get_all_transactions() -> list:
    """Get all transactions ordered by date desc."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM transactions ORDER BY date DESC")
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return []

def get_summary() -> dict:
    """Get financial summary."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type='income'")
        income = c.fetchone()[0]
        c.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type='expense'")
        expense = c.fetchone()[0]
        conn.close()
        return {"income": income, "expense": expense, "balance": income - expense}
    except Exception as e:
        print(f"Error getting summary: {e}")
        return {"income": 0, "expense": 0, "balance": 0}
