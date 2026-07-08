"""Loguru-backed file logging helpers for public command-line runs."""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Iterator

from loguru import logger

from ucbs.config.logging_config import LOG_FORMAT, VALID_LOG_LEVELS

_ACTIVE_SINKS: dict[str, int] = {}
_DEFAULT_SINK_REMOVED = False
_LOG_PATH_KEY = "ucbs_log_path"


def _normalize_path_key(log_path: Path) -> str:
    """Return a stable key used by loguru filters for one run log."""
    return str(log_path.resolve())


def _ensure_default_sink_removed() -> None:
    """Remove loguru's default stderr sink once for quiet JSON CLI output."""
    global _DEFAULT_SINK_REMOVED
    if not _DEFAULT_SINK_REMOVED:
        logger.remove()
        _DEFAULT_SINK_REMOVED = True


def normalize_log_level(level: str | None) -> str:
    """Return a loguru-compatible log level.

    Args:
        level: User-supplied log-level string from the command line.

    Returns:
        A normalized uppercase log-level name. Unknown values fall back to
        ``INFO`` so direct script invocations remain robust.
    """
    candidate = str(level or "INFO").strip().upper()
    return candidate if candidate in VALID_LOG_LEVELS else "INFO"


def _add_sink(log_path: Path, level: str) -> int:
    """Add one filtered loguru sink for ``log_path`` and return its id."""
    _ensure_default_sink_removed()
    key = _normalize_path_key(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    return logger.add(
        log_path,
        level=normalize_log_level(level),
        format=LOG_FORMAT,
        backtrace=False,
        diagnose=False,
        enqueue=False,
        filter=lambda record, expected=key: record["extra"].get(_LOG_PATH_KEY) == expected,
    )


def _emit(log_path: Path, message: str, level: str = "INFO") -> None:
    """Emit one message routed to the sink for ``log_path``."""
    key = _normalize_path_key(log_path)
    logger.bind(**{_LOG_PATH_KEY: key}).log(normalize_log_level(level), message)


@contextmanager
def configured_run_logger(log_path: Path, level: str = "INFO", *, reset: bool = False) -> Iterator[None]:
    """Configure one filtered file sink for a command run.

    Args:
        log_path: Destination log file.
        level: Minimum log level requested by the command-line caller.
        reset: Whether to replace stale log-file content before configuring the
            sink.

    Side effects:
        Adds a loguru sink keyed to ``log_path`` and removes it on exit. The key
        filter prevents nested repository and certificate runs from writing to
        one another's log files.
    """
    key = _normalize_path_key(log_path)
    old_sink = _ACTIVE_SINKS.pop(key, None)
    if old_sink is not None:
        logger.remove(old_sink)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if reset:
        log_path.write_text("", encoding="utf-8")
    sink_id = _add_sink(log_path, level)
    _ACTIVE_SINKS[key] = sink_id
    try:
        yield
    finally:
        current = _ACTIVE_SINKS.pop(key, None)
        if current is not None:
            logger.remove(current)


def log_to_file(log_path: Path, message: str, level: str = "INFO") -> None:
    """Append one English log line to ``log_path`` using loguru.

    Args:
        log_path: Destination log file. Parent directories are created when
            needed.
        message: English message to write.
        level: Minimum log level requested by the command-line caller.

    Side effects:
        Reuses the active sink for the run log. If called standalone by a unit
        test or utility, it configures a temporary filtered sink for the single
        message.
    """
    key = _normalize_path_key(log_path)
    if key in _ACTIVE_SINKS:
        _emit(log_path, message, level=level)
        return
    with configured_run_logger(log_path, level=level, reset=False):
        _emit(log_path, message, level=level)


def start_run_log(log_path: Path, lines: Iterable[str], level: str = "INFO") -> None:
    """Create a fresh run log and configure its sink once for the process.

    Args:
        log_path: Destination log file.
        lines: Header lines to write as individual log records.
        level: Minimum log level requested by the command-line caller.
    """
    key = _normalize_path_key(log_path)
    old_sink = _ACTIVE_SINKS.pop(key, None)
    if old_sink is not None:
        logger.remove(old_sink)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("", encoding="utf-8")
    _ACTIVE_SINKS[key] = _add_sink(log_path, level)
    for line in lines:
        _emit(log_path, line, level=level)


def close_run_log(log_path: Path) -> None:
    """Remove the active loguru sink for one run log when it exists.

    Args:
        log_path: Destination log file whose filtered sink should be closed.

    Side effects:
        Detaches the sink associated with ``log_path``. This keeps command-line
        runs clean when the verifier is embedded in a longer-lived Python
        process instead of being executed as a short-lived script.
    """
    key = _normalize_path_key(log_path)
    sink_id = _ACTIVE_SINKS.pop(key, None)
    if sink_id is not None:
        logger.remove(sink_id)
