"""Regression guard: the aggregate quarterly report's Risk Assessment
section must only include findings relevant to THIS quarter, per SPEC.md
§5 ("one entry per (category, system) pair with at least one Finding
this quarter") - not every Issue the tracker has ever seen for that
category+system.

Why this exists: found during Milestone 12's live-trial review of a
freshly-generated Q3 report. An Issue remediated back in Q2 (Ronnis
Pawgood's Orphaned/AWS finding, #3) reappeared as its own row in Q3's
Risk Assessment table too, with the narrative wrongly claiming it "was
remediated within the same audit cycle" - false, since it was actually
remediated a full quarter earlier. Root cause: generate_quarterly_reports
passed the full lifetime per_system_issues list into
build_risk_assessment_entries, with no period filter at all - correct for
the per-system/aggregate resolution-status rollups (cumulative by
design), but wrong for Risk Assessment's own quarter-scoped definition.

First fix attempt compared each Issue's real closed_at to period_bounds'
SIMULATED calendar quarter boundaries - which broke down in the very live
trial that found the bug: simulating three quarters within a single real
day closes every Issue with a real "today" timestamp regardless of which
simulated quarter it represents, so period_bounds couldn't tell "closed
during simulated Q2" from "closed during simulated Q3" (both are really
today). Fixed instead by comparing against the PRIOR period's own
report-generation moment (read_prior_report_generated_at) - a real,
sequential boundary with no simulated calendar involved: did this closure
happen after the last time a report was generated for the prior period,
or before it (already covered there). Correct in genuine production too,
where periods advance in real time anyway.

Uses a real temp git checkout (not REPO_ROOT) with a hand-written prior
period's aggregate.md, since generate_quarterly_reports resolves the Data
snapshot field via `git rev-parse HEAD` and Risk Assessment scoping now
reads the prior period's own committed report - same fixture pattern as
verify_trend_line.py.
"""

import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

SCRATCH_REPO = "dotMR/access-review-agent-scratch"


def _git_init(path: Path) -> None:
    """generate_quarterly_reports resolves the Data snapshot field via
    `git rev-parse HEAD` against checkout_dir - a real checkout always
    has one, but these fixtures' plain temp dirs don't unless this runs
    first. -c user.name/user.email rather than relying on global git
    config, which a CI runner has no reason to have set.
    """
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(
        ["git", "-c", "user.name=test", "-c", "user.email=test@example.com",
         "commit", "-q", "--allow-empty", "-m", "init"],
        cwd=path, check=True,
    )


class _RecordingAdapter:
    def __init__(self):
        self.committed: dict[str, str] = {}

    def commit_report(self, repo_full_name, path, content, message):
        from access_review_agent.github.adapter import ReportCommitResult

        self.committed[path] = content
        return ReportCommitResult(path=path, commit_sha="fake", html_url=None, dry_run=False)


def _mock_issue(number, category, system, created_at, state, closed_at=None):
    from access_review_agent.github.adapter import IssueInfo

    return IssueInfo(
        number=number,
        title=f"{category.replace('-', ' ').title()} access — Someone {number} ({system})",
        body=(
            f"**Access detail:** `write` access to {system}\n\n"
            "**Expected per policy:** N/A\n\n"
            f"**Source record:** `access_{system}.csv`, row matching `employee_id=E{number}`"
        ),
        state=state,
        labels=[category, system.replace("_", "-")],
        created_at=created_at,
        closed_at=closed_at,
        html_url=f"https://example.com/issues/{number}",
    )


def _write_prior_aggregate(checkout_dir: Path, period: str, generated_at: str) -> None:
    """A minimal but real aggregate.md, matching exactly what
    read_prior_report_generated_at parses back out of it: the "Report
    generated" line. Nothing else in the file needs to be real.
    """
    period_dir = checkout_dir / "reports" / period
    period_dir.mkdir(parents=True)
    (period_dir / "aggregate.md").write_text(
        f"# Quarterly Access Review Audit Report — {period}\n\n"
        f"- **Report generated:** {generated_at}\n"
    )


