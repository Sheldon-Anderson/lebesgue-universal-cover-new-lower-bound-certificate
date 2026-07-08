"""Claim-boundary checks for the LaTeX paper source."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from ucbs.config.repository_policy import CLAIM_FORBIDDEN_PATTERNS, CLAIM_NEGATION_MARKERS

PAPER_SOURCE_PATH = Path("paper") / "source" / "main.tex"
"""Repository-relative LaTeX source checked by the release audit."""

PAPER_REQUIRED_SCOPE_TERMS = (
    "convex",
    "Brass--Sharifi",
    "three-test-set",
    "certificate",
    "not a statement about the unrestricted nonconvex problem",
    "not a proof-assistant formalization",
)
"""Scope terms that must remain present in the paper source."""


def _is_negated_context(line: str) -> bool:
    """Return whether a line is explicitly recording a non-claim."""
    lower = line.lower()
    return any(marker in lower for marker in CLAIM_NEGATION_MARKERS) or any(marker in line for marker in CLAIM_NEGATION_MARKERS)


def check_paper_claim_boundary(root: Path) -> list[dict[str, Any]]:
    """Return claim-boundary diagnostics for ``paper/source/main.tex``.

    Args:
        root: Repository root.

    Returns:
        Diagnostic rows for forbidden positive claims and for required scope
        language that must remain present in the paper source.
    """
    path = root / PAPER_SOURCE_PATH
    if not path.exists():
        return [{
            "check": "paper_claim_boundary_source_exists",
            "file": PAPER_SOURCE_PATH.as_posix(),
            "passed": False,
            "summary": "paper source is missing",
        }]

    text = path.read_text(encoding="utf-8", errors="replace")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if _is_negated_context(line):
            continue
        for pattern in CLAIM_FORBIDDEN_PATTERNS:
            for match in pattern.finditer(line):
                rows.append({
                    "check": "paper_claim_boundary_forbidden_claim",
                    "file": PAPER_SOURCE_PATH.as_posix(),
                    "line": line_number,
                    "match": match.group(0),
                    "passed": False,
                    "summary": "forbidden positive paper-claim pattern found",
                })
    for term in PAPER_REQUIRED_SCOPE_TERMS:
        rows.append({
            "check": "paper_claim_boundary_required_scope_term",
            "file": PAPER_SOURCE_PATH.as_posix(),
            "term": term,
            "passed": term in text,
            "summary": "required paper scope term is present" if term in text else "required paper scope term is missing",
        })
    return rows
