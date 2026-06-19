"""Security helpers: input sanitization & validation for the water quality monitor.

Author: Avatar Putra Sigit
"""
from __future__ import annotations

import html
import re
import uuid

# Predefined whitelist of valid Jakarta-area locations.
VALID_LOCATIONS = [
    "Jakarta Selatan",
    "Jakarta Utara",
    "Jakarta Timur",
    "Jakarta Barat",
    "Jakarta Pusat",
    "Bekasi",
    "Tangerang",
    "Depok",
    "Bogor",
]

VALID_STATUSES = ["Safe", "Alert", "Critical"]

# Allowed numeric ranges per parameter (inclusive).
NUMERIC_RANGES = {
    "pH": (0.0, 14.0),
    "turbidity": (0.0, 200.0),
    "TDS": (0.0, 2000.0),
    "temperature": (0.0, 50.0),
}

_HTML_TAG_RE = re.compile(r"<[^>]*>")


def sanitize_input(text: str) -> str:
    """Strip HTML tags/entities and clamp length to 500 chars (XSS prevention)."""
    if text is None:
        return ""
    text = str(text)
    # Remove any HTML tags then escape residual special characters.
    text = _HTML_TAG_RE.sub("", text)
    text = html.escape(text, quote=True)
    return text[:500].strip()


def validate_numeric(param: str, value) -> bool:
    """Return True if ``value`` is within the allowed range for ``param``."""
    if param not in NUMERIC_RANGES:
        return False
    try:
        value = float(value)
    except (TypeError, ValueError):
        return False
    low, high = NUMERIC_RANGES[param]
    return low <= value <= high


def validate_location(loc) -> bool:
    """Return True if ``loc`` (str or iterable of str) is in the whitelist."""
    if isinstance(loc, (list, tuple, set)):
        return all(item in VALID_LOCATIONS for item in loc)
    return loc in VALID_LOCATIONS


def validate_status(status) -> bool:
    """Return True if ``status`` (str or iterable of str) is a valid status."""
    if isinstance(status, (list, tuple, set)):
        return all(item in VALID_STATUSES for item in status)
    return status in VALID_STATUSES


def generate_session_id() -> str:
    """Generate an 8-char hex session id."""
    return uuid.uuid4().hex[:8]
