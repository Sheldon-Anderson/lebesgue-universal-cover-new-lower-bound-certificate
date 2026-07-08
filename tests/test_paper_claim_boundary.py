"""Regression tests for LaTeX paper claim-boundary checks."""
from __future__ import annotations

import unittest
from pathlib import Path

from ucbs.verification.paper_claim_boundary import check_paper_claim_boundary


class PaperClaimBoundaryTests(unittest.TestCase):
    """Check that paper source keeps the public certificate scope."""

    def test_paper_claim_boundary_check_passes(self) -> None:
        """The bundled paper source must not contain forbidden positive claims."""
        rows = check_paper_claim_boundary(Path("."))
        failures = [row for row in rows if not row.get("passed")]
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