async def case_issue_closed_before_prior_report_excluded() -> bool:
    from access_review_agent.orchestrator import generate_quarterly_reports

    q2_generated_at = datetime(2026, 9, 12, 10, 22, 44, tzinfo=timezone.utc)
    before_q2_report = (q2_generated_at - timedelta(minutes=15)).isoformat()
    after_q2_report = (q2_generated_at + timedelta(minutes=50)).isoformat()

    # Closed BEFORE Q2's own report was generated - already covered by
    # Q2's report, must NOT reappear in Q3 even though its real
    # closed_at timestamp (like everything else in a same-day simulated
    # trial) would fall inside Q3's real calendar quarter too.
    closed_before_prior_report = _mock_issue(
        101, "orphaned", "aws", "2026-01-05T00:00:00+00:00", "closed", closed_at=before_q2_report
    )
    # Closed AFTER Q2's own report was generated - genuinely new since
    # then, must appear in Q3.
    closed_after_prior_report = _mock_issue(
        102, "unapproved", "aws", "2026-07-01T00:00:00+00:00", "closed", closed_at=after_q2_report
    )
    # Still open regardless of age - must appear.
    still_open = _mock_issue(103, "dormant-admin", "github", "2026-01-01T00:00:00+00:00", "open")

    with tempfile.TemporaryDirectory() as tmp:
        checkout_dir = Path(tmp)
        _git_init(checkout_dir)
        _write_prior_aggregate(checkout_dir, "2026-Q2", q2_generated_at.isoformat())

        with (
            patch(
                "access_review_agent.orchestrator.list_issues",
                return_value=[closed_before_prior_report, closed_after_prior_report, still_open],
            ),
            patch("access_review_agent.orchestrator.get_adapter", return_value=_RecordingAdapter()) as get_adapter,
        ):
            await generate_quarterly_reports(SCRATCH_REPO, "2026-Q3", checkout_dir, generate_narrative=False)
            aggregate_content = get_adapter.return_value.committed["reports/2026-Q3/aggregate.md"]

    risk_section = aggregate_content.split("## Risk Assessment")[1].split("## Escalations")[0]
    problems = []
    # generate_narrative=False renders NARRATIVE_DISABLED_NOTE, which never
    # cites an Issue number - each entry's presence is checked via its
    # (category, system) row instead, since these three issues each have a
    # distinct category+system pair.
    if "Orphaned access | AWS" in risk_section:
        problems.append(
            "Orphaned/AWS (#101, closed before Q2's report was generated) incorrectly appears in Q3's table"
        )
    if "Unapproved access | AWS" not in risk_section:
        problems.append("expected Unapproved/AWS (#102, closed after Q2's report was generated) in Q3's table")
    if "Dormant admin-level access | GitHub" not in risk_section:
        problems.append("expected Dormant admin-level/GitHub (#103, still open) in Q3's Risk Assessment table")

    status = "PASS" if not problems else "FAIL"
    print(
        f"[{status}] risk-assessment-period-scope — Risk Assessment shows only findings still open "
        "or closed after the prior period's own report was generated, not every Issue ever seen "
        "for that category+system"
    )
    for p in problems:
        print(f"         {p}")
    return not problems


async def case_first_quarter_includes_all_closed_issues() -> bool:
    """No prior period's report exists yet (the first quarter) - every
    closed Issue is necessarily new, so none should be excluded.
    """
    from access_review_agent.orchestrator import generate_quarterly_reports

    remediated_this_quarter = _mock_issue(
        201, "orphaned", "aws", "2026-01-05T00:00:00+00:00", "closed",
        closed_at="2026-01-10T00:00:00+00:00",
    )

    with tempfile.TemporaryDirectory() as tmp:
        checkout_dir = Path(tmp)
        _git_init(checkout_dir)

        with (
            patch("access_review_agent.orchestrator.list_issues", return_value=[remediated_this_quarter]),
            patch("access_review_agent.orchestrator.get_adapter", return_value=_RecordingAdapter()) as get_adapter,
        ):
            await generate_quarterly_reports(SCRATCH_REPO, "2026-Q1", checkout_dir, generate_narrative=False)
            aggregate_content = get_adapter.return_value.committed["reports/2026-Q1/aggregate.md"]

    risk_section = aggregate_content.split("## Risk Assessment")[1].split("## Escalations")[0]
    problems = []
    if "Orphaned access | AWS" not in risk_section:
        problems.append("expected #201 (remediated in Q1, no prior report exists) in Q1's Risk Assessment table")

    status = "PASS" if not problems else "FAIL"
    print(
        f"[{status}] risk-assessment-period-scope-first-quarter — a first quarter with no prior "
        "report includes every closed Issue, since none of them could have been reported before"
    )
    for p in problems:
        print(f"         {p}")
    return not problems


async def main() -> None:
    results = [
        await case_issue_closed_before_prior_report_excluded(),
        await case_first_quarter_includes_all_closed_issues(),
    ]
    total, passed = len(results), sum(results)
    print(f"\n{passed}/{total} cases passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
