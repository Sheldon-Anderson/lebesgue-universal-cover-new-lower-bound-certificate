"""Replay the final adjudication component of the certificate chain."""
from __future__ import annotations

import argparse
from collections.abc import Sequence

from ucbs.certificate.final_adjudication import run_final_adjudication_replay
from ucbs.cli.component_runner import build_component_parser, run_component_command
from ucbs.config.certificate_spec import DEFAULT_FINAL_ADJUDICATION

# Long command-line option for overriding the bundled final-adjudication archive.
_ARCHIVE_OPTION = "--final-adjudication-zip"
# Default run directory used by the final adjudication replay command.
_DEFAULT_RUN_ID = "final_adjudication_replay"
# Status JSON filename written by the final adjudication replay command.
_STATUS_FILENAME = "final_adjudication_replay.status.json"


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for this component replay."""
    return build_component_parser(
        description=__doc__,
        archive_option=_ARCHIVE_OPTION,
        archive_help="Explicit final-adjudication archive.",
        default_run_id=_DEFAULT_RUN_ID,
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the final adjudication replay command."""
    return run_component_command(
        argv=argv,
        description=__doc__,
        archive_option=_ARCHIVE_OPTION,
        archive_default=DEFAULT_FINAL_ADJUDICATION,
        archive_help="Explicit final-adjudication archive.",
        default_run_id=_DEFAULT_RUN_ID,
        replay_function=run_final_adjudication_replay,
        status_filename=_STATUS_FILENAME,
        summary_keys=("threshold_proved",),
    )


if __name__ == "__main__":
    raise SystemExit(main())
