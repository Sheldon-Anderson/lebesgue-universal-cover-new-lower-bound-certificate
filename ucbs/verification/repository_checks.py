"""Repository-level checks for the public certified lower-bound package."""
from __future__ import annotations

import ast
import shutil
import tomllib
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ucbs.cli.logging import close_run_log, log_to_file, start_run_log
from ucbs.config.repository_policy import (
    ALLOWED_RAW_STAGE_FILES,
    FORBIDDEN_BYTECODE_DIRECTORY_NAMES,
    FORBIDDEN_BYTECODE_SUFFIXES,
    FORBIDDEN_GENERATED_FILE_SUFFIXES,
    FORBIDDEN_REPOSITORY_PATHS,
    PUBLIC_SANITIZATION_PATTERNS,
    RAW_STAGE_PATTERN,
    REQUIRED_REPOSITORY_PATHS,
    TEXT_FILE_NAMES_REQUIRING_FINAL_NEWLINE,
    TEXT_FILE_SUFFIXES_REQUIRING_FINAL_NEWLINE,
)
from ucbs.verification.archive_mirror import check_archive_public_mirror
from ucbs.verification.artifact_checks import verify_key_artifact_hashes
from ucbs.verification.claim_boundary import check_claim_boundary
from ucbs.verification.diagnostics import (
    collect_failed,
    with_summary,
    write_csv,
    write_json,
)
from ucbs.verification.markdown_math import check_markdown_math
from ucbs.verification.narrative_lint import check_narrative_lint
from ucbs.verification.paper_claim_boundary import check_paper_claim_boundary
from ucbs.verification.release_consistency import check_release_consistency
from ucbs.certificate.chain_replay import verify_certificate


@dataclass(frozen=True)
class RepositoryCheckResult:
    """Outcome of the public repository check."""

    status: str
    failed_step_count: int
    feedback: Path


def _append_log(log_path: Path, message: str, level: str = "INFO") -> None:
    """Append one English repository-check log line with loguru."""
    log_to_file(log_path, message, level=level)



def _rel(path: Path, root: Path) -> str:
    """Return a repository-relative path when possible."""
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return f"<external>/{path.name}"


def check_bytecode_artifacts(root: Path) -> list[dict[str, Any]]:
    """Return compiled Python artifacts that must not ship in the release.

    Public release archives should contain source files and certificate records,
    not interpreter-generated caches. The check deliberately covers both cache
    directories and compiled-extension suffixes so repository checks catch these
    artifacts before packaging.
    """
    rows: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        rel = _rel(path, root)
        if path.is_dir() and path.name in FORBIDDEN_BYTECODE_DIRECTORY_NAMES:
            rows.append({
                "check": "bytecode_artifact",
                "path": rel,
                "passed": False,
                "summary": "compiled Python cache directory must not be included",
            })
        elif path.is_file() and path.suffix in FORBIDDEN_BYTECODE_SUFFIXES:
            rows.append({
                "check": "bytecode_artifact",
                "path": rel,
                "passed": False,
                "summary": "compiled Python artifact must not be included",
            })
    return rows


def _is_release_tree_file(path: Path, root: Path) -> bool:
    """Return whether a path belongs to the packaged release tree."""
    try:
        rel = path.relative_to(root)
    except ValueError:
        return False
    return bool(rel.parts) and rel.parts[0] not in {".git", "runs", ".pytest_cache"}


def check_generated_build_artifacts(root: Path) -> list[dict[str, Any]]:
    """Return LaTeX or build-generated files that must not ship."""
    rows: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or not _is_release_tree_file(path, root):
            continue
        rel = _rel(path, root)
        if any(rel.endswith(suffix) for suffix in FORBIDDEN_GENERATED_FILE_SUFFIXES):
            rows.append({
                "check": "generated_build_artifact",
                "path": rel,
                "passed": False,
                "summary": "generated build or LaTeX artifact must not be included",
            })
    return rows


