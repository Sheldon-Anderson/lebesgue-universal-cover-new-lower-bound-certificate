"""Replay checks for witness-construction records in the certificate chain."""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from ucbs.certificate.archive_io import read_csv_member, read_json_member, relative_label, require_members, resolve_archive
from ucbs.certificate.validation import CERTIFIED_THRESHOLD, ComponentReport, check_row, threshold_cleared, truthy, write_component_outputs

REQUIRED_MEMBERS = [
    "diagnostics/v135_point_in_source_object_certificate.csv",
    "diagnostics/v135_orientation_determinant_ledger.csv",
    "diagnostics/v135_interval_shoelace_area_certificate.csv",
    "diagnostics/v135_inner_polygon_area_lower_bound_summary.csv",
    "diagnostics/v135_witness_convex_order_audit.csv",
    "diagnostics/v135_operation_level_arb_rounding_ledger.csv",
    "status/v135.status.json",
]


def _accepted_shoelace_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if str(row.get("subbox_status", "")).strip().lower() == "passed"]


def _positive_decimal(value: str) -> bool:
    try:
        return Decimal(str(value)) > Decimal("0")
    except Exception:
        return False


def check_witness_construction(root: Path, archive: str | Path) -> ComponentReport:
    """Check witness-construction records from the archive."""
    path = resolve_archive(root, archive)
    checks = []
    if not path.exists():
        checks.append(check_row("archive_exists", False, relative_label(root, path), "archive is missing"))
        return ComponentReport("witness_construction", False, checks, {"witness_construction_passed": False})

    checks.append(check_row("archive_exists", True, relative_label(root, path), "archive is present"))
    member_rows = require_members(path, REQUIRED_MEMBERS)
    checks.extend(member_rows)
    if not all(truthy(row.get("passed")) for row in member_rows):
        return ComponentReport("witness_construction", False, checks, {"witness_construction_passed": False})

    status = read_json_member(path, "status/v135.status.json")
    point_rows = read_csv_member(path, "diagnostics/v135_point_in_source_object_certificate.csv")
    orientation_rows = read_csv_member(path, "diagnostics/v135_orientation_determinant_ledger.csv")
    shoelace_rows = read_csv_member(path, "diagnostics/v135_interval_shoelace_area_certificate.csv")
    summary_rows = read_csv_member(path, "diagnostics/v135_inner_polygon_area_lower_bound_summary.csv")
    order_rows = read_csv_member(path, "diagnostics/v135_witness_convex_order_audit.csv")
    rounding_rows = read_csv_member(path, "diagnostics/v135_operation_level_arb_rounding_ledger.csv")

    summary_global = summary_rows[0] if summary_rows else {}
    patch_rows = [row for row in summary_rows[1:] if row.get("patch_record_id")]
    accepted_rows = _accepted_shoelace_rows(shoelace_rows)
    accepted_subboxes = {row.get("subbox_id", "") for row in accepted_rows}
    accepted_orientation = [row for row in orientation_rows if row.get("subbox_id") in accepted_subboxes]
    accepted_points = [row for row in point_rows if row.get("subbox_id") in accepted_subboxes]

    checks.append(check_row("summary_global_passed", truthy(summary_global.get("inner_polygon_kernel_passed")), summary_global.get("inner_polygon_kernel_status"), "global witness summary is passed"))
    checks.append(check_row("witness_domain_count", len(patch_rows) == 16, len(patch_rows), "sixteen witness domains are summarized"))
    checks.append(check_row("witness_domains_passed", all(truthy(row.get("inner_polygon_patch_passed")) and str(row.get("patch_status", "")).lower() == "passed" for row in patch_rows), len(patch_rows), "all witness-domain summaries pass"))
    checks.append(check_row("witness_domain_failed_counts_zero", all(str(row.get("failed_subbox_count", "0")) == "0" for row in patch_rows), sum(int(row.get("failed_subbox_count", "0") or 0) for row in patch_rows), "witness-domain summaries record zero final failed subdomains"))
    checks.append(check_row("accepted_terminal_subdomains_present", len(accepted_rows) == 140, len(accepted_rows), "accepted terminal subdomains match the certificate summary"))
    checks.append(check_row("accepted_shoelace_bounds_clear_threshold", all(threshold_cleared(row.get("shoelace_area_lower_bound"), CERTIFIED_THRESHOLD) for row in accepted_rows), len(accepted_rows), "all accepted shoelace lower bounds clear the threshold"))
    checks.append(check_row("accepted_orientation_positive", all(_positive_decimal(row.get("min_orientation_lower", "")) for row in accepted_rows), len(accepted_rows), "all accepted terminal subdomains have positive orientation lower bounds"))
    checks.append(check_row("accepted_convex_order_certified", all(truthy(row.get("convex_order_certified")) for row in accepted_rows), len(accepted_rows), "all accepted terminal subdomains have a certified cyclic order"))
    checks.append(check_row("accepted_subbox_flags_passed", all(truthy(row.get("inner_polygon_subbox_passed")) for row in accepted_rows), len(accepted_rows), "all accepted terminal subdomain flags pass"))
    checks.append(check_row("accepted_orientation_rows_passed", all(str(row.get("orientation_status", "")).lower() == "passed" for row in accepted_orientation), len(accepted_orientation), "orientation rows for accepted terminal subdomains pass"))
    checks.append(check_row("point_containment_passed", all(str(row.get("point_in_source_object_status", "")).startswith("passed") for row in accepted_points), len(accepted_points), "point-containment rows for accepted terminal subdomains pass"))
    checks.append(check_row("order_audit_rows_passed", all(truthy(row.get("inner_polygon_patch_passed")) and str(row.get("patch_status", "")).lower() == "passed" for row in order_rows), len(order_rows), "witness cyclic-order audit rows pass"))
    checks.append(check_row("rounding_rows_present", len(rounding_rows) == 128, len(rounding_rows), "operation-level rounding rows are present"))
    checks.append(check_row("rounding_rows_certified", all(str(row.get("arb_status", "")).lower() == "available" and str(row.get("proof_status", "")).lower() == "proof_grade_operation_row" for row in rounding_rows), len(rounding_rows), "operation-level rounding rows are proof-grade rows"))
    checks.append(check_row("status_success", str(status.get("status", "")).strip().lower() == "success_gate_passed_for_final_adjudication", status.get("status"), "status records success for final adjudication"))
    checks.append(check_row("status_witness_certificate_passed", truthy(status.get("explicit_inner_witness_certificate_passed")), status.get("explicit_inner_witness_certificate_passed"), "status records accepted witness certificate"))
    status_failed_value = status.get("terminal_failed_subbox_count", status.get("inner_polygon_failed_patch_count", ""))
    checks.append(check_row("status_terminal_failed_zero", str(status_failed_value) == "0", status_failed_value, "status records zero final failed witness domains or terminal subdomains"))

    passed = not any(not truthy(row.get("passed")) for row in checks)
    details = {
        "witness_construction_passed": passed,
        "witness_domains": len(patch_rows),
        "accepted_terminal_subdomains": len(accepted_rows),
        "failed_terminal_subdomains": sum(int(row.get("failed_subbox_count", "0") or 0) for row in patch_rows),
        "point_containment_passed": all(str(row.get("point_in_source_object_status", "")).startswith("passed") for row in accepted_points),
        "orientation_certificates_passed": all(str(row.get("orientation_status", "")).lower() == "passed" for row in accepted_orientation),
        "shoelace_lower_bounds_passed": all(threshold_cleared(row.get("shoelace_area_lower_bound"), CERTIFIED_THRESHOLD) for row in accepted_rows),
        "intermediate_split_rows_ignored_as_nonterminal": len(shoelace_rows) - len(accepted_rows),
    }
    return ComponentReport("witness_construction", passed, checks, details)


def run_witness_construction_replay(
    root: Path,
    archive: str | Path,
    run_id: str = "witness_construction_replay",
    log_level: str = "INFO",
) -> Path:
    """Run witness-construction replay and write a feedback archive."""
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
