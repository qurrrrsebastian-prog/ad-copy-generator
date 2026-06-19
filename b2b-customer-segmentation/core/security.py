"""Security helpers: input sanitization, validation, session IDs, data masking.

All user-facing text must be treated as untrusted. Streamlit renders markdown,
so we strip HTML/script tags and bound length before anything is echoed back.
"""
import html
import re
import uuid

MAX_TEXT_LEN = 500
_TAG_RE = re.compile(r"<[^>]*>")


def sanitize_input(text) -> str:
    """Strip HTML tags, escape entities, and clamp to 500 chars.

    Defends against XSS / markdown injection when echoing user text back into
    the Streamlit UI. Non-string input is coerced to an empty string.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    # Remove any tag-like sequences, then escape remaining special chars.
    stripped = _TAG_RE.sub("", text)
    escaped = html.escape(stripped, quote=True)
    return escaped[:MAX_TEXT_LEN].strip()


def validate_numeric(value, min_val=None, max_val=None) -> bool:
    """Return True if value is a finite number within [min_val, max_val].

    Used for revenue/employees/contract_value (> 0) and engagement_score (0-100).
    """
    try:
        num = float(value)
    except (TypeError, ValueError):
        return False
    if num != num or num in (float("inf"), float("-inf")):  # NaN / inf guard
        return False
    if min_val is not None and num < min_val:
        return False
    if max_val is not None and num > max_val:
        return False
    return True


def validate_select(value, options) -> bool:
    """Check that value (scalar or list) is a member / subset of options."""
    try:
        opts = set(options)
    except TypeError:
        return False
    if isinstance(value, (list, tuple, set)):
        return all(v in opts for v in value)
    return value in opts


def generate_session_id() -> str:
    """Return an 8-char hex session identifier (uuid4-derived)."""
    return uuid.uuid4().hex[:8]


def mask_company_name(name) -> str:
    """Mask a company name for demo/privacy mode: first 3 chars + '***'.

    Example: 'Company_42' -> 'Com***'. Short names are masked fully.
    """
    safe = sanitize_input(name)
    if not safe:
        return "***"
    if len(safe) <= 3:
        return "***"
    return f"{safe[:3]}***"
