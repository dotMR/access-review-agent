"""Regression guard: a remediated finding must not be scored as
"recurring" just because its Issue number also appeared in a prior
period's report.

Why this exists: found during the second live trial's demo-timeline
validation. Ronnis Pawgood's Orphaned/AWS finding (Issue #3) was
genuinely remediated in Q2, yet Q2's own Risk Assessment narrative
described it as "demonstrates a recurring pattern... re-emergence
indicates a systemic control gap," and Q3's called it "reinfection...
occurring," with Likelihood escalating to High - despite the Issue
having been closed for two quarters straight. `count_consecutive_periods`
walks a per-system report file's `### {category}` sections backward and
counts any period where the Issue number appears at all, with no check
on whether it was open or already remediated at that time.

Real production impact, not just a demo artifact: this would
misrepresent any genuinely-fixed finding as an ongoing, escalating risk
for as long as its Issue number keeps appearing in the line-item
history table (which per-system reports always show, open or closed).

Fixed in build_risk_assessment_entries: a currently-remediated finding
short-circuits straight to consecutive_periods=1, skipping the
backward-walk entirely - "recurring" only means something for a
still-live problem (Open or Accepted risk); a remediated Issue can
never legitimately go back to Open under the same number (a later
recurrence of the same problem gets a fresh Issue instead, per the
duplicate-Issue-prevention design), so the multi-period walk is only
ever meaningful for an issue that's still open right now.

checkout_dir is a real temp directory with a hand-written prior-period
per-system report, since count_consecutive_periods/read_prior_report
are local file reads, not GitHub calls.
"""

import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def case_remediated_finding_not_scored_as_recurring() -> bool:
    from access_review_agent.github.adapter import IssueInfo
    from access_review_agent.risk_assessment import build_risk_assessment_entries

    with tempfile.TemporaryDirectory() as tmp:
        checkout_dir = Path(tmp)
        prior_dir = checkout_dir / "reports" / "2026-Q1"
        prior_dir.mkdir(parents=True)
        # Q1's own report shows #101 as genuinely Open that quarter - a
        # real prior appearance, not a parsing artifact.
        (prior_dir / "aws.md").write_text(
            "### Orphaned access\n\n"
            "| Identity | Access detail | Expected per policy | Date detected | "
            "Time to revoke | Status | Issue |\n"
            "| :-- | :-- | :-- | :-- | :-- | :-- | :-- |\n"
            "| Someone | `write` access to aws | None | 2026-01-01 | same day | "
            "Open | [#101](https://example.com/issues/101) |\n"
        )

        remediated_issue = IssueInfo(
            number=101,
            title="Orphaned access — Someone (AWS)",
            body=(
                "**Access detail:** `write` access to aws\n\n"
                "**Expected per policy:** None\n\n"
                "**Source record:** `access_aws.csv`, row matching `employee_id=E101`"
            ),
            state="closed",  # remediated: closed, no accepted-risk label
            labels=["orphaned", "aws"],
            created_at=datetime.now(timezone.utc).isoformat(),
            closed_at=datetime.now(timezone.utc).isoformat(),
            html_url="https://example.com/issues/101",
        )

        entries = build_risk_assessment_entries(
            "aws", [remediated_issue], "2026-Q2", checkout_dir, system_criticality="Critical"
        )

    problems = []
    orphaned_entries = [e for e in entries if e.category == "orphaned"]
    if len(orphaned_entries) != 1:
        problems.append(f"expected exactly one Orphaned/AWS entry, got {len(orphaned_entries)}")
    else:
        entry = orphaned_entries[0]
        finding = entry.findings[0]
        if finding.consecutive_periods != 1:
            problems.append(
                f"expected consecutive_periods=1 for a remediated finding despite appearing in "
                f"Q1's report too - got {finding.consecutive_periods}"
            )
        if entry.likelihood != "Low":
            problems.append(f"expected Likelihood=Low for an isolated, resolved finding - got {entry.likelihood}")

    status = "PASS" if not problems else "FAIL"
    print(
        f"[{status}] recurrence-excludes-remediated — a remediated finding scores as isolated "
        "(consecutive_periods=1), not recurring, even though its Issue number appeared in a prior "
        "period's report too"
    )
    for p in problems:
        print(f"         {p}")
    return not problems


def main() -> None:
    results = [case_remediated_finding_not_scored_as_recurring()]
    total, passed = len(results), sum(results)
    print(f"\n{passed}/{total} cases passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
