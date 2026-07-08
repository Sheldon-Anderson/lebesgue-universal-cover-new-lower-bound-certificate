"""Regression tests for release metadata and runtime dependencies."""
from __future__ import annotations

import tomllib
import unittest
from pathlib import Path

from ucbs import __version__
from ucbs.config.release_config import PAPER_TITLE, RELEASE_VERSION, RUNTIME_DEPENDENCIES
from ucbs.verification.release_consistency import check_release_consistency


class ReleaseVersionConsistencyTests(unittest.TestCase):
    """Check that release metadata uses the configured public version."""

    def test_pyproject_version_and_dependencies(self) -> None:
        """pyproject metadata and package version must match release configuration."""
        pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
        project = pyproject["project"]
        self.assertEqual(__version__, RELEASE_VERSION)
        self.assertEqual(project["version"], RELEASE_VERSION)
        for dependency in RUNTIME_DEPENDENCIES:
            self.assertIn(dependency, project["dependencies"])


    def test_paper_title_is_consistent_across_release_metadata(self) -> None:
        """The canonical paper title must match public metadata files."""
        self.assertIn(f"# {PAPER_TITLE}", Path("README.md").read_text(encoding="utf-8"))
        self.assertIn(f'title: "{PAPER_TITLE}"', Path("CITATION.cff").read_text(encoding="utf-8"))
        paper_source = Path("paper/source/main.tex").read_text(encoding="utf-8")
        self.assertIn(f"\\title{{{PAPER_TITLE}}}", paper_source)
        self.assertIn(f"pdftitle={{{PAPER_TITLE}}}", paper_source)

    def test_repository_release_consistency_check_passes(self) -> None:
        """The repository-level release-consistency diagnostic must be clean."""
        rows = check_release_consistency(Path("."))
        failures = [row for row in rows if not row.get("passed")]
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
