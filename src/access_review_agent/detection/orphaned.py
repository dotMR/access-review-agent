"""Orphaned access detection: plain Python, no model call.

Deterministic per eval-cases.md's Tier 1 classification - an anti-join
plus a status check. No LLM adds reliability here; it can only add cost,
latency, and run-to-run variance for a category that has none of those
problems in the first place. See ADR-0006 for the fuller reasoning: the
model is reserved for categories that genuinely need it (Milestone 6
onward), not used uniformly across every category regardless of whether
reasoning is actually involved.
"""

from pathlib import Path
from typing import Any

from access_review_agent.tools.access_data import read_and_validate as read_access_data
from access_review_agent.tools.hris import read_and_validate as read_hris


def detect_orphaned(data_dir: Path, system_name: str = "aws") -> dict[str, Any]:
    """Detect Orphaned access for one system against fixture/production data
    in data_dir. Returns a findings dict matching the shared Finding shape
    (SPEC.md §4's Issue format).
    """
    access_rows = read_access_data(data_dir / f"access_{system_name}.csv", system_name)
    hris_rows = read_hris(data_dir / "system_hr.csv")
    terminated_ids = {r["employee_id"] for r in hris_rows if r["status"] == "terminated"}

    findings = [
        {
            "category": "orphaned",
            "system_name": system_name,
            "employee_id": row["employee_id"],
            "source_record": {
                "file": f"access_{system_name}.csv",
                "employee_id": row["employee_id"],
            },
        }
        for row in access_rows
        if row["status"] == "active" and row["employee_id"] in terminated_ids
    ]
    return {"findings": findings}
