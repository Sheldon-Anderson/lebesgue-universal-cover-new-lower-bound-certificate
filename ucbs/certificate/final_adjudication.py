"""Replay checks for public final verification records."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from ucbs.certificate.archive_io import (
    read_csv_member,
    read_json_member,
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
    "status/certificate_status.json",
    "status/final_adjudication.status.json",
    "status/theorem_ready_gate.status.json",
    "status/claim_freeze.status.json",
    "data/final_adjudication_ledger.csv",
    "data/final_aggregation_gate.csv",
    "data/final_blocker_matrix.csv",
]

LEDGER_COLUMNS = {
    "adjudication_class",
    "component",
    "record_id",
    "requirement",
    "status",
    "pass",
    "failure_reason",
    "proof_boundary",
}
AGGREGATION_COLUMNS = {"gate", "passed", "details"}

EXPECTED_LEDGER_ROWS = 3411
EXPECTED_AGGREGATION_ROWS = 7
EXPECTED_CLASS_COUNTS = {
    "FINAL_REPLAY_ONLY": 2790,
    "EVENT_AWARE": 493,
    "WITNESS_SOURCE": 117,
    "P1_THIN": 11,
}


def _all_pass(rows: list[dict[str, str]], field: str) -> bool:
    return bool(rows) and all(truthy(row.get(field)) for row in rows)


def check_final_adjudication(root: Path, archive: str | Path) -> ComponentReport:
    """Check final verification records from the public archive."""
    path = resolve_archive(root, archive)
    checks = []
    if not path.exists():
        checks.append(check_row("archive_exists", False, relative_label(root, path), "archive is missing"))
        return ComponentReport("final_adjudication", False, checks, {"final_adjudication_passed": False})

    checks.append(check_row("archive_exists", True, relative_label(root, path), "archive is present"))
    member_rows = require_members(path, REQUIRED_MEMBERS)
    checks.extend(member_rows)
    if not all(truthy(row.get("passed")) for row in member_rows):
        return ComponentReport("final_adjudication", False, checks, {"final_adjudication_passed": False})

    certificate_status = read_json_member(path, "status/certificate_status.json")
    final_status = read_json_member(path, "status/final_adjudication.status.json")
    theorem_gate = read_json_member(path, "status/theorem_ready_gate.status.json")
    claim_freeze = read_json_member(path, "status/claim_freeze.status.json")
    ledger = read_csv_member(path, "data/final_adjudication_ledger.csv")
    aggregation = read_csv_member(path, "data/final_aggregation_gate.csv")
    blockers = read_csv_member(path, "data/final_blocker_matrix.csv")

    checks.extend(require_columns(ledger, LEDGER_COLUMNS, "final_adjudication_ledger"))
    checks.extend(require_columns(aggregation, AGGREGATION_COLUMNS, "final_aggregation_gate"))
    checks.append(require_exact_count(ledger, EXPECTED_LEDGER_ROWS, "final_adjudication_ledger"))
    checks.append(require_exact_count(aggregation, EXPECTED_AGGREGATION_ROWS, "final_aggregation_gate"))
    checks.append(require_exact_count(blockers, 0, "final_blocker_matrix"))
    checks.append(require_unique_keys(aggregation, ["gate"], "final_aggregation_gate"))

    class_counts = Counter(row.get("adjudication_class", "") for row in ledger)
    checks.append(check_row("ledger_class_counts", dict(class_counts) == EXPECTED_CLASS_COUNTS, dict(class_counts), "ledger class counts match the public certificate summary"))
    checks.append(check_row("ledger_rows_pass", _all_pass(ledger, "pass"), len(ledger), "all final ledger rows pass"))
    checks.append(check_row("ledger_no_failure_reason", all(not str(row.get("failure_reason", "")).strip() for row in ledger), len(ledger), "ledger rows have no failure reasons"))
    checks.append(check_row("aggregation_rows_pass", _all_pass(aggregation, "passed"), len(aggregation), "all final aggregation gates pass"))

    for name, status in [
        ("certificate_status", certificate_status),
        ("final_status", final_status),
        ("theorem_gate", theorem_gate),
        ("claim_freeze", claim_freeze),
    ]:
        checks.append(check_row(f"{name}_target", str(status.get("target")) == "0.833", status.get("target"), f"{name} records the certified target"))

    checks.append(check_row("certificate_status_final_aggregation", truthy(certificate_status.get("final_aggregation_passed")), certificate_status.get("final_aggregation_passed"), "certificate status records final aggregation"))
    checks.append(check_row("certificate_status_blockers_zero", str(certificate_status.get("proof_grade_blocker_rows", "")) == "0", certificate_status.get("proof_grade_blocker_rows"), "certificate status records zero proof-grade blockers"))
    checks.append(check_row("certificate_status_claim_boundary", truthy(certificate_status.get("claim_boundary_ok")), certificate_status.get("claim_boundary_ok"), "certificate status records the claim boundary"))
    checks.append(check_row("certificate_status_theorem_ready", truthy(certificate_status.get("theorem_ready")), certificate_status.get("theorem_ready"), "certificate status records the final gate"))
    checks.append(check_row("final_status_final_aggregation", truthy(final_status.get("final_aggregation_passed")), final_status.get("final_aggregation_passed"), "final status records final aggregation"))
    checks.append(check_row("final_status_blockers_zero", str(final_status.get("proof_grade_blocker_rows", "")) == "0", final_status.get("proof_grade_blocker_rows"), "final status records zero proof-grade blockers"))
    checks.append(check_row("theorem_gate_passed", truthy(theorem_gate.get("theorem_ready")), theorem_gate.get("theorem_ready"), "the final gate records success"))
    checks.append(check_row("theorem_gate_claim_boundary", truthy(theorem_gate.get("claim_boundary_ok")), theorem_gate.get("claim_boundary_ok"), "the final gate records a clean claim boundary"))
    checks.append(check_row("theorem_gate_final_blocker_count", str(theorem_gate.get("final_blocker_count", "")) == "0", theorem_gate.get("final_blocker_count"), "the final gate records zero blockers"))
    checks.append(check_row("claim_freeze_claim_boundary", truthy(claim_freeze.get("claim_boundary_ok")), claim_freeze.get("claim_boundary_ok"), "claim-freeze status records the claim boundary"))
    checks.append(check_row("nonconvex_not_claimed", not truthy(claim_freeze.get("nonconvex_claim")) and not truthy(theorem_gate.get("nonconvex_claim")), "", "public statuses do not claim a nonconvex theorem"))
    checks.append(check_row("proof_assistant_not_claimed", not truthy(claim_freeze.get("proof_assistant_formalization_claim")) and not truthy(theorem_gate.get("proof_assistant_formalization_claim")), "", "public statuses do not claim proof-assistant formalization"))
    checks.append(check_row("external_not_claimed", not truthy(claim_freeze.get("external_independent_verification_claim")) and not truthy(theorem_gate.get("external_independent_verification_claim")), "", "public statuses do not claim external independent verification"))

    passed = not any(not truthy(row.get("passed")) for row in checks)
    details = {
        "final_adjudication_passed": passed,
        "certificate_verified": passed,
        "threshold_proved": passed and truthy(theorem_gate.get("theorem_ready")),
        "proof_obligations_discharged": passed,
        "nonconvex_lower_bound_claimed": False,
        "proof_assistant_formalization_completed": False,
        "independent_external_verification_completed": False,
    }
    return ComponentReport("final_adjudication", passed, checks, details)


def run_final_adjudication_replay(
    root: Path,
    archive: str | Path,
    run_id: str = "final_adjudication_replay",
    log_level: str = "INFO",
) -> Path:
    """Run final verification replay and write a feedback archive."""
    report = check_final_adjudication(root, archive)
    return write_component_outputs(
        root=root,
        run_id=run_id,
        log_name="final_adjudication_replay.log",
        status_name="final_adjudication_replay.status.json",
        feedback_name="final_adjudication_replay_feedback.zip",
        report=report,
        archive_label=relative_label(root, resolve_archive(root, archive)),
        log_level=log_level,
    )
