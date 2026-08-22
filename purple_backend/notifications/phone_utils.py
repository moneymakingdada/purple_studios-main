"""
Normalizes Ghanaian phone numbers into the international format Arkesel
expects (+233XXXXXXXXX), regardless of how the user actually typed it in.

Ghanaians commonly write numbers in local format (0240338541) rather than
international (+233240338541) — nothing in the registration form enforces
one format, so we normalize at send-time instead of relying on input discipline.
"""
import re


def normalize_ghana_phone(raw: str) -> str | None:
    """
    Accepts any of: 0240338541, 233240338541, +233240338541, with or without
    spaces/dashes. Returns clean +233XXXXXXXXX format, or None if it doesn't
    look like a valid Ghanaian number at all.
    """
    if not raw:
        return None

    digits = re.sub(r"[^\d+]", "", raw)  # strip spaces, dashes, parens

    if digits.startswith("+233") and len(digits) == 13:
        return digits

    if digits.startswith("233") and len(digits) == 12:
        return f"+{digits}"

    if digits.startswith("0") and len(digits) == 10:
        return f"+233{digits[1:]}"

    # Already 9 digits with no leading 0/233 (rare, but handle it)
    if len(digits) == 9 and digits.isdigit():
        return f"+233{digits}"

    return None
