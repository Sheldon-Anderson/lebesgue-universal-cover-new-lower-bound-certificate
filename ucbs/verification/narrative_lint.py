"""Clean-story checks for public Markdown and certificate notes."""
from __future__ import annotations

import re
from pathlib import Path

from ucbs.config.repository_policy import INLINE_CODE_PATTERN, NARRATIVE_FORBIDDEN_PATTERNS


def checked_text_files(root: Path) -> list[Path]:
    """Return public text files checked for the clean certificate narrative."""
    paths = [root / "README.md", root / "README.zh-CN.md"]
    for folder in [root / "docs", root / "certificate" / "public"]:
        if folder.exists():
            paths.extend(folder.rglob("*.md"))
    return sorted(path for path in paths if path.exists())


def _strip_fenced_code(text: str) -> str:
    """Remove fenced code blocks and inline code from narrative checks."""
    stripped = re.sub(r"```.*?```", lambda match: "\n" * match.group(0).count("\n"), text, flags=re.DOTALL)
    return INLINE_CODE_PATTERN.sub(lambda match: " " * len(match.group(0)), stripped)


def check_narrative_lint(root: Path) -> list[dict[str, object]]:
    """Return forbidden wording found in public text."""
    rows: list[dict[str, object]] = []
    for path in checked_text_files(root):
        text = _strip_fenced_code(path.read_text(encoding="utf-8", errors="replace"))
        for line_number, line in enumerate(text.splitlines(), start=1):
            for pattern, issue in NARRATIVE_FORBIDDEN_PATTERNS:
                for match in pattern.finditer(line):
                    rows.append({
                        "check": "narrative_lint",
                        "file": str(path.relative_to(root)),
                        "line": line_number,
                        "issue": issue,
                        "fragment": match.group(0),
                        "passed": False,
                        "summary": "forbidden public wording found",
                    })
    return rows
