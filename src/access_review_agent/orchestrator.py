"""Main agent: the sole orchestrator and Issue-writer, per SPEC.md §3.

Constructs one SystemDetectionUnit per Information System and aggregates
each unit's already-detected findings — it never re-derives them by
combining raw per-system data against HRIS itself (SPEC.md §3). Then runs
open_issue (which itself gates on validate_finding, per ADR-0007) on
every finding. Units never call open_issue themselves; this module is the
only caller in the whole detection path, matching the tool registry's
"open_issue — held by: Main agent only."

Milestone 4 always ran all five systems (manually/locally triggered, no
dispatch yet). Milestone 5 adds `systems`, so a real push-triggered run
can scope to exactly what `dispatch.determine_dispatch()` decided — a
single-system commit runs one unit, not all five.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from access_review_agent.github.adapter import IssueResult, ReportCommitResult, get_adapter, list_issues
from access_review_agent.github.issues import open_issue
from access_review_agent.grounding import GroundingError
from access_review_agent.reports import SYSTEM_LABEL, SYSTEM_ORDER, build_aggregate_report, build_per_system_report
from access_review_agent.units import SYSTEMS, SystemDetectionUnit


def run_full_reconciliation(
    data_dir: Path,
    repo_full_name: str,
    systems: set[str] | None = None,
    commit_sha: str | None = None,
) -> dict[str, Any]:
    """Reconciliation across `systems` (default: all five) and all Tier 1
    categories: detect, then open an Issue for every grounded finding.
    `commit_sha`, when given, upgrades every Issue's Source record
    citation to a clickable GitHub blob permalink (Milestone 5) - passed
    straight through to open_issue.
    Returns a per-system summary (findings detected, Issues opened,
    findings rejected by the grounding gate) for inspection.
    """
    results: dict[str, Any] = {}
    for system_name in (systems if systems is not None else SYSTEMS):
        unit = SystemDetectionUnit(system_name, data_dir)
        findings = unit.detect_all()

        opened: list[IssueResult] = []
        rejected: list[dict[str, Any]] = []
        for finding in findings:
            try:
                opened.append(open_issue(finding, repo_full_name, data_dir, commit_sha))
            except GroundingError as e:
                rejected.append({"finding": finding, "reason": str(e)})

        results[system_name] = {
            "detected": len(findings),
            "opened": opened,
            "rejected": rejected,
        }
    return results


def generate_quarterly_reports(repo_full_name: str, period: str) -> dict[str, ReportCommitResult]:
    """Roll up the quarter's already-existing Issue-tracker state (SPEC.md
    §2 — detection already happened via push-triggered runs throughout
    the quarter; this just reads and renders, no fresh detection) into
    the two evidentiary reports per system plus the aggregate, committing
    all six via commit_report — the sole caller of commit_report, same
    "main agent only" pattern as open_issue.
    """
    all_issues = list_issues(repo_full_name)
    per_system_issues = {
        system_name: [i for i in all_issues if SYSTEM_LABEL[system_name] in i.labels]
        for system_name in SYSTEM_ORDER
    }

    generated_at = datetime.now(timezone.utc).isoformat()
    adapter = get_adapter()
    results: dict[str, ReportCommitResult] = {}

    for system_name in SYSTEM_ORDER:
        content = build_per_system_report(
            system_name, period, per_system_issues[system_name], generated_at
        )
        path = f"reports/{period}/{system_name}.md"
        results[system_name] = adapter.commit_report(
            repo_full_name, path, content, f"Per-system report: {system_name}, {period}"
        )

    aggregate_content = build_aggregate_report(period, per_system_issues, generated_at)
    results["aggregate"] = adapter.commit_report(
        repo_full_name,
        f"reports/{period}/aggregate.md",
        aggregate_content,
        f"Aggregate report: {period}",
    )
    return results
