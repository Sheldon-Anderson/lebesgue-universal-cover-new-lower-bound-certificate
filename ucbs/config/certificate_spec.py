"""Certificate-record schemas, counts, member paths, and default artifact paths.

The values in this module describe the frozen public certificate format. They
are deliberately separated from replay logic so changes to the certificate
profile are reviewed as configuration changes rather than hidden code changes.
"""
from __future__ import annotations

from pathlib import Path


DEFAULT_ARTIFACT_ROOT = Path("certificate") / "final_chain"
"""Default directory containing the four public certificate-chain archives."""

DEFAULT_PER_RECORD_EVIDENCE = "per_record_evidence_feedback.zip"
"""Default per-record evidence feedback archive name."""

DEFAULT_CONSTRUCTION_AUDIT = "construction_audit_feedback.zip"
"""Default construction-audit feedback archive name."""

DEFAULT_WITNESS_CONSTRUCTION = "witness_construction_feedback.zip"
"""Default witness-construction feedback archive name."""

DEFAULT_FINAL_ADJUDICATION = "final_adjudication_feedback.zip"
"""Default final-adjudication feedback archive name."""

DEFAULT_MANIFEST = Path("certificate") / "manifest" / "key_artifacts_sha256.txt"
"""Default SHA256 manifest for theorem-relevant public artifacts."""

PUBLIC_CERTIFICATE_ROOT = Path("certificate") / "public"
"""Default directory containing expanded public copies of certificate records."""

FROZEN_RECORD_INVENTORY_MEMBER = "data/frozen_record_inventory.csv"
"""Archive member storing the frozen-record inventory."""

FINAL_REPLAY_ONLY_LEDGER_MEMBER = "data/final_replay_only_ledger.csv"
"""Archive member storing final-replay-only ledger rows."""

EVENT_AWARE_INTERVAL_MEMBER = "data/event_aware_interval_replay_adjudication.csv"
"""Archive member storing event-aware interval replay rows."""

THIN_EXTRA_MEMBER = "data/p1_thin_extra_replay_adjudication.csv"
"""Archive member storing retained thin-extra replay rows."""

WITNESS_SOURCE_MEMBER = "data/witness_source_reconstruction_adjudication.csv"
"""Archive member storing witness/source reconstruction rows."""

CERTIFICATE_STATUS_MEMBER = "status/certificate_status.json"
"""Archive member storing the certificate status JSON record."""

FINAL_STATUS_MEMBER = "status/final_adjudication.status.json"
"""Archive member storing the final-adjudication status JSON record."""

THEOREM_GATE_MEMBER = "status/theorem_ready_gate.status.json"
"""Archive member storing the final theorem gate JSON record."""

CLAIM_FREEZE_MEMBER = "status/claim_freeze.status.json"
"""Archive member storing the claim-freeze status JSON record."""

FINAL_LEDGER_MEMBER = "data/final_adjudication_ledger.csv"
"""Archive member storing the final-adjudication ledger."""

FINAL_AGGREGATION_GATE_MEMBER = "data/final_aggregation_gate.csv"
"""Archive member storing final aggregation gates."""

FINAL_BLOCKER_MATRIX_MEMBER = "data/final_blocker_matrix.csv"
"""Archive member storing unresolved final blockers."""

PER_RECORD_REQUIRED_MEMBERS = (
    FROZEN_RECORD_INVENTORY_MEMBER,
    FINAL_REPLAY_ONLY_LEDGER_MEMBER,
)
"""Required members of the per-record evidence archive."""

CONSTRUCTION_REQUIRED_MEMBERS = (
    EVENT_AWARE_INTERVAL_MEMBER,
    THIN_EXTRA_MEMBER,
)
"""Required members of the construction-audit archive."""

WITNESS_REQUIRED_MEMBERS = (
    WITNESS_SOURCE_MEMBER,
)
"""Required members of the witness/source reconstruction archive."""

FINAL_REQUIRED_MEMBERS = (
    CERTIFICATE_STATUS_MEMBER,
    FINAL_STATUS_MEMBER,
    THEOREM_GATE_MEMBER,
    CLAIM_FREEZE_MEMBER,
    FINAL_LEDGER_MEMBER,
    FINAL_AGGREGATION_GATE_MEMBER,
    FINAL_BLOCKER_MATRIX_MEMBER,
)
"""Required members of the final-adjudication archive."""

ARCHIVE_PUBLIC_MIRROR_MAP = (
    (DEFAULT_PER_RECORD_EVIDENCE, FROZEN_RECORD_INVENTORY_MEMBER, PUBLIC_CERTIFICATE_ROOT / FROZEN_RECORD_INVENTORY_MEMBER),
    (DEFAULT_PER_RECORD_EVIDENCE, FINAL_REPLAY_ONLY_LEDGER_MEMBER, PUBLIC_CERTIFICATE_ROOT / FINAL_REPLAY_ONLY_LEDGER_MEMBER),
    (DEFAULT_CONSTRUCTION_AUDIT, EVENT_AWARE_INTERVAL_MEMBER, PUBLIC_CERTIFICATE_ROOT / EVENT_AWARE_INTERVAL_MEMBER),
    (DEFAULT_CONSTRUCTION_AUDIT, THIN_EXTRA_MEMBER, PUBLIC_CERTIFICATE_ROOT / THIN_EXTRA_MEMBER),
    (DEFAULT_WITNESS_CONSTRUCTION, WITNESS_SOURCE_MEMBER, PUBLIC_CERTIFICATE_ROOT / WITNESS_SOURCE_MEMBER),
    (DEFAULT_FINAL_ADJUDICATION, CERTIFICATE_STATUS_MEMBER, PUBLIC_CERTIFICATE_ROOT / CERTIFICATE_STATUS_MEMBER),
    (DEFAULT_FINAL_ADJUDICATION, FINAL_STATUS_MEMBER, PUBLIC_CERTIFICATE_ROOT / FINAL_STATUS_MEMBER),
    (DEFAULT_FINAL_ADJUDICATION, THEOREM_GATE_MEMBER, PUBLIC_CERTIFICATE_ROOT / THEOREM_GATE_MEMBER),
    (DEFAULT_FINAL_ADJUDICATION, CLAIM_FREEZE_MEMBER, PUBLIC_CERTIFICATE_ROOT / CLAIM_FREEZE_MEMBER),
    (DEFAULT_FINAL_ADJUDICATION, FINAL_LEDGER_MEMBER, PUBLIC_CERTIFICATE_ROOT / FINAL_LEDGER_MEMBER),
    (DEFAULT_FINAL_ADJUDICATION, FINAL_AGGREGATION_GATE_MEMBER, PUBLIC_CERTIFICATE_ROOT / FINAL_AGGREGATION_GATE_MEMBER),
    (DEFAULT_FINAL_ADJUDICATION, FINAL_BLOCKER_MATRIX_MEMBER, PUBLIC_CERTIFICATE_ROOT / FINAL_BLOCKER_MATRIX_MEMBER),
)
"""Archive-to-public-file byte-for-byte mirror checks for expanded records."""

