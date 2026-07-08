"""Regression tests for ZIP/public certificate mirror consistency."""
from __future__ import annotations

import unittest
from pathlib import Path

from ucbs.verification.archive_mirror import check_archive_public_mirror


class ArchivePublicMirrorTests(unittest.TestCase):
    """Check expanded public certificate records against ZIP members."""

    def test_archive_public_mirror_check_passes(self) -> None:
        """Bundled public CSV/JSON files must match their ZIP members byte for byte."""
        rows = check_archive_public_mirror(Path("."))
        failures = [row for row in rows if not row.get("passed")]
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
