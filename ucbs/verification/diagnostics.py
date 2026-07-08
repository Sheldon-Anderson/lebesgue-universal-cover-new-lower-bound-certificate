"""Shared diagnostic helpers for replay and repository-audit modules."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable

DiagnosticRow = dict[str, Any]
"""One diagnostic row written to a CSV file."""


def check_row(
    check: str,
    passed: bool,
    value: Any = "",
    summary: str = "",
    **extra: Any,
) -> DiagnosticRow:
    """Build one diagnostic row for replay and repository-check tables."""
    row: DiagnosticRow = {"check": check, "passed": bool(passed), "value": value, "summary": summary}
    row.update(extra)
    return row


def truthy(value: Any) -> bool:
    """Interpret common serialized Boolean and status values.

    The certificate ledgers encode pass/fail information as strings, booleans,
    and a small number of status labels. Centralizing the interpretation keeps
    certificate replay and repository-level diagnostics consistent.
    """
    if value is True:
        return True
    if value is False or value is None:
        return False
    return str(value).strip().lower() in {
        "true",
        "1",
        "yes",
        "passed",
        "pass",
        "ok",
        "closed",
        "discharged",
        "present",
        "present_locked",
        "empty",
        "clean",
        "success",
        "success_gate_passed_for_final_adjudication",
    }


def failed_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collect rows whose ``passed`` field is present and false-like."""
    failed: list[dict[str, Any]] = []
    for row in rows:
        if "passed" in row and not truthy(row["passed"]):
            failed.append(row)
    return failed


def summary_row(
    name: str,
    rows: Iterable[DiagnosticRow],
    ok: str,
    bad: str,
) -> DiagnosticRow:
    """Return a standard summary row for a diagnostic table."""
    failures = failed_rows(rows)
    return {
        "check": f"{name}_summary",
        "issue_count": len(failures),
        "passed": len(failures) == 0,
        "summary": ok if not failures else bad,
    }


def with_summary(name: str, rows: list[DiagnosticRow], ok: str, bad: str) -> list[DiagnosticRow]:
    """Append a standard summary row to diagnostic rows."""
    return [*rows, summary_row(name, rows, ok, bad)]


def write_csv(
    path: Path,
    rows: Iterable[DiagnosticRow],
    fieldnames: list[str] | None = None,
) -> None:
    """Write diagnostic rows to CSV with a deterministic header."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    fields: list[str] = list(fieldnames or [])
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    if not fields:
        fields = ["check", "issue_count", "passed", "summary"]
        rows = [{"check": "empty_summary", "issue_count": 0, "passed": True, "summary": "no rows produced"}]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write a JSON object with stable formatting and a final newline."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def collect_failed(diagnostics: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Collect failed diagnostic rows from a named diagnostic table mapping."""
    failed: list[dict[str, Any]] = []
    for name, rows in diagnostics.items():
        for row in failed_rows(rows):
            failed.append({"diagnostic": name, **row})
    return failed
