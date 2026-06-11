"""Markdown math rendering checks for README and public documentation files."""
from __future__ import annotations

import re
from pathlib import Path

BAD_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\\\([^\n]*?\\\)"), "non-GitHub inline math delimiter"),
    (re.compile(r"\\\[[\s\S]*?\\\]"), "non-GitHub display math delimiter"),
    (re.compile(r"\$`"), "backtick math marker"),
    (re.compile(r"`\$"), "backtick math marker"),
    (re.compile(r"\bOmega_(adm|B|r)\b"), "plain-text Omega symbol"),
    (re.compile(r"\balpha_cvx\b"), "plain-text alpha symbol"),
    (re.compile(r"\bconv\s+Q\b"), "plain-text convex hull expression"),
    (re.compile(r"\bunion_r\b"), "plain-text union expression"),
    (re.compile(r"(?<!\\)\bsubset\b"), "plain-text subset relation"),
]


def markdown_files(root: Path) -> list[Path]:
    """Return public Markdown files checked by the repository audit."""
    candidates = [root / "README.md", root / "README.zh-CN.md"]
    for folder in [root / "docs", root / "certificate" / "public"]:
        if folder.exists():
            candidates.extend(folder.rglob("*.md"))
    return sorted(path for path in candidates if path.exists())


def _strip_fenced_code(text: str) -> str:
    """Replace fenced code blocks and inline code spans with spaces."""
    text = re.sub(r"```.*?```", lambda match: "\n" * match.group(0).count("\n"), text, flags=re.DOTALL)
    return re.sub(r"`[^`]*`", lambda match: " " * len(match.group(0)), text)


def _line_number(text: str, position: int) -> int:
    """Return the one-based line number for a character offset."""
    return text.count("\n", 0, position) + 1


def check_markdown_math(root: Path) -> list[dict[str, object]]:
    """Detect mathematical fragments that are likely not rendered by GitHub."""
    rows: list[dict[str, object]] = []
    for path in markdown_files(root):
        original = path.read_text(encoding="utf-8", errors="replace")
        text = _strip_fenced_code(original)
        for pattern, label in BAD_PATTERNS:
            for match in pattern.finditer(text):
                rows.append({
                    "check": "readme_math",
                    "file": str(path.relative_to(root)),
                    "line": _line_number(original, match.start()),
                    "issue": label,
                    "fragment": match.group(0),
                    "position": match.start(),
                    "passed": False,
                    "summary": "markdown math lint issue found",
                })
    return rows
