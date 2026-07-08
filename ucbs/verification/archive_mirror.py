"""Consistency checks between component archives and expanded public records."""
from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path
from typing import Any

from ucbs.config.certificate_spec import ARCHIVE_PUBLIC_MIRROR_MAP, DEFAULT_ARTIFACT_ROOT


def _digest(payload: bytes) -> str:
    """Return the SHA256 digest of an in-memory byte payload."""
    return hashlib.sha256(payload).hexdigest()


def _archive_member_bytes(archive_path: Path, member: str) -> bytes | None:
    """Return bytes for one ZIP member, or ``None`` when unavailable.

    Args:
        archive_path: Filesystem path to the component archive.
        member: Archive-internal member name using POSIX separators.

    Returns:
        The exact member payload if both the archive and member exist;
        otherwise ``None``.
    """
    if not archive_path.exists():
        return None
    try:
        with zipfile.ZipFile(archive_path) as archive:
            if member not in archive.namelist():
                return None
            return archive.read(member)
    except zipfile.BadZipFile:
        return None


def check_archive_public_mirror(root: Path) -> list[dict[str, Any]]:
    """Check that public CSV/JSON files exactly mirror ZIP members.

    Args:
        root: Repository root.

    Returns:
        Diagnostic rows, one for every archive/member/public-file triple
        declared in the frozen certificate configuration. The check compares
        bytes, not parsed CSV/JSON objects, so it also catches newline and
        formatting drift.
    """
    rows: list[dict[str, Any]] = []
    for archive_name, member, public_relative_path in ARCHIVE_PUBLIC_MIRROR_MAP:
        archive_relative_path = DEFAULT_ARTIFACT_ROOT / archive_name
        archive_path = root / archive_relative_path
        public_path = root / public_relative_path
        archive_bytes = _archive_member_bytes(archive_path, member)
        public_exists = public_path.exists()
        public_bytes = public_path.read_bytes() if public_exists else None
        matched = archive_bytes is not None and public_bytes is not None and archive_bytes == public_bytes
        rows.append({
            "check": "archive_public_mirror",
            "archive": archive_relative_path.as_posix(),
            "member": member,
            "public_path": public_relative_path.as_posix(),
            "archive_member_exists": archive_bytes is not None,
            "public_file_exists": public_exists,
            "archive_sha256": _digest(archive_bytes) if archive_bytes is not None else "",
            "public_sha256": _digest(public_bytes) if public_bytes is not None else "",
            "passed": matched,
            "summary": "expanded public record matches archive member" if matched else "expanded public record differs from archive member",
        })
    return rows