def check_text_file_final_newlines(root: Path) -> list[dict[str, Any]]:
    """Return text files that do not end with a final newline."""
    rows: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or not _is_release_tree_file(path, root):
            continue
        if path.suffix not in TEXT_FILE_SUFFIXES_REQUIRING_FINAL_NEWLINE and path.name not in TEXT_FILE_NAMES_REQUIRING_FINAL_NEWLINE:
            continue
        data = path.read_bytes()
        if data and not data.endswith(b"\n"):
            rows.append({
                "check": "text_file_final_newline",
                "path": _rel(path, root),
                "passed": False,
                "summary": "text file must end with a newline",
            })
    return rows


def check_python_compile(root: Path) -> list[dict[str, Any]]:
    """Compile public Python sources in memory without writing cache files.

    The check intentionally uses Python's built-in ``compile`` rather than
    ``py_compile`` because ``py_compile`` writes ``.pyc`` files by design. A
    release audit should validate syntax and bytecode generation while leaving
    the source tree bytecode-free.
    """
    files = sorted([*root.glob("ucbs/**/*.py"), *root.glob("scripts/*.py"), *root.glob("tests/*.py")])
    if not files:
        return [{"check": "python_compile", "passed": False, "file_count": 0, "output": "no Python files found"}]
    failures: list[str] = []
    for path in files:
        rel = _rel(path, root)
        try:
            compile(path.read_text(encoding="utf-8"), rel, "exec")
        except SyntaxError as exc:
            failures.append(f"{rel}:{exc.lineno or 0}: {exc.msg}")
    return [{
        "check": "python_compile",
        "passed": not failures,
        "file_count": len(files),
        "output": "\n".join(failures)[-2000:],
    }]



def check_script_entry_points(root: Path) -> list[dict[str, Any]]:
    """Check public script wrappers and the direct-run bootstrap helper.

    ``scripts/_bootstrap.py`` is the only public script allowed to mutate
    ``sys.path``. It supports direct source-tree commands such as
    ``python scripts/verify_certificate.py`` before editable installation.
    All other scripts must delegate to ``ucbs.cli`` entry points.
    """
    rows: list[dict[str, Any]] = []
    scripts = sorted(root.glob("scripts/*.py"))
    for path in scripts:
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        is_bootstrap = rel == "scripts/_bootstrap.py"
        rows.append(
            {
                "check": "script_sys_path_policy",
                "path": rel,
                "passed": ("sys.path.insert" not in text) or is_bootstrap,
                "summary": "only scripts/_bootstrap.py may mutate sys.path",
            }
        )
        rows.append(
            {
                "check": "script_imports_ucbs_cli",
                "path": rel,
                "passed": is_bootstrap or "from ucbs.cli." in text,
                "summary": (
                    "bootstrap helper is exempt from ucbs.cli delegation"
                    if is_bootstrap
                    else "script delegates to ucbs.cli entry point"
                ),
            }
        )
    return rows or [
        {
            "check": "script_entry_points",
            "passed": False,
            "path": "scripts",
            "summary": "no public scripts found",
        }
    ]


