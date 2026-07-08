"""Claim-boundary checks for public repository text."""
from __future__ import annotations

from pathlib import Path

from ucbs.config.repository_policy import CLAIM_FORBIDDEN_PATTERNS, CLAIM_NEGATION_MARKERS


def checked_text_files(root: Path) -> list[Path]:
    """Return text files whose public claims should be linted."""
    paths = [root / "README.md", root / "README.zh-CN.md"]
    for folder in [root / "docs", root / "certificate" / "public"]:
        if folder.exists():
            paths.extend(folder.rglob("*.md"))
    return sorted(path for path in paths if path.exists())


def _is_negated_context(line: str) -> bool:
    """Return whether a line is explicitly recording a non-claim."""
    lower = line.lower()
    return any(marker in lower for marker in CLAIM_NEGATION_MARKERS) or any(marker in line for marker in CLAIM_NEGATION_MARKERS)


def check_claim_boundary(root: Path) -> list[dict[str, object]]:
    """Return forbidden public-claim matches found in repository text.

    The linter is claim-oriented.  It ignores lines that explicitly state a
    non-claim, so the repository can safely document its scope boundaries.
    """
    rows: list[dict[str, object]] = []
    for path in checked_text_files(root):
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        offset = 0
        for line_number, line in enumerate(lines, start=1):
            if _is_negated_context(line):
                offset += len(line) + 1
                continue
            for pattern in CLAIM_FORBIDDEN_PATTERNS:
                for match in pattern.finditer(line):
                    rows.append({
                        "check": "claim_boundary",
                        "file": str(path.relative_to(root)),
                        "line": line_number,
                        "match": match.group(0),
                        "position": offset + match.start(),
                        "passed": False,
                        "summary": "forbidden public-claim pattern found",
                    })
            offset += len(line) + 1
    return rows
