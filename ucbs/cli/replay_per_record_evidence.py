"""Replay the per-record evidence component of the certificate chain."""
from __future__ import annotations

import argparse
from collections.abc import Sequence

from ucbs.certificate.per_record_evidence import run_per_record_evidence_replay
from ucbs.cli.component_runner import build_component_parser, run_component_command
from ucbs.config.certificate_spec import DEFAULT_PER_RECORD_EVIDENCE

# Long command-line option for overriding the bundled per-record evidence archive.
_ARCHIVE_OPTION = "--per-record-evidence-zip"
# Default run directory used by the per-record evidence replay command.
_DEFAULT_RUN_ID = "per_record_evidence_replay"
# Status JSON filename written by the per-record evidence replay command.
_STATUS_FILENAME = "per_record_evidence_replay.status.json"


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for this component replay."""
    return build_component_parser(
        description=__doc__,
        archive_option=_ARCHIVE_OPTION,
        archive_help="Explicit per-record evidence archive.",
        default_run_id=_DEFAULT_RUN_ID,
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the per-record evidence replay command."""
    return run_component_command(
        argv=argv,
        description=__doc__,
        archive_option=_ARCHIVE_OPTION,
        archive_default=DEFAULT_PER_RECORD_EVIDENCE,
        archive_help="Explicit per-record evidence archive.",
        default_run_id=_DEFAULT_RUN_ID,
        replay_function=run_per_record_evidence_replay,
        status_filename=_STATUS_FILENAME,
        summary_keys=("failed_rows",),
    )


if __name__ == "__main__":
    raise SystemExit(main())
