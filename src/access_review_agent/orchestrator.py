"""Main agent: the sole orchestrator and Issue-writer, per SPEC.md §3.

Constructs one SystemDetectionUnit per Information System and aggregates
each unit's already-detected findings — it never re-derives them by
combining raw per-system data against HRIS itself (SPEC.md §3). Then runs
open_issue (which itself gates on validate_finding, per ADR-0007) on
every finding. Units never call open_issue themselves; this module is the
only caller in the whole detection path, matching the tool registry's
"open_issue — held by: Main agent only."

Still manually/locally triggered here (Milestone 4) — GitHub Actions
dispatch arrives at Milestone 5.
"""

from pathlib import Path
from typing import Any

from access_review_agent.github.adapter import IssueResult
from access_review_agent.github.issues import open_issue
from access_review_agent.grounding import GroundingError
from access_review_agent.units import SYSTEMS, SystemDetectionUnit


def run_full_reconciliation(data_dir: Path, repo_full_name: str) -> dict[str, Any]:
    """Full reconciliation across all five systems and all Tier 1
    categories: detect, then open an Issue for every grounded finding.
    Returns a per-system summary (findings detected, Issues opened,
    findings rejected by the grounding gate) for inspection.
    """
    results: dict[str, Any] = {}
    for system_name in SYSTEMS:
        unit = SystemDetectionUnit(system_name, data_dir)
        findings = unit.detect_all()

        opened: list[IssueResult] = []
        rejected: list[dict[str, Any]] = []
        for finding in findings:
            try:
                opened.append(open_issue(finding, repo_full_name, data_dir))
            except GroundingError as e:
                rejected.append({"finding": finding, "reason": str(e)})

        results[system_name] = {
            "detected": len(findings),
            "opened": opened,
            "rejected": rejected,
        }
    return results
