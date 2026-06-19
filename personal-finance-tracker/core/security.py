"""Security layer for Personal Finance Tracker.

Input sanitization, validation and anti-abuse helpers. All user-facing
strings are Indonesian to match the UI.

Author: Avatar Putra Sigit
"""
from __future__ import annotations

import datetime
import html
import re
import uuid

# ── Constants ────────────────────────────────────────────────────────────────
MAX_NOTE_LEN = 500
MAX_AMOUNT = 999_999_999          # Rp 999.999.999
MAX_DAYS_BACK = 365               # max 1 tahun ke belakang
VALID_CATEGORIES = [
    "Makan", "Transport", "Gaji", "Investasi",
    "Belanja", "Hiburan", "Kesehatan", "Lainnya",
]
VALID_TYPES = ["Pemasukan", "Pengeluaran"]

# Patterns that must never reach the SQL layer (defence-in-depth; the data
# layer already uses parameterized queries).
_SQL_BLOCKLIST = re.compile(
    r"\b(DROP|DELETE|ALTER|TRUNCATE|INSERT|UPDATE|EXEC|UNION)\b",
    re.IGNORECASE,
)
_SCRIPT_TAG = re.compile(r"<\s*script", re.IGNORECASE)
_HTML_TAG = re.compile(r"<[^>]*>")


class ValidationError(Exception):
    """Raised when user input fails validation."""


# ── Sanitization ─────────────────────────────────────────────────────────────
def sanitize_input(text: str | None) -> str:
    """Strip HTML, block <script>, escape entities, trim and clamp to 500 chars.

    Returns a safe plain-text string suitable for storage and for rendering
    via ``st.text`` (never markdown).
    """
    if text is None:
        return ""
    text = str(text).strip()
    if not text:
        return ""
    # Hard block on script tags -> drop content entirely.
    if _SCRIPT_TAG.search(text):
        text = _SCRIPT_TAG.sub("", text)
    # Remove any remaining HTML tags.
    text = _HTML_TAG.sub("", text)
    # Neutralize SQL keywords defensively (queries are parameterized anyway).
    text = _SQL_BLOCKLIST.sub("", text)
    # Escape residual HTML entities so it is inert even if misrendered.
    text = html.escape(text, quote=False)
    return text.strip()[:MAX_NOTE_LEN]


# ── Validation ───────────────────────────────────────────────────────────────
def validate_amount(amount) -> float:
    """Validate a monetary amount.

    Rules: numeric only, > 0, <= Rp 999.999.999, no negatives.
    Returns the amount as ``float``. Raises ``ValidationError`` otherwise.
    """
    try:
        value = float(amount)
    except (TypeError, ValueError):
        raise ValidationError("Jumlah harus berupa angka.")
    if value != value or value in (float("inf"), float("-inf")):  # NaN/inf
        raise ValidationError("Jumlah tidak valid.")
    if value <= 0:
        raise ValidationError("Jumlah harus lebih besar dari 0.")
    if value > MAX_AMOUNT:
        raise ValidationError("Jumlah melebihi batas maksimum (Rp 999.999.999).")
    return value


def validate_date(date) -> datetime.date:
    """Validate a transaction date.

    Rules: must be a real date, not in the future, not more than 1 year back.
    Accepts ``datetime.date``/``datetime.datetime`` or an ISO ``YYYY-MM-DD``
    string. Returns a ``datetime.date``.
    """
    if isinstance(date, datetime.datetime):
        date = date.date()
    elif isinstance(date, str):
        try:
            date = datetime.date.fromisoformat(date.strip())
        except ValueError:
            raise ValidationError("Format tanggal tidak valid (gunakan YYYY-MM-DD).")
    if not isinstance(date, datetime.date):
        raise ValidationError("Tanggal tidak valid.")

    today = datetime.date.today()
    if date > today:
        raise ValidationError("Tanggal tidak boleh di masa depan.")
    if date < today - datetime.timedelta(days=MAX_DAYS_BACK):
        raise ValidationError("Tanggal maksimal 1 tahun ke belakang.")
    return date


def validate_category(category: str) -> str:
    """Ensure category is one of the predefined values."""
    cat = (category or "").strip()
    if cat not in VALID_CATEGORIES:
        raise ValidationError(
            f"Kategori tidak valid. Pilih salah satu: {', '.join(VALID_CATEGORIES)}."
        )
    return cat


def validate_type(t_type: str) -> str:
    """Ensure transaction type is Pemasukan or Pengeluaran."""
    value = (t_type or "").strip()
    if value not in VALID_TYPES:
        raise ValidationError("Tipe transaksi tidak valid.")
    return value


# ── Anti-abuse helpers ───────────────────────────────────────────────────────
def generate_session_id() -> str:
    """Return a short (8-char) session identifier."""
    return uuid.uuid4().hex[:8]


def check_duplicate(amount, date, note: str, minutes: int = 1) -> bool:
    """Return True if an identical transaction was created within ``minutes``.

    Delegates the recency check to the database layer. Imported lazily to
    avoid a circular import at module load time.
    """
    try:
        from core.database import find_recent_duplicate
        return find_recent_duplicate(amount, date, note, minutes=minutes)
    except Exception:
        # Fail open on lookup error -> never block a legitimate save.
        return False
