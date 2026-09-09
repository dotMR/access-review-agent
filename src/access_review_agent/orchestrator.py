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

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from access_review_agent.github.adapter import IssueResult, ReportCommitResult, get_adapter, list_issues
from access_review_agent.github.issues import open_issue
from access_review_agent.grounding import GroundingError
from access_review_agent.narrative import synthesize_narrative
from access_review_agent.reports import SYSTEM_LABEL, SYSTEM_ORDER, build_aggregate_report, build_per_system_report
from access_review_agent.risk_assessment import build_risk_assessment_entries
from access_review_agent.tools.policy import DEFAULT_ROLE_ACCESS_MAPPING_PATH, read_policy
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


_PERIOD_RE = re.compile(r"^\d{4}-Q[1-4]$")

NARRATIVE_DISABLED_NOTE = (
    "_(narrative synthesis disabled for this run — set generate_narrative=True / "
    "ENABLE_RISK_ASSESSMENT_NARRATIVE=true to generate; Likelihood/Impact/Risk Rating "
    "above are still real, computed values)_"
)


async def generate_quarterly_reports(
    repo_full_name: str, period: str, checkout_dir: Path, generate_narrative: bool = False
) -> dict[str, ReportCommitResult]:
    """Roll up the quarter's already-existing Issue-tracker state (SPEC.md
    §2 — detection already happened via push-triggered runs throughout
    the quarter; this just reads and renders, no fresh detection) into
    the two evidentiary reports per system plus the aggregate, committing
    all six via commit_report — the sole caller of commit_report, same
    "main agent only" pattern as open_issue.

    `period` becomes part of every committed file's path
    (`reports/{period}/...`) - validated strictly (YYYY-Qn) before it
    ever reaches a path, since workflow_dispatch's `period` input is
    free-form text a caller controls, not something safe to trust as a
    path segment unvalidated (path traversal via `../`, or worse).

    `checkout_dir` is the local repo checkout Risk Assessment's
    read_prior_report needs (SPEC.md §3 - a local file read, not a
    GitHub API call) for quarterly-recurrence Likelihood.

    `generate_narrative` gates the one real per-run cost this function
    can incur: narrative synthesis is a real Anthropic API call, made
    regardless of GITHUB_WRITE_MODE (that flag only gates GitHub writes,
    not this). Defaults to False - the deterministic Likelihood/Impact/
    Risk Rating scores are still computed and shown either way (free,
    local); only the narrative text itself is skipped when False, with
    an explicit placeholder rather than a silent gap.
    """
    if not _PERIOD_RE.match(period):
        raise ValueError(f"period must match YYYY-Qn (e.g. 2026-Q1), got: {period!r}")

    all_issues = list_issues(repo_full_name)
    per_system_issues = {
        system_name: [i for i in all_issues if SYSTEM_LABEL[system_name] in i.labels]
        for system_name in SYSTEM_ORDER
    }

    system_criticality = read_policy(DEFAULT_ROLE_ACCESS_MAPPING_PATH)["system_criticality"]
    risk_assessment_rows: list[dict[str, Any]] = []
    for system_name in SYSTEM_ORDER:
        entries = build_risk_assessment_entries(
            system_name, per_system_issues[system_name], period, checkout_dir, system_criticality[system_name]
        )
        for entry in entries:
            if generate_narrative:
                narrative, _cost = await synthesize_narrative(entry)
            else:
                narrative = NARRATIVE_DISABLED_NOTE
            risk_assessment_rows.append(
                {
                    "category": entry.category,
                    "system_name": entry.system_name,
                    "likelihood": entry.likelihood,
                    "impact": entry.impact,
                    "risk_rating": entry.risk_rating,
                    "narrative": narrative,
                }
            )

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

    aggregate_content = build_aggregate_report(
        period, per_system_issues, generated_at, risk_assessment_rows=risk_assessment_rows
    )
    results["aggregate"] = adapter.commit_report(
        repo_full_name,
        f"reports/{period}/aggregate.md",
        aggregate_content,
        f"Aggregate report: {period}",
    )
    return results
