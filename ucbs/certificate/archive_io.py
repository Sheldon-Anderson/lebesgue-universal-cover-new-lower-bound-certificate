"""Input helpers for certificate-chain feedback archives."""
from __future__ import annotations

import csv
import json
import zipfile
from pathlib import Path
from typing import Any


def resolve_archive(root: Path, path: str | Path) -> Path:
    """Resolve an archive path relative to the repository root if needed."""
    candidate = Path(path)
    return candidate if candidate.is_absolute() else root / candidate


def relative_label(root: Path, path: Path) -> str:
    """Return a repository-relative label without exposing local absolute paths."""
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return f"<external>/{path.name}"


def list_members(archive_path: Path) -> list[str]:
    """List members in a ZIP archive."""
    with zipfile.ZipFile(archive_path) as archive:
        return archive.namelist()


def read_text_member(archive_path: Path, member: str) -> str:
    """Read one UTF-8 text member from a ZIP archive."""
    with zipfile.ZipFile(archive_path) as archive:
        with archive.open(member) as handle:
            return handle.read().decode("utf-8", errors="replace")


def read_json_member(archive_path: Path, member: str) -> dict[str, Any]:
    """Read one JSON object from a ZIP archive."""
    payload = json.loads(read_text_member(archive_path, member))
    if not isinstance(payload, dict):
        raise ValueError(f"archive member is not a JSON object: {member}")
    return payload


def read_csv_member(archive_path: Path, member: str) -> list[dict[str, str]]:
    """Read one CSV member from a ZIP archive."""
    text = read_text_member(archive_path, member)
    if not text.strip():
        return []
    return list(csv.DictReader(text.splitlines()))


def require_members(archive_path: Path, members: list[str]) -> list[dict[str, object]]:
    """Return diagnostic rows for required archive members."""
    archive_members = set(list_members(archive_path)) if archive_path.exists() else set()
    rows: list[dict[str, object]] = []
    for member in members:
        rows.append({
            "check": "required_archive_member",
            "member": member,
            "exists": member in archive_members,
            "passed": member in archive_members,
            "summary": "required member is present" if member in archive_members else "required member is missing",
        })
    return rows