INVENTORY_COLUMNS = frozenset({
    "freeze_component",
    "final_adjudication_requirement",
    "freeze_route_kind",
    "freeze_route_status",
    "rows",
})
"""Required columns for the frozen-record inventory."""

REPLAY_COLUMNS = frozenset({
    "replay_row",
    "component",
    "root_box_id",
    "record_id",
    "final_adjudication_requirement",
    "freeze_route_kind",
    "freeze_route_status",
    "final_replay_status",
    "final_replay_pass",
})
"""Required columns for final-replay-only rows."""

EVENT_COLUMNS = frozenset({
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
})
"""Required columns for event-aware interval replay rows."""

THIN_COLUMNS = frozenset({
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
})
"""Required columns for retained thin-extra replay rows."""

WITNESS_COLUMNS = frozenset({
    "adjudication_row",
    "component",
    "requirement",
    "root_box_id",
    "record_id",
    "freeze_route_kind",
    "freeze_route_status",
    "has_witness_or_source_seed",
    "min_surplus",
    "numeric_clearance_ok",
    "route_status_ok",
    "adjudication_status",
    "adjudication_pass",
    "proof_boundary",
})
"""Required columns for witness/source reconstruction rows."""

LEDGER_COLUMNS = frozenset({
    "adjudication_class",
    "component",
    "record_id",
    "requirement",
    "status",
    "pass",
    "failure_reason",
    "proof_boundary",
})
"""Required columns for the final-adjudication ledger."""

AGGREGATION_COLUMNS = frozenset({"gate", "passed", "details"})
"""Required columns for final aggregation-gate records."""

EXPECTED_INVENTORY_ROWS = 13
"""Expected number of frozen-inventory summary rows."""

EXPECTED_FROZEN_RECORDS = 3411
"""Expected number of frozen certificate records."""

EXPECTED_FINAL_REPLAY_ROWS = 2790
"""Expected number of final-replay-only records."""

EXPECTED_EVENT_ROWS = 493
"""Expected number of event-aware interval records."""

EXPECTED_THIN_ROWS = 11
"""Expected number of retained thin-extra records."""

EXPECTED_WITNESS_SOURCE_ROWS = 117
"""Expected number of witness/source reconstruction records."""

EXPECTED_LEDGER_ROWS = 3411
"""Expected number of rows in the final-adjudication ledger."""

EXPECTED_AGGREGATION_ROWS = 7
"""Expected number of final aggregation gates."""

EXPECTED_FINAL_BLOCKERS = 0
"""Expected number of unresolved final blocker rows."""

EXPECTED_CLASS_COUNTS = {
    "FINAL_REPLAY_ONLY": EXPECTED_FINAL_REPLAY_ROWS,
    "EVENT_AWARE": EXPECTED_EVENT_ROWS,
    "WITNESS_SOURCE": EXPECTED_WITNESS_SOURCE_ROWS,
    "P1_THIN": EXPECTED_THIN_ROWS,
}
"""Expected final-ledger class counts by adjudication class."""

CERTIFICATE_COUNTS = {
    "parameter_domains": "356,816",
    "directed_interval_records": "41,261",
    "tensor_records": "8,751",
    "bridge_records": "282",
    "witness_domains": "16",
    "frozen_certificate_records": "3,411",
    "final_replay_records": "2,790",
    "event_aware_interval_records": "493",
    "witness_source_records": "117",
    "thin_extra_records": "11",
    "final_blockers": "0",
}
"""Paper-facing certificate counts used by release-consistency tests."""

PAPER_TABLE_COUNT_ROWS = {
    "parameter domains": "356,816",
    "directed interval records": "41,261",
    "tensor records": "8,751",
    "bridge records": "282",
    "witness domains": "16",
    "frozen certificate records": "3,411",
    "final-replay records": "2,790",
    "event-aware interval records": "493",
    "witness/source records": "117",
    "thin extra records": "11",
    "final blockers": "0",
    "accepted terminal subdomains": "140",
    "unresolved terminal subdomains": "0",
    "witness point incidences": "2,112",
    "point-containment certificates": "2,112 / 2,112",
    "minimum witness-domain area bound": "0.8642876791",
    "minimum excess over tau": "0.0312876791",
    "minimum orientation determinant lower endpoint": r"3.6637\times10^{-5}",
}
"""Row-label/value pairs that must appear in the LaTeX certificate tables."""
