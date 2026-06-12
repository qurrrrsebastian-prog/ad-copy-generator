"""Personal Finance Tracker — Flask + SQLite. Author: Avatar Putra Sigit"""
from flask import Flask, render_template, request, redirect, url_for
from database import init_db, add_transaction, get_all_transactions, get_summary
import datetime

app = Flask(__name__)

@app.route("/")
def index() -> str:
    """Dashboard with transaction list and summary."""
    try:
        init_db()
        transactions = get_all_transactions()
        summary = get_summary()
        categories = ["Gaji", "Makan", "Transport", "Utilitas", "Entertainment", "Kesehatan", "Lainnya"]
        return render_template("index.html", transactions=transactions, summary=summary,
                               categories=categories, now=datetime.date.today())
    except Exception as e:
        return f"Error loading dashboard: {e}", 500

@app.route("/add", methods=["POST"])
def add():
    """Add new transaction."""
    try:
        date = request.form.get("date", "")
        category = request.form.get("category", "Lainnya")
        amount = float(request.form.get("amount", 0))
        t_type = request.form.get("type", "expense")
        note = request.form.get("note", "")
        add_transaction(date, category, amount, t_type, note)
    except (ValueError, TypeError) as e:
        print(f"Invalid form input: {e}")
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