def check_pyproject_config(root: Path) -> list[dict[str, Any]]:
    """Check parsed packaging metadata for the public ``ucbs`` package."""
    path = root / "pyproject.toml"
    if not path.exists():
        return [{"check": "pyproject_exists", "passed": False, "path": "pyproject.toml", "summary": "missing pyproject.toml"}]
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        return [
            {"check": "pyproject_exists", "passed": True, "path": "pyproject.toml", "summary": "pyproject.toml is present"},
            {"check": "pyproject_parse", "passed": False, "path": "pyproject.toml", "summary": f"pyproject.toml is invalid TOML: {exc}"},
        ]
    tool = data.get("tool", {}) if isinstance(data, dict) else {}
    setuptools = tool.get("setuptools", {}) if isinstance(tool, dict) else {}
    packages = setuptools.get("packages", {}) if isinstance(setuptools, dict) else {}
    find = packages.get("find", {}) if isinstance(packages, dict) else {}
    include = find.get("include", []) if isinstance(find, dict) else []
    scripts = data.get("project", {}).get("scripts", {}) if isinstance(data.get("project", {}), dict) else {}
    return [
        {"check": "pyproject_exists", "passed": True, "path": "pyproject.toml", "summary": "pyproject.toml is present"},
        {"check": "pyproject_parse", "passed": True, "path": "pyproject.toml", "summary": "pyproject.toml parses as TOML"},
        {"check": "pyproject_uses_ucbs_package", "passed": any(str(item).startswith("ucbs") for item in include), "path": "pyproject.toml", "summary": "package discovery includes ucbs"},
        {"check": "pyproject_no_stale_app_package", "passed": "app" not in {str(item) for item in include}, "path": "pyproject.toml", "summary": "stale app package is not referenced"},
        {"check": "pyproject_console_scripts", "passed": "ucbs-verify-certificate" in scripts, "path": "pyproject.toml", "summary": "console-script entry points are declared"},
        {"check": "pyproject_no_release_zip_entry", "passed": "ucbs-make-release-zip" not in scripts, "path": "pyproject.toml", "summary": "release-zip helper is not exposed as a console script"},
    ]



def check_layout(root: Path) -> list[dict[str, Any]]:
    """Check that the public repository layout is clean and intentional."""
    rows: list[dict[str, Any]] = []
    for rel in REQUIRED_REPOSITORY_PATHS:
        exists = (root / rel).exists()
        rows.append({"check": "layout_required", "path": rel, "required": True, "exists": exists, "passed": exists})
    for rel in FORBIDDEN_REPOSITORY_PATHS:
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
    for path in sorted([*root.glob("ucbs/**/*.py"), *root.glob("scripts/*.py"), *root.glob("tests/*.py")]):
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


def check_public_python_no_print(root: Path) -> list[dict[str, Any]]:
    """Return public Python source lines that call ``print`` directly.

    The check parses Python files with ``ast`` so comments, docstrings, and the
    implementation of this check are not mistaken for actual print calls.
    """
    rows: list[dict[str, Any]] = []
    files = sorted([*root.glob("ucbs/**/*.py"), *root.glob("scripts/*.py")])
    for path in files:
        rel = path.relative_to(root).as_posix()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        except SyntaxError as exc:
            rows.append(
                {
                    "check": "public_python_parse_for_print",
                    "file": rel,
                    "line": exc.lineno or 0,
                    "passed": False,
                    "summary": "Python source could not be parsed",
                }
            )
            continue
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "print"
            ):
                rows.append(
                    {
                        "check": "public_python_no_print",
                        "file": rel,
                        "line": getattr(node, "lineno", 0),
                        "passed": False,
                        "summary": "use ucbs.cli.output.emit_summary instead of print",
                    }
                )
    return rows


def check_raw_stage_label_policy(root: Path) -> list[dict[str, Any]]:
    """Return public Markdown locations with disallowed raw v133--v136 labels."""
    rows: list[dict[str, Any]] = []
    candidates = [root / "README.md", root / "README.zh-CN.md"]
    for folder in [root / "docs", root / "certificate" / "public"]:
        if folder.exists():
            candidates.extend(folder.rglob("*.md"))
    for path in sorted(path for path in candidates if path.exists()):
        rel = path.relative_to(root).as_posix()
        if rel in ALLOWED_RAW_STAGE_FILES:
            continue
        for idx, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(),
            start=1,
        ):
            if RAW_STAGE_PATTERN.search(line):
                rows.append(
                    {
                        "check": "raw_stage_label_policy",
                        "file": rel,
                        "line": idx,
                        "text": line.strip()[:160],
                        "passed": False,
                        "summary": "raw v133--v136 labels are allowed only in provenance docs",
                    }
                )
    return rows




