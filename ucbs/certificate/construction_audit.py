"""Replay checks for public construction-audit records.

The public construction archive contains event-aware interval replay rows and
thin-extra replay rows. These checks verify that the bundled rows are present,
schema-conforming, numerically clear, and marked as passing.
"""
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
    CONSTRUCTION_REQUIRED_MEMBERS,
    EVENT_AWARE_INTERVAL_MEMBER,
    EVENT_COLUMNS,
    EXPECTED_EVENT_ROWS,
    EXPECTED_THIN_ROWS,
    THIN_COLUMNS,
    THIN_EXTRA_MEMBER,
)


def check_construction_audit(root: Path, archive: str | Path) -> ComponentReport:
    """Check construction-audit records from the public archive."""
    path = resolve_archive(root, archive)
    checks = []
    if not path.exists():
        checks.append(check_row("archive_exists", False, relative_label(root, path), "archive is missing"))
        return ComponentReport("construction_audit", False, checks, {"construction_audit_passed": False})

    checks.append(check_row("archive_exists", True, relative_label(root, path), "archive is present"))
    member_rows = require_members(path, list(CONSTRUCTION_REQUIRED_MEMBERS))
    checks.extend(member_rows)
    if not all(truthy(row.get("passed")) for row in member_rows):
        return ComponentReport("construction_audit", False, checks, {"construction_audit_passed": False})

    event_rows = read_csv_member(path, EVENT_AWARE_INTERVAL_MEMBER)
    thin_rows = read_csv_member(path, THIN_EXTRA_MEMBER)

    checks.extend(require_columns(event_rows, EVENT_COLUMNS, "event_aware_interval_rows"))
    checks.extend(require_columns(thin_rows, THIN_COLUMNS, "thin_extra_rows"))
    checks.append(require_exact_count(event_rows, EXPECTED_EVENT_ROWS, "event_aware_interval_rows"))
    checks.append(require_exact_count(thin_rows, EXPECTED_THIN_ROWS, "thin_extra_rows"))
    checks.append(require_unique_keys(event_rows, ["adjudication_row"], "event_aware_interval_rows"))
    checks.append(require_unique_keys(thin_rows, ["adjudication_row"], "thin_extra_rows"))
    checks.append(require_unique_keys(thin_rows, ["record_id"], "thin_extra_records"))

    checks.append(check_row("event_adjudication_pass", all_pass(event_rows, "adjudication_pass"), len(event_rows), "all event-aware rows pass"))
    checks.append(check_row("event_numeric_clearance", all_pass(event_rows, "numeric_clearance_ok"), len(event_rows), "all event-aware rows clear the numeric tests"))
    checks.append(check_row("event_route_status", all_pass(event_rows, "route_status_ok"), len(event_rows), "all event-aware route status rows pass"))
    checks.append(check_row("event_positive_surplus", has_numeric_surplus(event_rows) and all(positive_decimal(row.get("min_surplus")) for row in event_rows), len(event_rows), "all non-empty event-aware surplus values are positive"))
    checks.append(check_row("thin_adjudication_pass", all_pass(thin_rows, "adjudication_pass"), len(thin_rows), "all thin-extra rows pass"))
    checks.append(check_row("thin_numeric_clearance", all_pass(thin_rows, "numeric_clearance_ok"), len(thin_rows), "all thin-extra rows clear the numeric tests"))
    checks.append(check_row("thin_extra_retained", all_pass(thin_rows, "extra_split_retained"), len(thin_rows), "all thin-extra rows are retained"))
    checks.append(check_row("thin_positive_surplus", has_numeric_surplus(thin_rows) and all(positive_decimal(row.get("min_surplus")) for row in thin_rows), len(thin_rows), "all thin-extra surplus values are positive"))

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
