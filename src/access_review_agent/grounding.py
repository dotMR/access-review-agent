"""Grounding/citation guardrail: independently re-verify a claimed finding.

Per SPEC.md §7 — a validation step confirms a claimed finding's source
record actually exists with the claimed properties, before that finding
is trusted. Trusts nothing about what happened during the model's own
tool calls; re-reads the source data itself, the same way a real
reviewer re-checks a source rather than trusting "I already looked."

Built once here, used twice: Milestone 1's runner rejects hallucinated
findings with it; Milestone 2 reuses it unchanged as the gate in front
of open_issue.
"""

from pathlib import Path
from typing import Any

from access_review_agent.tools.access_data import read_and_validate as read_access_data
from access_review_agent.tools.hris import read_and_validate as read_hris


class GroundingError(Exception):
    """Raised when a claimed finding does not hold up against source data."""


def validate_finding(finding: dict[str, Any], data_dir: Path) -> None:
    """Raise GroundingError if `finding` isn't actually supported by the
    source data in data_dir. Returns None (no exception) if grounded.
    """
    category = finding.get("category")
    system_name = finding.get("system_name")
    employee_id = finding.get("employee_id")

    if not system_name or not employee_id:
        raise GroundingError(
            f"Finding missing system_name or employee_id: {finding}"
        )

    if category != "orphaned":
        raise GroundingError(
            f"No grounding check implemented for category={category!r} yet"
        )

    access_rows = read_access_data(data_dir / f"access_{system_name}.csv", system_name)
    hris_rows = read_hris(data_dir / "system_hr.csv")

    access_row = next((r for r in access_rows if r["employee_id"] == employee_id), None)
    if access_row is None:
        raise GroundingError(
            f"No access record for employee_id={employee_id!r} in "
            f"access_{system_name}.csv — finding not grounded"
        )
    if access_row["status"] != "active":
        raise GroundingError(
            f"Access record for {employee_id!r} has status={access_row['status']!r}, "
            "not 'active' — Orphaned requires currently-active access"
        )

    hris_row = next((r for r in hris_rows if r["employee_id"] == employee_id), None)
    if hris_row is None:
        raise GroundingError(
            f"No HRIS record for employee_id={employee_id!r} — finding not grounded"
        )
    if hris_row["status"] != "terminated":
        raise GroundingError(
            f"HRIS record for {employee_id!r} has status={hris_row['status']!r}, "
            "not 'terminated' — Orphaned requires HRIS status=terminated"
        )
