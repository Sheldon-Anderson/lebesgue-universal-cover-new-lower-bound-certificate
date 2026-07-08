"""Replay the witness construction component of the certificate chain."""
from __future__ import annotations

import argparse
from collections.abc import Sequence

from ucbs.certificate.witness_construction import run_witness_construction_replay
from ucbs.cli.component_runner import build_component_parser, run_component_command
from ucbs.config.certificate_spec import DEFAULT_WITNESS_CONSTRUCTION

# Long command-line option for overriding the bundled witness-construction archive.
_ARCHIVE_OPTION = "--witness-construction-zip"
# Default run directory used by the witness construction replay command.
_DEFAULT_RUN_ID = "witness_construction_replay"
# Status JSON filename written by the witness construction replay command.
_STATUS_FILENAME = "witness_construction_replay.status.json"


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for this component replay."""
    return build_component_parser(
        description=__doc__,
        archive_option=_ARCHIVE_OPTION,
        archive_help="Explicit witness-construction archive.",
        default_run_id=_DEFAULT_RUN_ID,
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the witness construction replay command."""
    return run_component_command(
        argv=argv,
        description=__doc__,
        archive_option=_ARCHIVE_OPTION,
        archive_default=DEFAULT_WITNESS_CONSTRUCTION,
        archive_help="Explicit witness-construction archive.",
        default_run_id=_DEFAULT_RUN_ID,
        replay_function=run_witness_construction_replay,
        status_filename=_STATUS_FILENAME,
        summary_keys=("witness_construction_passed",),
    )


if __name__ == "__main__":
    raise SystemExit(main())
