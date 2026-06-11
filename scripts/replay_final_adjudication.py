"""Replay the final-adjudication component of the certificate chain."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from ucbs.certificate.final_adjudication import run_final_adjudication_replay
from ucbs.verification.artifact_checks import DEFAULT_ARTIFACT_ROOT, DEFAULT_FINAL_ADJUDICATION


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root. Defaults to the current directory.")
    parser.add_argument("--final-adjudication-zip", default=None, help="Explicit final-adjudication archive.")
    parser.add_argument("--run-id", default="final_adjudication_replay", help="Output directory name under runs/.")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level label recorded in output logs.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.root).resolve()
    archive = args.final_adjudication_zip or DEFAULT_ARTIFACT_ROOT / DEFAULT_FINAL_ADJUDICATION
    feedback = run_final_adjudication_replay(root, archive, run_id=args.run_id, log_level=args.log_level)
    status_path = root / "runs" / args.run_id / "status" / "final_adjudication_replay.status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    print(json.dumps({"status": status["status"], "threshold_proved": status.get("threshold_proved"), "feedback": str(feedback)}, indent=2))
    return 0 if status["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
