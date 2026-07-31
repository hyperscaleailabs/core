"""Redaction - strip secrets / raw sensitive fields before telemetry emission.

Raw output is stored to object storage behind access control and referenced by ``rawOutputRef``;
it must never appear on the event stream (``docs/design/SYSTEM_DESIGN.md`` §14).
"""

from __future__ import annotations

import re
from typing import Any

# Field names whose values are always dropped from emitted telemetry.
SENSITIVE_KEYS = frozenset(
    {
        "password",
        "secret",
        "token",
        "api_key",
        "apikey",
        "authorization",
        "card_number",
        "cardnumber",
        "cvv",
        "ssn",
        "raw_output",
        "rawoutput",
        "credentials",
    }
)

_PATTERNS = [
    re.compile(r"\b\d{13,19}\b"),  # PAN-like numbers
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN
    re.compile(r"(?i)\b(sk|pk|ghp)_[A-Za-z0-9]{16,}\b"),  # API-key-like tokens
]

REDACTED = "[REDACTED]"


def redact(value: Any) -> Any:
    """Recursively redact sensitive keys and value patterns. Pure; returns a new structure."""
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            if str(k).lower() in SENSITIVE_KEYS:
                out[k] = REDACTED
            else:
                out[k] = redact(v)
        return out
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, str):
        redacted = value
        for pat in _PATTERNS:
            redacted = pat.sub(REDACTED, redacted)
        return redacted
    return value
