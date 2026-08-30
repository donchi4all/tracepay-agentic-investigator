"""Redaction and untrusted-content controls."""

import re
from typing import Any, Dict, List, Tuple


SENSITIVE_KEY = re.compile(
    r"(^|_)(pin|otp|token|secret|password|account_?number|pan|email)(_|$)", re.IGNORECASE
)
LONG_DIGITS = re.compile(r"(?<![A-Za-z0-9])\d{8,19}(?![A-Za-z0-9])")
EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
BEARER = re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]+", re.IGNORECASE)
LOCAL_HOME_PATH = re.compile(
    r"(?:(?:/Users|/home)/[^/\s\"']+)(?:/[^\s\"']*)?|[A-Z]:\\Users\\[^\\\s\"']+(?:\\[^\s\"']*)?",
    re.IGNORECASE,
)
INJECTION = re.compile(
    r"(ignore\s+(all\s+)?previous\s+instructions|system\s*:|developer\s*:|retry\s+the\s+payment|execute\s+payment)",
    re.IGNORECASE,
)


def _redact_string(value: str) -> str:
    value = BEARER.sub("[REDACTED_BEARER]", value)
    value = EMAIL.sub("[REDACTED_EMAIL]", value)
    value = LONG_DIGITS.sub("[REDACTED_NUMBER]", value)
    value = LOCAL_HOME_PATH.sub("[REDACTED_LOCAL_PATH]", value)
    return value


def redact(value: Any, key: str = "") -> Any:
    """Return a sanitized deep copy; never mutate fixture data."""
    if key and SENSITIVE_KEY.search(key):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {str(k): redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str):
        return _redact_string(value)
    return value


def find_untrusted_instruction_text(payload: Dict[str, Any]) -> List[str]:
    """Flag hostile-looking data for audit without interpreting it as instructions."""
    findings: List[str] = []

    def walk(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for child_key, child in value.items():
                walk(child, "%s.%s" % (path, child_key))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, "%s[%d]" % (path, index))
        elif isinstance(value, str) and INJECTION.search(value):
            findings.append(path)

    walk(payload, "payload")
    return findings


def recommendations_are_safe(recommendations: List[Dict[str, Any]]) -> Tuple[bool, List[int]]:
    unsafe = [
        index
        for index, item in enumerate(recommendations)
        if item.get("approval") != "REQUIRES_HUMAN_APPROVAL"
    ]
    return not unsafe, unsafe
