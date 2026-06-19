"""Security utilities for AI Ad Copy Generator. Author: Avatar Putra Sigit

Input sanitization, validation, session id generation, and sensitive-data
masking. All functions are pure and safe to import without side effects.
"""
import re
import uuid

# Allowed characters: alphanumeric, whitespace, basic punctuation, Indonesian chars.
_ALLOWED_RE = re.compile(r"[^a-zA-Z0-9\s.,!?()\-'\"/:&%+@éÉàèùçÀÈ]", re.UNICODE)
_TAG_RE = re.compile(r"<[^>]*>")
_SCRIPT_RE = re.compile(r"(?is)<\s*script.*?>.*?<\s*/\s*script\s*>")
_EMAIL_RE = re.compile(r"([A-Za-z0-9._%+\-])([A-Za-z0-9._%+\-]*)(@[A-Za-z0-9.\-]+\.[A-Za-z]{2,})")
_PHONE_RE = re.compile(r"(\+?\d[\d\s\-]{7,}\d)")

MAX_LEN = 500


def sanitize_input(text: str) -> str:
    """Strip HTML/script tags and disallowed chars, trim, and cap at 500 chars."""
    if text is None:
        return ""
    text = str(text)
    # Remove <script>...</script> blocks first, then any remaining tags.
    text = _SCRIPT_RE.sub("", text)
    text = _TAG_RE.sub("", text)
    # Drop characters outside the allowlist.
    text = _ALLOWED_RE.sub("", text)
    text = text.strip()
    return text[:MAX_LEN]


def validate_select(value: str, options) -> str:
    """Ensure value is one of options (guards against dropdown tampering)."""
    if value not in options:
        raise ValueError(f"Pilihan tidak valid: {value!r}. Harus salah satu dari {list(options)}.")
    return value


def validate_text_length(text: str, min: int = 3, max: int = 500) -> str:
    """Raise ValueError if the trimmed text length is outside [min, max]."""
    cleaned = (text or "").strip()
    n = len(cleaned)
    if n < min:
        raise ValueError(f"Teks terlalu pendek (min {min} karakter, ada {n}).")
    if n > max:
        raise ValueError(f"Teks terlalu panjang (max {max} karakter, ada {n}).")
    return cleaned


def generate_session_id() -> str:
    """Return an 8-char hex session id."""
    return uuid.uuid4().hex[:8]


def mask_sensitive(text: str) -> str:
    """Mask emails and phone numbers found inside free text."""
    if not text:
        return ""

    def _mask_email(m: "re.Match") -> str:
        first, _mid, domain = m.group(1), m.group(2), m.group(3)
        return f"{first}***{domain}"

    def _mask_phone(m: "re.Match") -> str:
        digits = re.sub(r"\D", "", m.group(1))
        if len(digits) <= 4:
            return "*" * len(digits)
        return digits[:2] + "*" * (len(digits) - 4) + digits[-2:]

    text = _EMAIL_RE.sub(_mask_email, text)
    text = _PHONE_RE.sub(_mask_phone, text)
    return text
