"""Repository-level checks for the public certified lower-bound package."""
from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from ucbs.verification.artifact_checks import verify_key_artifact_hashes
from ucbs.verification.claim_boundary import check_claim_boundary
from ucbs.verification.markdown_math import check_markdown_math
from ucbs.verification.narrative_lint import check_narrative_lint
from ucbs.certificate.chain_replay import verify_certificate


@dataclass(frozen=True)
class RepositoryCheckResult:
    """Outcome of the public repository check."""

    status: str
    failed_step_count: int
    feedback: Path


def _truthy(value: Any) -> bool:
    """Interpret common serialized Boolean representations."""
    return value is True or str(value).strip().lower() in {"true", "1", "yes", "passed", "ok"}


def _write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    """Write diagnostic rows to CSV with a stable header."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    fields: list[str] = list(fieldnames or [])
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    if not fields:
        fields = ["check", "issue_count", "passed", "summary"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write a JSON object to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _summary_row(name: str, passed: bool, issue_count: int, summary: str) -> dict[str, Any]:
    """Build a standard diagnostic summary row."""
    return {"check": f"{name}_summary", "issue_count": issue_count, "passed": passed, "summary": summary}


def _with_summary(name: str, rows: list[dict[str, Any]], ok_summary: str, bad_summary: str) -> list[dict[str, Any]]:
    """Append a summary row to diagnostic rows."""
    issue_count = sum(1 for row in rows if row.get("passed") is False or str(row.get("passed", "")).lower() == "false")
    passed = issue_count == 0
    return [*rows, _summary_row(name, passed, issue_count, ok_summary if passed else bad_summary)]


def _append_log(log_path: Path, message: str) -> None:
    """Append one UTC-stamped line to the repository-check log."""
    timestamp = datetime.now(timezone.utc).isoformat()
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"[{timestamp}] {message}\n")


def _rel(path: Path, root: Path) -> str:
    """Return a repository-relative path when possible."""
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return f"<external>/{path.name}"


def check_python_compile(root: Path) -> list[dict[str, Any]]:
    """Compile every Python source file under ``ucbs`` and ``scripts``."""
    files = sorted([*root.glob("ucbs/**/*.py"), *root.glob("scripts/*.py")])
    if not files:
        return [{"check": "python_compile", "passed": False, "file_count": 0, "output": "no Python files found"}]
    cmd = [sys.executable, "-m", "py_compile", *map(str, files)]
    proc = subprocess.run(cmd, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    return [{"check": "python_compile", "passed": proc.returncode == 0, "file_count": len(files), "output": proc.stdout[-2000:]}]


def check_pyproject_config(root: Path) -> list[dict[str, Any]]:
    """Check that packaging metadata points to the public ``ucbs`` package."""
    path = root / "pyproject.toml"
    if not path.exists():
        return [{"check": "pyproject_exists", "passed": False, "path": "pyproject.toml", "summary": "missing pyproject.toml"}]
    text = path.read_text(encoding="utf-8")
    return [
        {"check": "pyproject_exists", "passed": True, "path": "pyproject.toml", "summary": "pyproject.toml is present"},
        {"check": "pyproject_uses_ucbs_package", "passed": "ucbs*" in text or "ucbs" in text, "path": "pyproject.toml", "summary": "package discovery includes ucbs"},
        {"check": "pyproject_no_stale_app_package", "passed": "packages = [\"app\"]" not in text and "packages = ['app']" not in text, "path": "pyproject.toml", "summary": "stale app package is not referenced"},
    ]


def check_layout(root: Path) -> list[dict[str, Any]]:
    """Check that the public repository layout is clean and intentional."""
    required = [
        "README.md",
        "README.zh-CN.md",
        "CITATION.cff",
        "pyproject.toml",
        "ucbs",
        "ucbs/certificate",
        "ucbs/verification",
        "scripts",
        "scripts/verify_certificate.py",
        "scripts/check_repository.py",
        "scripts/replay_certificate_chain.py",
        "scripts/replay_per_record_evidence.py",
        "scripts/replay_construction_audit.py",
        "scripts/replay_witness_construction.py",
        "scripts/replay_final_adjudication.py",
        "certificate/final_chain",
        "certificate/manifest",
        "certificate/public",
        "docs/artifact_policy.md",
        "docs/claim_scope.md",
        "docs/expected_outputs.md",
        "docs/reproducibility.md",
        "paper",
    ]
    forbidden = [
        "release",
        "scripts/stages",
        "ucbs/pipeline",
        "ucbs/target_083201",
        "ucbs/legacy_bs0832",
        "certificate/target_083201",
        "certificate/legacy_bs0832",
        "paper/source",
        "paper/preview",
        "scripts/verify_theorem_ready.py",
        "scripts/replay_inner_witness_certificate.py",
    ]
    rows: list[dict[str, Any]] = []
    for rel in required:
        exists = (root / rel).exists()
        rows.append({"check": "layout_required", "path": rel, "required": True, "exists": exists, "passed": exists})
    for rel in forbidden:
        exists = (root / rel).exists()
        if exists:
            rows.append({"check": "layout_forbidden", "path": rel, "forbidden": True, "exists": True, "passed": False})
    return rows


def check_empty_directories(root: Path) -> list[dict[str, Any]]:
    """Return unintended empty public directories."""
    skip_names = {".git", "__pycache__", ".pytest_cache"}
    rows: list[dict[str, Any]] = []
    for path in sorted(p for p in root.rglob("*") if p.is_dir()):
        rel = path.relative_to(root)
        if any(part in skip_names for part in rel.parts):
            continue
        if rel.parts and rel.parts[0] == "runs":
            continue
        if not any(path.iterdir()):
            rows.append({"check": "empty_directory", "path": rel.as_posix(), "passed": False, "summary": "empty directory found"})
    return rows


def check_english_only_comments(root: Path) -> list[dict[str, Any]]:
    """Return Python source lines that contain CJK characters."""
    rows: list[dict[str, Any]] = []
    for path in sorted([*root.glob("ucbs/**/*.py"), *root.glob("scripts/*.py")]):
        for idx, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            if any("\u4e00" <= ch <= "\u9fff" for ch in line):
                rows.append({
                    "check": "english_comments",
                    "file": str(path.relative_to(root)),
                    "line": idx,
                    "text": line.strip()[:160],
                    "passed": False,
                    "summary": "CJK character found in Python source",
                })
    return rows


def _collect_failed(diagnostics: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Collect rows whose ``passed`` field is false-like."""
    failed: list[dict[str, Any]] = []
    for name, rows in diagnostics.items():
        for row in rows:
            if "passed" in row and not _truthy(row["passed"]):
                failed.append({"diagnostic": name, **row})
    return failed


