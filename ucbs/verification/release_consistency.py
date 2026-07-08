"""Release-metadata consistency checks for the public repository."""
from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any

from ucbs import __version__
from ucbs.config.release_config import (
    CERTIFIED_THRESHOLD_TEXT,
    PAPER_TITLE,
    RELEASE_TAG,
    RELEASE_VERSION,
    RUNTIME_DEPENDENCIES,
)


def _read_text(path: Path) -> str:
    """Read a UTF-8 text file, returning an empty string when it is absent."""
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def _row(check: str, passed: bool, path: str, summary: str, value: Any = "") -> dict[str, Any]:
    """Build one release-consistency diagnostic row."""
    return {
        "check": check,
        "path": path,
        "value": value,
        "passed": passed,
        "summary": summary,
    }


def _citation_version(text: str) -> str:
    """Extract the ``version`` field from a CFF text payload."""
    match = re.search(r'^version:\s*["\']?([^"\'\n]+)', text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _citation_title(text: str) -> str:
    """Extract the ``title`` field from a CFF text payload.

    The title contains an apostrophe in ``Lebesgue's``, so the parser strips
    only the outer YAML quotes instead of treating every apostrophe as a field
    delimiter.
    """
    match = re.search(r"^title:\s*(.+)$", text, flags=re.MULTILINE)
    if not match:
        return ""
    value = match.group(1).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return value.strip()


def check_release_consistency(root: Path) -> list[dict[str, Any]]:
    """Check version, dependency, and README coverage for this release.

    Args:
        root: Repository root.

    Returns:
        Diagnostic rows consumed by the repository-level release check.
    """
    rows: list[dict[str, Any]] = []
    pyproject_path = root / "pyproject.toml"
    pyproject_text = _read_text(pyproject_path)
    try:
        pyproject = tomllib.loads(pyproject_text) if pyproject_text else {}
    except tomllib.TOMLDecodeError as exc:
        pyproject = {}
        rows.append(_row("pyproject_parse", False, "pyproject.toml", "pyproject.toml is valid TOML", str(exc)))

    project = pyproject.get("project", {}) if isinstance(pyproject, dict) else {}
    version = str(project.get("version", ""))
    dependencies = tuple(str(item) for item in project.get("dependencies", []))
    rows.append(_row("package_dunder_version", __version__ == RELEASE_VERSION, "ucbs/__init__.py", "package __version__ matches release configuration", __version__))
    rows.append(_row("pyproject_release_version", version == RELEASE_VERSION, "pyproject.toml", "pyproject version matches release configuration", version))
    rows.append(_row("pyproject_runtime_dependencies", all(dep in dependencies for dep in RUNTIME_DEPENDENCIES), "pyproject.toml", "pyproject lists required runtime dependencies", ";".join(dependencies)))

    citation_text = _read_text(root / "CITATION.cff")
    citation_version = _citation_version(citation_text)
    citation_title = _citation_title(citation_text)
    rows.append(_row("citation_release_version", citation_version == RELEASE_VERSION, "CITATION.cff", "CITATION.cff version matches release configuration", citation_version))
    rows.append(_row("citation_paper_title", citation_title == PAPER_TITLE, "CITATION.cff", "CITATION.cff title matches release configuration", citation_title))

    paper_source = _read_text(root / "paper" / "source" / "main.tex")
    tex_title = f"\\title{{{PAPER_TITLE}}}"
    tex_pdf_title = f"pdftitle={{{PAPER_TITLE}}}"
    rows.append(_row("paper_latex_title", tex_title in paper_source, "paper/source/main.tex", "LaTeX title matches release configuration", tex_title))
    rows.append(_row("paper_latex_pdf_title_metadata", tex_pdf_title in paper_source, "paper/source/main.tex", "LaTeX PDF metadata title matches release configuration", tex_pdf_title))

    requirements_text = _read_text(root / "requirements.txt")
    rows.append(_row("requirements_runtime_dependencies", all(dep in requirements_text for dep in RUNTIME_DEPENDENCIES), "requirements.txt", "requirements.txt lists required runtime dependencies", requirements_text.replace("\n", ";")[:240]))

    release_notes = _read_text(root / "RELEASE_NOTES.md")
    rows.append(_row("release_notes_tag", RELEASE_TAG in release_notes, "RELEASE_NOTES.md", "release notes name the canonical release tag", RELEASE_TAG))
    rows.append(_row("release_notes_threshold", CERTIFIED_THRESHOLD_TEXT in release_notes, "RELEASE_NOTES.md", "release notes state the certified threshold", CERTIFIED_THRESHOLD_TEXT))

    readme = _read_text(root / "README.md")
    readme_zh = _read_text(root / "README.zh-CN.md")
    rows.append(_row("readme_english_h1_title", readme.startswith(f"# {PAPER_TITLE}"), "README.md", "English README H1 matches the canonical paper title"))
    rows.append(_row("readme_english_scope_after_title", "convex Brass-Sharifi three-test-set framework" in readme, "README.md", "English README keeps the convex framework scope after the broad title"))

    for rel, text in [("README.md", readme), ("README.zh-CN.md", readme_zh)]:
        rows.append(_row("readme_developer_tests", "python -B -m unittest discover -s tests" in text, rel, "README documents the bytecode-free developer regression-test command"))
        rows.append(_row("readme_loguru_dependency", "loguru" in text.lower(), rel, "README documents the loguru runtime logging dependency"))
        rows.append(_row("readme_release_check_scope", "release/version" in text.lower() or "\u7248\u672c\u4e00\u81f4\u6027" in text, rel, "README documents release/version consistency checks"))
        rows.append(_row("readme_paper_title_consistency_scope", "title consistency" in text.lower() or "\u8bba\u6587\u6807\u9898\u4e00\u81f4\u6027" in text, rel, "README documents paper-title consistency checks"))

    return rows
