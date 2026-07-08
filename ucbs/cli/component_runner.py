"""Shared runner for certificate component replay command-line tools."""
from __future__ import annotations

import argparse
import json
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from ucbs.cli.common import add_log_level_argument, add_root_argument, add_run_id_argument
from ucbs.cli.output import emit_summary
from ucbs.config.certificate_spec import DEFAULT_ARTIFACT_ROOT

ReplayFunction = Callable[[Path, Path, str, str], Path]
"""Callable shape shared by component replay functions."""


def build_component_parser(
    *,
    description: str | None,
    archive_option: str,
    archive_help: str,
    default_run_id: str,
) -> argparse.ArgumentParser:
    """Build a parser for one certificate component replay command.

    Args:
        description: Command description shown in ``--help`` output.
        archive_option: Long option name for the component archive.
        archive_help: Help text for the archive option.
        default_run_id: Default output directory under ``runs/``.

    Returns:
        Configured argument parser with root, archive, run-id, and log-level
        options.
    """
    parser = argparse.ArgumentParser(description=description)
    add_root_argument(parser)
    parser.add_argument(archive_option, default=None, help=archive_help)
    add_run_id_argument(parser, default_run_id)
    add_log_level_argument(parser)
    return parser


def run_component_command(
    *,
    argv: Sequence[str] | None,
    description: str | None,
    archive_option: str,
    archive_default: str,
    archive_help: str,
    default_run_id: str,
    replay_function: ReplayFunction,
    status_filename: str,
    summary_keys: Sequence[str],
) -> int:
    """Run one component replay command and emit a compact JSON summary.

    Args:
        argv: Optional argument vector used by tests and direct callers.
        description: Command description from the wrapper module docstring.
        archive_option: Long option name for an explicit component archive.
        archive_default: Default archive filename under the artifact root.
        archive_help: Help text for the explicit archive option.
        default_run_id: Default output directory under ``runs/``.
        replay_function: Component replay function that writes diagnostics.
        status_filename: Status JSON filename written by the replay function.
        summary_keys: Status fields copied into the standard-output summary.

    Returns:
        Process exit code: zero when the component status is ``passed``.
    """
    parser = build_component_parser(
        description=description,
        archive_option=archive_option,
        archive_help=archive_help,
        default_run_id=default_run_id,
    )
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    attr_name = archive_option.lstrip("-").replace("-", "_")
    archive_arg = getattr(args, attr_name)
    archive = Path(archive_arg) if archive_arg else DEFAULT_ARTIFACT_ROOT / archive_default
    feedback = replay_function(root, archive, args.run_id, args.log_level)
    status_path = root / "runs" / args.run_id / "status" / status_filename
    status = json.loads(status_path.read_text(encoding="utf-8"))
    summary: dict[str, Any] = {"status": status["status"]}
    summary.update({key: status.get(key) for key in summary_keys})
    summary["feedback"] = str(feedback)
    emit_summary(summary)
    return 0 if status["status"] == "passed" else 1