def check_public_release_sanitization(root: Path) -> list[dict[str, Any]]:
    """Return machine-local traces left in public status or report files."""
    rows: list[dict[str, Any]] = []
    candidates: list[Path] = []
    for folder in [root / "certificate" / "public" / "status", root / "certificate" / "public" / "report"]:
        if folder.exists():
            candidates.extend(path for path in folder.rglob("*") if path.is_file())
    for path in sorted(candidates):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for pattern, issue in PUBLIC_SANITIZATION_PATTERNS:
                if pattern.search(line):
                    rows.append(
                        {
                            "check": "public_release_sanitization",
                            "file": rel,
                            "line": line_number,
                            "issue": issue,
                            "passed": False,
                            "summary": "machine-local public-release trace found",
                        }
                    )
    return rows



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
    start_run_log(
        log,
        [
            "repository check started",
            "root=<repository-root>",
            f"run_id={run_id}",
            f"log_level={log_level}",
        ],
        level=log_level,
    )

    diagnostics: dict[str, list[dict[str, Any]]] = {}
    _append_log(log, "checking for pre-existing Python bytecode artifacts", level=log_level)
    diagnostics["bytecode_artifacts_pre"] = with_summary(
        "bytecode_artifacts_pre",
        check_bytecode_artifacts(root),
        "no Python bytecode artifact found before compilation",
        "Python bytecode artifact found before compilation",
    )

    _append_log(log, "checking generated build artifacts", level=log_level)
    diagnostics["generated_build_artifacts"] = with_summary(
        "generated_build_artifacts",
        check_generated_build_artifacts(root),
        "no generated build artifact found",
        "generated build artifact found",
    )

    _append_log(log, "checking text-file final newlines", level=log_level)
    diagnostics["text_file_final_newlines"] = with_summary(
        "text_file_final_newlines",
        check_text_file_final_newlines(root),
        "all checked text files end with a newline",
        "text file missing final newline",
    )

    _append_log(log, "checking Python source compilation", level=log_level)
    diagnostics["python_compile"] = with_summary("python_compile", check_python_compile(root), "Python sources compile", "Python source compilation failed")

    _append_log(log, "checking for Python bytecode artifacts after compilation", level=log_level)
    diagnostics["bytecode_artifacts_post"] = with_summary(
        "bytecode_artifacts_post",
        check_bytecode_artifacts(root),
        "Python compilation left no bytecode artifact",
        "Python compilation left a bytecode artifact",
    )

    _append_log(log, "checking pyproject package metadata", level=log_level)
    diagnostics["pyproject"] = with_summary("pyproject", check_pyproject_config(root), "pyproject package metadata is consistent", "pyproject package metadata failed")

    _append_log(log, "checking release/version consistency", level=log_level)
    diagnostics["release_consistency"] = with_summary("release_consistency", check_release_consistency(root), "release metadata and README coverage are consistent", "release metadata or README coverage issue found")

    _append_log(log, "checking public script entry points", level=log_level)
    diagnostics["script_entry_points"] = with_summary("script_entry_points", check_script_entry_points(root), "public scripts delegate to package entry points", "public script entry-point issue found")

    _append_log(log, "checking repository layout", level=log_level)
    diagnostics["layout"] = with_summary("layout", check_layout(root), "repository layout is clean", "repository layout issue found")

    _append_log(log, "checking empty directories", level=log_level)
    diagnostics["empty_directories"] = with_summary("empty_directories", check_empty_directories(root), "no unintended empty directory found", "empty directory issue found")

    _append_log(log, "checking English-only Python comments and docstrings", level=log_level)
    diagnostics["english_comments"] = with_summary("english_comments", check_english_only_comments(root), "no CJK characters found in Python sources checked", "CJK characters found in Python sources checked")

    _append_log(log, "checking direct print calls in public Python code", level=log_level)
    diagnostics["public_python_no_print"] = with_summary("public_python_no_print", check_public_python_no_print(root), "public Python code does not call print directly", "public Python print call found")

    _append_log(log, "checking raw v13x provenance labels", level=log_level)
    diagnostics["raw_stage_label_policy"] = with_summary("raw_stage_label_policy", check_raw_stage_label_policy(root), "raw v13x labels appear only in provenance docs", "raw v13x label found outside allowed provenance docs")

    _append_log(log, "checking public status and report sanitization", level=log_level)
    diagnostics["public_release_sanitization"] = with_summary("public_release_sanitization", check_public_release_sanitization(root), "no machine-local public-release trace found", "machine-local public-release trace found")

    _append_log(log, "checking clean public narrative", level=log_level)
    diagnostics["narrative_lint"] = with_summary("narrative_lint", check_narrative_lint(root), "public narrative is clean", "forbidden clean-story wording found")

    _append_log(log, "checking public Markdown math rendering fragments", level=log_level)
    diagnostics["readme_math"] = with_summary("readme_math", check_markdown_math(root), "no markdown math lint issue found", "markdown math lint issue found")

    _append_log(log, "checking public claim boundary", level=log_level)
    diagnostics["claim_boundary"] = with_summary("claim_boundary", check_claim_boundary(root), "no forbidden public-claim pattern found", "forbidden public-claim pattern found")

    _append_log(log, "checking LaTeX paper claim boundary", level=log_level)
    diagnostics["paper_claim_boundary"] = with_summary("paper_claim_boundary", check_paper_claim_boundary(root), "paper claim boundary is clean", "paper claim-boundary issue found")


    _append_log(log, "checking certificate-chain artifact hashes", level=log_level)
    diagnostics["artifact_hashes"] = with_summary("artifact_hashes", verify_key_artifact_hashes(root), "certificate-chain artifact hashes passed", "artifact hash issue found")

    _append_log(log, "checking archive/public mirror consistency", level=log_level)
    diagnostics["archive_public_mirror"] = with_summary("archive_public_mirror", check_archive_public_mirror(root), "expanded public records match archive members", "archive/public mirror issue found")

    _append_log(log, "running certificate verification as part of repository check", level=log_level)
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
    diagnostics["certificate_verification"] = with_summary(
        "certificate_verification",
        [{"check": "certificate_verification", "passed": theorem.status == "passed", "feedback": _rel(theorem.output_feedback, root)}],
        "certificate verification passed",
        "certificate verification failed",
    )

    for name, rows in diagnostics.items():
        write_csv(run_dir / "diagnostics" / f"{name}.csv", rows)

    failed = collect_failed(diagnostics)
    status = "passed" if not failed else "failed"
    feedback = run_dir / "repository_check_feedback.zip"
    summary = {
        "schema": "ucbs-public-repository-check-v10",
        "status": status,
        "failed_step_count": len(failed),
        "run_id": run_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "certificate_verification_feedback": _rel(theorem.output_feedback, root),
        "repository_check_feedback": _rel(feedback, root),
    }
    write_json(run_dir / "status" / "repository_check.status.json", summary)
    write_json(run_dir / "summary.json", summary)

    if failed:
        write_csv(run_dir / "diagnostics" / "failed_checks.csv", failed)
        _append_log(log, f"repository check failed with {len(failed)} failed diagnostic rows", level=log_level)
    else:
        write_csv(run_dir / "diagnostics" / "failed_checks.csv", [{"check": "failed_checks_summary", "issue_count": 0, "passed": True, "summary": "no failed repository diagnostic row found"}])
        _append_log(log, "repository check passed", level=log_level)

    (run_dir / "report" / "repository_check.md").write_text(
        "# Repository check\n\n"
        f"Status: `{status}`.\n\n"
        f"Failed diagnostic rows: `{len(failed)}`.\n\n"
        "This check covers Python compilation, package metadata, release/version consistency, "
        "repository layout, bytecode-artifact exclusion, generated-artifact exclusion, final-newline hygiene, empty directories, "
        "clean public narrative, public Markdown math, claim boundaries, paper claim-boundary checks, "
        "certificate-chain artifact hashes, archive/public mirror consistency, and the final certificate verification.\n",
        encoding="utf-8",
    )

    close_run_log(log)
    with zipfile.ZipFile(feedback, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(run_dir.rglob("*")):
            if path.is_file() and path != feedback:
                archive.write(path, path.relative_to(run_dir).as_posix())
    return RepositoryCheckResult(status=status, failed_step_count=len(failed), feedback=feedback)
