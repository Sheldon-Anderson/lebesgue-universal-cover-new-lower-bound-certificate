"""Replay the per-record evidence component of the certificate chain."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from ucbs.certificate.per_record_evidence import run_per_record_evidence_replay
from ucbs.verification.artifact_checks import DEFAULT_ARTIFACT_ROOT, DEFAULT_PER_RECORD_EVIDENCE


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root. Defaults to the current directory.")
    parser.add_argument("--per-record-evidence-zip", default=None, help="Explicit per-record evidence archive.")
    parser.add_argument("--run-id", default="per_record_evidence_replay", help="Output directory name under runs/.")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level label recorded in output logs.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.root).resolve()
    archive = args.per_record_evidence_zip or DEFAULT_ARTIFACT_ROOT / DEFAULT_PER_RECORD_EVIDENCE
    feedback = run_per_record_evidence_replay(root, archive, run_id=args.run_id, log_level=args.log_level)
    status_path = root / "runs" / args.run_id / "status" / "per_record_evidence_replay.status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    print(json.dumps({"status": status["status"], "failed_rows": status.get("failed_rows"), "feedback": str(feedback)}, indent=2))
    return 0 if status["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
