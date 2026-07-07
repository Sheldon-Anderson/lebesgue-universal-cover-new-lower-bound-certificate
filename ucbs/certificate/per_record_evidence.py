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

REQUIRED_MEMBERS = [
    "data/frozen_record_inventory.csv",
    "data/final_replay_only_ledger.csv",
]

INVENTORY_COLUMNS = {
    "freeze_component",
    "final_adjudication_requirement",
    "freeze_route_kind",
    "freeze_route_status",
    "rows",
}
REPLAY_COLUMNS = {
    "replay_row",
    "component",
    "root_box_id",
    "record_id",
    "final_adjudication_requirement",
    "freeze_route_kind",
    "freeze_route_status",
    "final_replay_status",
    "final_replay_pass",
}

EXPECTED_INVENTORY_ROWS = 13
EXPECTED_FROZEN_RECORDS = 3411
EXPECTED_FINAL_REPLAY_ROWS = 2790


def _int_field(row: dict[str, str], field: str) -> int:
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
    member_rows = require_members(path, REQUIRED_MEMBERS)
    checks.extend(member_rows)
    if not all(truthy(row.get("passed")) for row in member_rows):
        return ComponentReport("per_record_evidence", False, checks, {"per_record_evidence_passed": False})

    inventory = read_csv_member(path, "data/frozen_record_inventory.csv")
    replay = read_csv_member(path, "data/final_replay_only_ledger.csv")

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