def run_repository_check(
    root: Path,
    artifact_root: str | None = None,
    per_record_evidence_zip: str | None = None,
    construction_audit_zip: str | None = None,
    witness_construction_zip: str | None = None,
    final_adjudication_zip: str | None = None,
    run_id: str = "repository_check",
    log_level: str = "INFO",
) -> RepositoryCheckResult:
    """Run public repository checks and create ``repository_check_feedback.zip``."""
    root = Path(root).resolve()
    run_dir = root / "runs" / run_id
    if run_dir.exists():
        shutil.rmtree(run_dir)
    for sub in ["diagnostics", "status", "log", "report"]:
        (run_dir / sub).mkdir(parents=True, exist_ok=True)
    log = run_dir / "log" / "repository_check.log"
    log.write_text(
        "repository check started " + datetime.now(timezone.utc).isoformat() + "\n"
        "root=<repository-root>\n"
        f"run_id={run_id}\n"
        f"log_level={log_level}\n",
        encoding="utf-8",
    )

    diagnostics: dict[str, list[dict[str, Any]]] = {}
    _append_log(log, "checking Python source compilation")
    diagnostics["python_compile"] = _with_summary("python_compile", check_python_compile(root), "Python sources compile", "Python source compilation failed")

    _append_log(log, "checking pyproject package metadata")
    diagnostics["pyproject"] = _with_summary("pyproject", check_pyproject_config(root), "pyproject package metadata is consistent", "pyproject package metadata failed")

    _append_log(log, "checking repository layout")
    diagnostics["layout"] = _with_summary("layout", check_layout(root), "repository layout is clean", "repository layout issue found")

    _append_log(log, "checking empty directories")
    diagnostics["empty_directories"] = _with_summary("empty_directories", check_empty_directories(root), "no unintended empty directory found", "empty directory issue found")

    _append_log(log, "checking English-only Python comments and docstrings")
    diagnostics["english_comments"] = _with_summary("english_comments", check_english_only_comments(root), "no CJK characters found in Python sources checked", "CJK characters found in Python sources checked")

    _append_log(log, "checking clean public narrative")
    diagnostics["narrative_lint"] = _with_summary("narrative_lint", check_narrative_lint(root), "public narrative is clean", "forbidden clean-story wording found")

    _append_log(log, "checking public Markdown math rendering fragments")
    diagnostics["readme_math"] = _with_summary("readme_math", check_markdown_math(root), "no markdown math lint issue found", "markdown math lint issue found")

    _append_log(log, "checking public claim boundary")
    diagnostics["claim_boundary"] = _with_summary("claim_boundary", check_claim_boundary(root), "no forbidden public-claim pattern found", "forbidden public-claim pattern found")

    _append_log(log, "checking certificate-chain artifact hashes")
    diagnostics["artifact_hashes"] = _with_summary("artifact_hashes", verify_key_artifact_hashes(root), "certificate-chain artifact hashes passed", "artifact hash issue found")

    _append_log(log, "running certificate verification as part of repository check")
    theorem = verify_certificate(
        root=root,
        artifact_root=artifact_root,
        per_record_evidence_zip=per_record_evidence_zip,
        construction_audit_zip=construction_audit_zip,
        witness_construction_zip=witness_construction_zip,
        final_adjudication_zip=final_adjudication_zip,
        run_id="certificate_verification",
        log_level=log_level,
    )
    diagnostics["certificate_verification"] = _with_summary(
        "certificate_verification",
        [{"check": "certificate_verification", "passed": theorem.status == "passed", "feedback": _rel(theorem.output_feedback, root)}],
        "certificate verification passed",
        "certificate verification failed",
    )

    for name, rows in diagnostics.items():
        _write_csv(run_dir / "diagnostics" / f"{name}.csv", rows)

    failed = _collect_failed(diagnostics)
    status = "passed" if not failed else "failed"
    feedback = run_dir / "repository_check_feedback.zip"
    summary = {
        "schema": "ucbs-public-repository-check-v5",
        "status": status,
        "failed_step_count": len(failed),
        "run_id": run_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "certificate_verification_feedback": _rel(theorem.output_feedback, root),
        "repository_check_feedback": _rel(feedback, root),
    }
    _write_json(run_dir / "status" / "repository_check.status.json", summary)
    _write_json(run_dir / "summary.json", summary)

    if failed:
        _write_csv(run_dir / "diagnostics" / "failed_checks.csv", failed)
        _append_log(log, f"repository check failed with {len(failed)} failed diagnostic rows")
    else:
        _write_csv(run_dir / "diagnostics" / "failed_checks.csv", [_summary_row("failed_checks", True, 0, "no failed repository diagnostic row found")])
        _append_log(log, "repository check passed")

    (run_dir / "report" / "repository_check.md").write_text(
        "# Repository check\n\n"
        f"Status: `{status}`.\n\n"
        f"Failed diagnostic rows: `{len(failed)}`.\n\n"
        "This check covers Python compilation, package metadata, repository layout, "
        "empty directories, clean public narrative, public Markdown math, claim boundaries, "
        "certificate-chain artifact hashes, and the final certificate verification.\n",
        encoding="utf-8",
    )

    with zipfile.ZipFile(feedback, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(run_dir.rglob("*")):
            if path.is_file() and path != feedback:
                archive.write(path, path.relative_to(run_dir).as_posix())
    return RepositoryCheckResult(status=status, failed_step_count=len(failed), feedback=feedback)
