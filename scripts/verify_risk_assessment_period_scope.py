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

Fixed by scoping the issues passed to build_risk_assessment_entries to
just this quarter's: still-open (a live finding, regardless of how long
it's been open) or closed within this quarter's own period_bounds (a
resolution this quarter's record should show) - excluding anything
closed in an earlier quarter and untouched since.

Mocks list_issues and get_adapter the same way
verify_escalations_this_period.py does, so the committed aggregate
content can be inspected directly.
"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRATCH_REPO = "dotMR/access-review-agent-scratch"


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


async def case_issue_closed_in_earlier_quarter_excluded() -> bool:
    from access_review_agent.orchestrator import generate_quarterly_reports

    # Remediated a full quarter before Q3 - must NOT reappear in Q3.
    stale_remediated = _mock_issue(
        101, "orphaned", "aws", "2026-01-05T00:00:00+00:00", "closed", closed_at="2026-05-01T00:00:00+00:00"
    )
    # Remediated inside Q3 itself - must appear.
    this_quarter_remediated = _mock_issue(
        102, "unapproved", "aws", "2026-07-01T00:00:00+00:00", "closed", closed_at="2026-08-15T00:00:00+00:00"
    )
    # Still open regardless of age - must appear.
    still_open = _mock_issue(103, "dormant-admin", "github", "2026-01-01T00:00:00+00:00", "open")

    with (
        patch(
            "access_review_agent.orchestrator.list_issues",
            return_value=[stale_remediated, this_quarter_remediated, still_open],
        ),
        patch("access_review_agent.orchestrator.get_adapter", return_value=_RecordingAdapter()) as get_adapter,
    ):
        await generate_quarterly_reports(SCRATCH_REPO, "2026-Q3", REPO_ROOT, generate_narrative=False)
        aggregate_content = get_adapter.return_value.committed["reports/2026-Q3/aggregate.md"]

    risk_section = aggregate_content.split("## Risk Assessment")[1].split("## Escalations")[0]
    problems = []
    # generate_narrative=False renders NARRATIVE_DISABLED_NOTE, which never
    # cites an Issue number - each entry's presence is checked via its
    # (category, system) row instead, since these three issues each have a
    # distinct category+system pair.
    if "Orphaned access | AWS" in risk_section:
        problems.append("Orphaned/AWS (#101, remediated in Q2, not Q3) incorrectly appears in Q3's table")
    if "Unapproved access | AWS" not in risk_section:
        problems.append("expected Unapproved/AWS (#102, remediated within Q3) in Q3's Risk Assessment table")
    if "Dormant admin-level access | GitHub" not in risk_section:
        problems.append("expected Dormant admin-level/GitHub (#103, still open) in Q3's Risk Assessment table")

    status = "PASS" if not problems else "FAIL"
    print(
        f"[{status}] risk-assessment-period-scope — Risk Assessment shows only findings still open "
        "or closed within THIS quarter, not every Issue ever seen for that category+system"
    )
    for p in problems:
        print(f"         {p}")
    return not problems


async def main() -> None:
    results = [await case_issue_closed_in_earlier_quarter_excluded()]
    total, passed = len(results), sum(results)
    print(f"\n{passed}/{total} cases passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
