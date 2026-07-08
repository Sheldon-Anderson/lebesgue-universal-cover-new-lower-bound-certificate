"""Replay checks for public per-record evidence records.

The public archive contains the frozen record inventory and final-replay-only
ledger. These checks verify schema, row counts, and per-row pass fields without
rerunning the original geometric search.
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
    check_row,
    require_columns,
    require_exact_count,
    require_unique_keys,
    truthy,
    write_component_outputs,
)
from ucbs.config.certificate_spec import (
    EXPECTED_FINAL_REPLAY_ROWS,
    EXPECTED_FROZEN_RECORDS,
    EXPECTED_INVENTORY_ROWS,
    INVENTORY_COLUMNS,
    FROZEN_RECORD_INVENTORY_MEMBER,
    FINAL_REPLAY_ONLY_LEDGER_MEMBER,
    PER_RECORD_REQUIRED_MEMBERS,
    REPLAY_COLUMNS,
)


def _int_field(row: dict[str, str], field: str) -> int:
    """Parse a nonnegative integer field from a CSV row.

    Missing or malformed values are treated as zero so the caller can report a
    deterministic aggregate-count failure instead of raising during diagnostic
    generation. The certificate check still fails whenever the aggregate count
    differs from the configured frozen-record count.
    """
    try:
        return int(str(row.get(field, "0") or "0"))
    except ValueError:
        return 0


def check_per_record_evidence(root: Path, archive: str | Path) -> ComponentReport:
    """Check the public per-record evidence archive."""
    path = resolve_archive(root, archive)
    checks = []
    if not path.exists():
        checks.append(check_row("archive_exists", False, relative_label(root, path), "archive is missing"))
        return ComponentReport("per_record_evidence", False, checks, {"per_record_evidence_passed": False})

    checks.append(check_row("archive_exists", True, relative_label(root, path), "archive is present"))
    member_rows = require_members(path, list(PER_RECORD_REQUIRED_MEMBERS))
    checks.extend(member_rows)
    if not all(truthy(row.get("passed")) for row in member_rows):
        return ComponentReport("per_record_evidence", False, checks, {"per_record_evidence_passed": False})

    inventory = read_csv_member(path, FROZEN_RECORD_INVENTORY_MEMBER)
    replay = read_csv_member(path, FINAL_REPLAY_ONLY_LEDGER_MEMBER)

    checks.extend(require_columns(inventory, INVENTORY_COLUMNS, "frozen_record_inventory"))
    checks.extend(require_columns(replay, REPLAY_COLUMNS, "final_replay_only_ledger"))
    checks.append(require_exact_count(inventory, EXPECTED_INVENTORY_ROWS, "frozen_record_inventory"))
    checks.append(require_exact_count(replay, EXPECTED_FINAL_REPLAY_ROWS, "final_replay_only_ledger"))
    checks.append(require_unique_keys(inventory, ["freeze_component", "final_adjudication_requirement", "freeze_route_kind"], "frozen_record_inventory"))
    checks.append(require_unique_keys(replay, ["replay_row"], "final_replay_only_ledger"))
    checks.append(require_unique_keys(replay, ["record_id"], "final_replay_only_ledger_records"))

    inventory_total = sum(_int_field(row, "rows") for row in inventory)
    checks.append(check_row("inventory_total_frozen_records", inventory_total == EXPECTED_FROZEN_RECORDS, inventory_total, "inventory row counts sum to the frozen certificate record count"))
    checks.append(check_row("final_replay_rows_pass", all(truthy(row.get("final_replay_pass")) for row in replay), len(replay), "all final-replay-only rows pass"))
    checks.append(check_row("final_replay_status", all(str(row.get("final_replay_status", "")).strip() == "pass_final_replay_only" for row in replay), len(replay), "all final-replay-only status fields are passing"))
    checks.append(check_row("final_replay_requirement", all(str(row.get("final_adjudication_requirement", "")).strip() == "final_replay_only" for row in replay), len(replay), "all rows have the final-replay-only requirement"))

    passed = not any(not truthy(row.get("passed")) for row in checks)
    return ComponentReport(
        "per_record_evidence",
        passed,
        checks,
        {
            "per_record_evidence_passed": passed,
            "inventory_rows": len(inventory),
            "frozen_records": inventory_total,
            "final_replay_rows": len(replay),
            "failed_rows": 0 if passed else sum(1 for row in replay if not truthy(row.get("final_replay_pass"))),
        },
    )


def run_per_record_evidence_replay(
    root: Path,
    archive: str | Path,
    run_id: str = "per_record_evidence_replay",
    log_level: str = "INFO",
) -> Path:
    """Run the per-record evidence replay and write a feedback archive."""
    report = check_per_record_evidence(root, archive)
    return write_component_outputs(
        root=root,
        run_id=run_id,
        log_name="per_record_evidence_replay.log",
        status_name="per_record_evidence_replay.status.json",
        feedback_name="per_record_evidence_replay_feedback.zip",
        report=report,
        archive_label=relative_label(root, resolve_archive(root, archive)),
        log_level=log_level,
    )
