"""Public entry point for certificate verification."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from ucbs.certificate.chain_replay import verify_certificate


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root. Defaults to the current directory.")
    parser.add_argument("--artifact-root", default=None, help="Directory containing certificate-chain feedback archives.")
    parser.add_argument("--per-record-evidence-zip", default=None, help="Explicit per-record evidence feedback archive.")
    parser.add_argument("--construction-audit-zip", default=None, help="Explicit construction-audit feedback archive.")
    parser.add_argument("--witness-construction-zip", default=None, help="Explicit witness-construction feedback archive.")
    parser.add_argument("--final-adjudication-zip", default=None, help="Explicit final-adjudication feedback archive.")
    parser.add_argument("--run-id", default="certificate_verification", help="Output directory name under runs/.")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level label recorded in output logs.")
    return parser


def main() -> int:
    """Run certificate verification and return a process exit code."""
    args = build_parser().parse_args()
    result = verify_certificate(
        root=Path(args.root),
        artifact_root=args.artifact_root,
        per_record_evidence_zip=args.per_record_evidence_zip,
        construction_audit_zip=args.construction_audit_zip,
        witness_construction_zip=args.witness_construction_zip,
        final_adjudication_zip=args.final_adjudication_zip,
        run_id=args.run_id,
        log_level=args.log_level,
    )
    print(json.dumps({
        "status": result.status,
        "certificate_verified": result.certificate_verified,
        "threshold_proved": result.threshold_proved,
        "failed_component_count": result.failed_component_count,
        "feedback": str(result.output_feedback),
    }, indent=2))
    return 0 if result.certificate_verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
