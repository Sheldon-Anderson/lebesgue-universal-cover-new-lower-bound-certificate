"""Regression tests for loguru-backed run logging."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ucbs.cli.logging import close_run_log, log_to_file, start_run_log


class LoguruLoggingTests(unittest.TestCase):
    """Check that public logs are written through the loguru helper."""

    def test_single_log_line_is_written(self) -> None:
        """A loguru-backed helper call must append an English message."""
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "run.log"
            log_to_file(log_path, "sample repository check message")
            payload = log_path.read_text(encoding="utf-8")
            self.assertIn("INFO", payload)
            self.assertIn("sample repository check message", payload)

    def test_start_run_log_resets_file(self) -> None:
        """Starting a run log must replace stale file content."""
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "run.log"
            log_path.write_text("stale content\n", encoding="utf-8")
            start_run_log(log_path, ["new run started"])
            close_run_log(log_path)
            payload = log_path.read_text(encoding="utf-8")
            self.assertNotIn("stale content", payload)
            self.assertIn("new run started", payload)


if __name__ == "__main__":
    unittest.main()
