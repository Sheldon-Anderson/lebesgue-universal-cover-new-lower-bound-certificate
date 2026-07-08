"""Replay checks for public witness/source reconstruction records."""
from __future__ import annotations

from pathlib import Path

from ucbs.certificate.archive_io import (
    read_csv_member,
    relative_label,
    require_members,
    resolve_archive,
)
from ucbs.certificate.validation import (
    ComponentReport,
    all_pass,
    check_row,
    has_numeric_surplus,
    positive_decimal,
    require_columns,
    require_exact_count,
    require_unique_keys,
    truthy,
    write_component_outputs,
)
from ucbs.config.certificate_spec import (
    EXPECTED_WITNESS_SOURCE_ROWS,
    WITNESS_COLUMNS,
    WITNESS_SOURCE_MEMBER,
    WITNESS_REQUIRED_MEMBERS,
)


def check_witness_construction(root: Path, archive: str | Path) -> ComponentReport:
    """Check witness/source reconstruction records from the public archive."""
    path = resolve_archive(root, archive)
    checks = []
    if not path.exists():
        checks.append(check_row("archive_exists", False, relative_label(root, path), "archive is missing"))
        return ComponentReport("witness_construction", False, checks, {"witness_construction_passed": False})

    checks.append(check_row("archive_exists", True, relative_label(root, path), "archive is present"))
    member_rows = require_members(path, list(WITNESS_REQUIRED_MEMBERS))
    checks.extend(member_rows)
    if not all(truthy(row.get("passed")) for row in member_rows):
        return ComponentReport("witness_construction", False, checks, {"witness_construction_passed": False})

    rows = read_csv_member(path, WITNESS_SOURCE_MEMBER)

    checks.extend(require_columns(rows, WITNESS_COLUMNS, "witness_source_rows"))
    checks.append(require_exact_count(rows, EXPECTED_WITNESS_SOURCE_ROWS, "witness_source_rows"))
    checks.append(require_unique_keys(rows, ["adjudication_row"], "witness_source_rows"))
    checks.append(check_row("witness_source_adjudication_pass", all_pass(rows, "adjudication_pass"), len(rows), "all witness/source rows pass"))
    checks.append(check_row("witness_source_seed_present", all_pass(rows, "has_witness_or_source_seed"), len(rows), "all witness/source rows have a seed"))
    checks.append(check_row("witness_source_numeric_clearance", all_pass(rows, "numeric_clearance_ok"), len(rows), "all witness/source rows clear the numeric tests"))
    checks.append(check_row("witness_source_route_status", all_pass(rows, "route_status_ok"), len(rows), "all witness/source route status rows pass"))
    checks.append(check_row("witness_source_positive_surplus", has_numeric_surplus(rows) and all(positive_decimal(row.get("min_surplus")) for row in rows), len(rows), "all non-empty witness/source surplus values are positive"))

    passed = not any(not truthy(row.get("passed")) for row in checks)
    return ComponentReport(
        "witness_construction",
        passed,
        checks,
        {
            "witness_construction_passed": passed,
            "witness_source_rows": len(rows),
        },
    )


def run_witness_construction_replay(
    root: Path,
    archive: str | Path,
    run_id: str = "witness_construction_replay",
    log_level: str = "INFO",
) -> Path:
    """Run witness/source replay and write a feedback archive."""
    report = check_witness_construction(root, archive)
    return write_component_outputs(
        root=root,
        run_id=run_id,
        log_name="witness_construction_replay.log",
        status_name="witness_construction_replay.status.json",
        feedback_name="witness_construction_replay_feedback.zip",
        report=report,
        archive_label=relative_label(root, resolve_archive(root, archive)),
        log_level=log_level,
    )
