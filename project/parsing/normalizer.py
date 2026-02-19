"""
Normalize different kind of log formats to one standard format
and that is dictionary format
"""

import re
from datetime import datetime, timezone

# -----------------------------
# Supported severity levels
# -----------------------------
SEVERITIES = {"INFO", "WARN", "ERROR", "DEBUG", "FATAL"}

# -----------------------------
# Regex for TXT logs
# Supports:
#  - with / without milliseconds
#  - multiline messages (DOTALL)
# -----------------------------
LOG_REGEX = re.compile(
    r"""
    ^
    (?:\[)?
    (?P<ts>
        \d{4}-\d{2}-\d{2}\s+
        \d{2}:\d{2}:\d{2}
        (?:[.,]\d{3})?
    )
    (?:\])?
    \s+
    (?P<severity>INFO|WARN|ERROR|DEBUG|FATAL|info|warn|error|debug|fatal)
    \s+
    (?P<message>.+)
    $
    """,
    re.VERBOSE | re.DOTALL
)


def _parse_timestamp(ts: str) -> datetime | None:
    """
    Parse timestamp safely and normalize to UTC.
    Supports:
      - YYYY-MM-DD HH:MM:SS
      - YYYY-MM-DD HH:MM:SS,mmm
      - YYYY-MM-DD HH:MM:SS.mmm
      - ISO-8601 (JSON/XML)
    """
    try:
        ts = ts.strip()

        # TXT format (replace comma millis)
        if " " in ts:
            ts = ts.replace(",", ".")
            fmt = "%Y-%m-%d %H:%M:%S.%f" if "." in ts else "%Y-%m-%d %H:%M:%S"
            return datetime.strptime(ts, fmt).replace(tzinfo=timezone.utc)

        # ISO format (JSON/XML/CSV)
        ts = ts.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    except Exception:
        return None


def normalize_entry(entry):
    """
    Universal normalizer.

    Accepts:
      - str  → TXT logs
      - dict → JSON / XML / CSV records

    Returns:
      dict { timestamp, severity, message }
      or None (junk / invalid entry)
    """

    # ============================================================
    # CASE 1: TEXT LOG (TXT)
    # ============================================================
    if isinstance(entry, str):
        match = LOG_REGEX.match(entry)
        if not match:
            return None

        ts_raw = match.group("ts")
        severity = match.group("severity")
        message = match.group("message").strip()

        if not message:
            return None

        timestamp = _parse_timestamp(ts_raw)
        if not timestamp:
            return None

        return {
            "timestamp": timestamp,
            "severity": severity.upper(),
            "message": message
        }

    # ============================================================
    # CASE 2: STRUCTURED LOG (JSON / XML / CSV)
    # ============================================================
    if isinstance(entry, dict):
        ts_raw = (
            entry.get("timestamp")
            or entry.get("time")
            or entry.get("date")
        )

        severity = (
            entry.get("severity")
            or entry.get("level")
        )

        message = (
            entry.get("message")
            or entry.get("msg")
        )

        if not (ts_raw and severity and message):
            return None

        severity = str(severity).upper()
        if severity not in SEVERITIES:
            return None

        timestamp = _parse_timestamp(str(ts_raw))
        if not timestamp:
            return None

        return {
            "timestamp": timestamp,
            "severity": severity,
            "message": str(message)
        }

    # ============================================================
    # UNKNOWN TYPE
    # ============================================================
    return None
