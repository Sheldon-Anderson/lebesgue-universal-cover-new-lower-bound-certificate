"""Replay the construction audit component of the certificate chain."""
from __future__ import annotations

import argparse
from collections.abc import Sequence

from ucbs.certificate.construction_audit import run_construction_audit_replay
from ucbs.cli.component_runner import build_component_parser, run_component_command
from ucbs.config.certificate_spec import DEFAULT_CONSTRUCTION_AUDIT

# Long command-line option for overriding the bundled construction-audit archive.
_ARCHIVE_OPTION = "--construction-audit-zip"
# Default run directory used by the construction audit replay command.
_DEFAULT_RUN_ID = "construction_audit_replay"
# Status JSON filename written by the construction audit replay command.
_STATUS_FILENAME = "construction_audit_replay.status.json"


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for this component replay."""
    return build_component_parser(
        description=__doc__,
        archive_option=_ARCHIVE_OPTION,
        archive_help="Explicit construction-audit archive.",
        default_run_id=_DEFAULT_RUN_ID,
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the construction audit replay command."""
    return run_component_command(
        argv=argv,
        description=__doc__,
        archive_option=_ARCHIVE_OPTION,
        archive_default=DEFAULT_CONSTRUCTION_AUDIT,
        archive_help="Explicit construction-audit archive.",
        default_run_id=_DEFAULT_RUN_ID,
        replay_function=run_construction_audit_replay,
        status_filename=_STATUS_FILENAME,
        summary_keys=("construction_audit_passed",),
    )


if __name__ == "__main__":
    raise SystemExit(main())
