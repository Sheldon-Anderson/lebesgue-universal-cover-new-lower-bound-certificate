"""Replay the construction-audit component of the certificate chain."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from ucbs.certificate.construction_audit import run_construction_audit_replay
from ucbs.verification.artifact_checks import DEFAULT_ARTIFACT_ROOT, DEFAULT_CONSTRUCTION_AUDIT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root. Defaults to the current directory.")
    parser.add_argument("--construction-audit-zip", default=None, help="Explicit construction-audit archive.")
    parser.add_argument("--run-id", default="construction_audit_replay", help="Output directory name under runs/.")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level label recorded in output logs.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.root).resolve()
    archive = args.construction_audit_zip or DEFAULT_ARTIFACT_ROOT / DEFAULT_CONSTRUCTION_AUDIT
    feedback = run_construction_audit_replay(root, archive, run_id=args.run_id, log_level=args.log_level)
    status_path = root / "runs" / args.run_id / "status" / "construction_audit_replay.status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    print(json.dumps({"status": status["status"], "construction_audit_passed": status.get("construction_audit_passed"), "feedback": str(feedback)}, indent=2))
    return 0 if status["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
