"""Logging policy constants for public command-line runs."""
from __future__ import annotations

VALID_LOG_LEVELS = frozenset({"TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"})
"""Log levels accepted by the public CLI wrappers."""

LOG_FORMAT = "[{time:YYYY-MM-DDTHH:mm:ss.SSS!UTC}] {level} {message}"
"""Stable one-line log format used by replay and repository-check logs."""
