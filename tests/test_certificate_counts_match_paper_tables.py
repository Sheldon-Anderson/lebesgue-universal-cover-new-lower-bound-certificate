"""Regression tests matching configured certificate counts to paper tables."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from ucbs.config.certificate_spec import PAPER_TABLE_COUNT_ROWS

TABLE_ROW_GROUPS = {
    "tab:component-summary": (
        "parameter domains",
        "directed interval records",
        "tensor records",
        "bridge records",
        "witness domains",
    ),
    "tab:final-adjudication-summary": (
        "frozen certificate records",
        "final-replay records",
        "event-aware interval records",
        "witness/source records",
        "thin extra records",
        "final blockers",
    ),
    "tab:witness-counts": (
        "witness domains",
        "accepted terminal subdomains",
        "unresolved terminal subdomains",
        "witness point incidences",
        "point-containment certificates",
    ),
    "tab:witness-bounds": (
        "minimum witness-domain area bound",
        "minimum excess over tau",
        "minimum orientation determinant lower endpoint",
    ),
}
"""Paper table labels and the configured row labels expected in each table."""


def _normalize_latex_table_text(text: str) -> str:
    """Collapse LaTeX table text into a comparison-friendly string."""
    replacements = {
        "\\(": "",
        "\\)": "",
        "\\,": "",
        "\\target": "tau",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return "".join(text.lower().split())


def _table_containing_label(text: str, label: str) -> str:
    """Return the LaTeX table environment that contains ``label``."""
    pattern = re.compile(r"\\begin\{table\}.*?\\end\{table\}", flags=re.DOTALL)
    for match in pattern.finditer(text):
        table = match.group(0)
        if f"\\label{{{label}}}" in table:
            return table
    raise AssertionError(f"table {label!r} was not found")


class CertificateCountsMatchPaperTablesTests(unittest.TestCase):
    """Check that paper tables expose the configured public certificate counts."""

    def test_configured_table_rows_appear_in_expected_tables(self) -> None:
        """Every configured row label must appear with its intended table value."""
        source = Path("paper/source/main.tex").read_text(encoding="utf-8")
        missing: list[str] = []
        for table_label, row_labels in TABLE_ROW_GROUPS.items():
            table = _normalize_latex_table_text(_table_containing_label(source, table_label))
            for row_label in row_labels:
                value = PAPER_TABLE_COUNT_ROWS[row_label]
                expected = _normalize_latex_table_text(f"{row_label}&{value}")
                if expected not in table:
                    missing.append(f"{table_label}: {row_label} -> {value}")
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
