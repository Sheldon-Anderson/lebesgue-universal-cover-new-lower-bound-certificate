"""Replay checks for public construction-audit records.

The public construction archive contains event-aware interval replay rows and
thin-extra replay rows. These checks verify that the bundled rows are present,
schema-conforming, numerically clear, and marked as passing.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from pathlib import Path

from ucbs.certificate.archive_io import (
    read_csv_member,
    relative_label,
    require_members,
    resolve_archive,
)
from ucbs.certificate.validation import (
    ComponentReport,
    check_row,
    require_columns,
    require_exact_count,
    require_unique_keys,
    truthy,
    write_component_outputs,
)

REQUIRED_MEMBERS = [
    "data/event_aware_interval_replay_adjudication.csv",
    "data/p1_thin_extra_replay_adjudication.csv",
]

EVENT_COLUMNS = {
    "adjudication_row",
    "component",
    "requirement",
    "root_box_id",
    "record_id",
    "freeze_route_kind",
    "freeze_route_status",
    "min_surplus",
    "numeric_clearance_ok",
    "route_status_ok",
    "adjudication_status",
    "adjudication_pass",
    "proof_boundary",
}
THIN_COLUMNS = {
    "adjudication_row",
    "component",
    "requirement",
    "root_box_id",
    "record_id",
    "freeze_route_kind",
    "freeze_route_status",
    "min_surplus",
    "extra_split_retained",
    "numeric_clearance_ok",
    "adjudication_status",
    "adjudication_pass",
    "proof_boundary",
}

EXPECTED_EVENT_ROWS = 493
EXPECTED_THIN_ROWS = 11


def _positive_decimal(value: object) -> bool:
    text = str(value).strip()
    if not text:
        return True
    try:
        return Decimal(text) > Decimal("0")
    except (InvalidOperation, ValueError):
        return False


def _has_numeric_surplus(rows: list[dict[str, str]]) -> bool:
    return any(str(row.get("min_surplus", "")).strip() for row in rows)


def _all_pass(rows: list[dict[str, str]], field: str) -> bool:
    return bool(rows) and all(truthy(row.get(field)) for row in rows)


def check_construction_audit(root: Path, archive: str | Path) -> ComponentReport:
    """Check construction-audit records from the public archive."""
    path = resolve_archive(root, archive)
    checks = []
    if not path.exists():
        checks.append(check_row("archive_exists", False, relative_label(root, path), "archive is missing"))
        return ComponentReport("construction_audit", False, checks, {"construction_audit_passed": False})

    checks.append(check_row("archive_exists", True, relative_label(root, path), "archive is present"))
    member_rows = require_members(path, REQUIRED_MEMBERS)
    checks.extend(member_rows)
    if not all(truthy(row.get("passed")) for row in member_rows):
        return ComponentReport("construction_audit", False, checks, {"construction_audit_passed": False})

    event_rows = read_csv_member(path, "data/event_aware_interval_replay_adjudication.csv")
    thin_rows = read_csv_member(path, "data/p1_thin_extra_replay_adjudication.csv")

    checks.extend(require_columns(event_rows, EVENT_COLUMNS, "event_aware_interval_rows"))
    checks.extend(require_columns(thin_rows, THIN_COLUMNS, "thin_extra_rows"))
    checks.append(require_exact_count(event_rows, EXPECTED_EVENT_ROWS, "event_aware_interval_rows"))
    checks.append(require_exact_count(thin_rows, EXPECTED_THIN_ROWS, "thin_extra_rows"))
    checks.append(require_unique_keys(event_rows, ["adjudication_row"], "event_aware_interval_rows"))
    checks.append(require_unique_keys(thin_rows, ["adjudication_row"], "thin_extra_rows"))
    checks.append(require_unique_keys(thin_rows, ["record_id"], "thin_extra_records"))

    checks.append(check_row("event_adjudication_pass", _all_pass(event_rows, "adjudication_pass"), len(event_rows), "all event-aware rows pass"))
    checks.append(check_row("event_numeric_clearance", _all_pass(event_rows, "numeric_clearance_ok"), len(event_rows), "all event-aware rows clear the numeric tests"))
    checks.append(check_row("event_route_status", _all_pass(event_rows, "route_status_ok"), len(event_rows), "all event-aware route status rows pass"))
    checks.append(check_row("event_positive_surplus", _has_numeric_surplus(event_rows) and all(_positive_decimal(row.get("min_surplus")) for row in event_rows), len(event_rows), "all non-empty event-aware surplus values are positive"))
    checks.append(check_row("thin_adjudication_pass", _all_pass(thin_rows, "adjudication_pass"), len(thin_rows), "all thin-extra rows pass"))
    checks.append(check_row("thin_numeric_clearance", _all_pass(thin_rows, "numeric_clearance_ok"), len(thin_rows), "all thin-extra rows clear the numeric tests"))
    checks.append(check_row("thin_extra_retained", _all_pass(thin_rows, "extra_split_retained"), len(thin_rows), "all thin-extra rows are retained"))
    checks.append(check_row("thin_positive_surplus", _has_numeric_surplus(thin_rows) and all(_positive_decimal(row.get("min_surplus")) for row in thin_rows), len(thin_rows), "all thin-extra surplus values are positive"))

    passed = not any(not truthy(row.get("passed")) for row in checks)
    return ComponentReport(
        "construction_audit",
        passed,
        checks,
        {
            "construction_audit_passed": passed,
            "event_aware_interval_rows": len(event_rows),
            "thin_extra_rows": len(thin_rows),
        },
    )


def run_construction_audit_replay(
    root: Path,
    archive: str | Path,
    run_id: str = "construction_audit_replay",
    log_level: str = "INFO",
) -> Path:
    """Run construction-audit replay and write a feedback archive."""
    report = check_construction_audit(root, archive)
    return write_component_outputs(
        root=root,
        run_id=run_id,
        log_name="construction_audit_replay.log",
        status_name="construction_audit_replay.status.json",
        feedback_name="construction_audit_replay_feedback.zip",
        report=report,
        archive_label=relative_label(root, resolve_archive(root, archive)),
        log_level=log_level,
    )
