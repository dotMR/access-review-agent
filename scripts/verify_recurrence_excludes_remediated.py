"""Regression guard: a Remediated or Accepted-risk finding must not be
scored as "recurring" just because its Issue number also appeared in a
prior period's report.

Why this exists: found during the second live trial's demo-timeline
validation. Ronnis Pawgood's Orphaned/AWS finding (Issue #3) was
genuinely remediated in Q2, yet Q2's own Risk Assessment narrative
described it as "demonstrates a recurring pattern... re-emergence
indicates a systemic control gap," and Q3's called it "reinfection...
occurring," with Likelihood escalating to High - despite the Issue
having been closed for two quarters straight. `count_consecutive_periods`
walks a per-system report file's `### {category}` sections backward and
counts any period where the Issue number appears at all, with no check
on whether it was open or already remediated/accepted at that time.

Real production impact, not just a demo artifact: this would
misrepresent any genuinely-fixed finding as an ongoing, escalating risk
for as long as its Issue number keeps appearing in the line-item
history table (which per-system reports always show, open or closed).

Fixed in build_risk_assessment_entries: a currently-Remediated finding
short-circuits straight to consecutive_periods=1, skipping the
backward-walk entirely - "recurring" only means something for a
still-live problem (Open); a closed Issue can never legitimately go
back to Open under the same number (a later recurrence of the same
problem gets a fresh Issue instead, per the duplicate-Issue-prevention
design), so the multi-period walk is only ever meaningful for an issue
that's still open right now.

A second live trial (the fourth scratch repo) then caught the same class
of bug still present for Accepted-risk findings, which the first fix
hadn't covered: Issue #5 (vpn-legacy-4402), genuinely Open in Q1 and
accepted as risk for the first time in Q2, got described in Q2's own
report as "a recurring identity-resolution gap... persisting as an
accepted risk across two consecutive audit cycles." False: the manual
acceptance determination happened exactly once, this quarter, not
across a span where it was already accepted - count_consecutive_periods
had counted the Issue's two report-section appearances without regard
to what status it held in each one, misreading a fresh determination as
a multi-quarter pattern. Also consistent with CONTEXT.md's own Accepted
Risk definition ("No expiry planned in v1 - the underlying condition is
never re-reviewed or re-surfaced automatically once accepted") - once
closed, a finding is settled either way, not an ongoing pattern to keep
scoring. The fix extends the same short-circuit to both statuses.

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


def case_accepted_risk_finding_not_scored_as_recurring() -> bool:
    from access_review_agent.github.adapter import IssueInfo
    from access_review_agent.risk_assessment import build_risk_assessment_entries

    with tempfile.TemporaryDirectory() as tmp:
        checkout_dir = Path(tmp)
        prior_dir = checkout_dir / "reports" / "2026-Q1"
        prior_dir.mkdir(parents=True)
        # Q1's own report shows #201 as genuinely Open that quarter - a
        # real prior appearance, not a parsing artifact.
        (prior_dir / "vpn.md").write_text(
            "### Identity resolution\n\n"
            "| Identity | Access detail | Expected per policy | Date detected | "
            "Time to revoke | Status | Issue |\n"
            "| :-- | :-- | :-- | :-- | :-- | :-- | :-- |\n"
            "| Someone | `write` access to vpn | None | 2026-01-01 | same day | "
            "Open | [#201](https://example.com/issues/201) |\n"
        )

        accepted_risk_issue = IssueInfo(
            number=201,
            title="Identity resolution — Someone (VPN)",
            body=(
                "**Access detail:** `write` access to vpn\n\n"
                "**Expected per policy:** None\n\n"
                "**Source record:** `access_vpn.csv`, row matching `employee_id=E201`"
            ),
            state="closed",  # accepted risk: closed, carries the accepted-risk label
            labels=["identity-resolution", "vpn", "accepted-risk"],
            created_at=datetime.now(timezone.utc).isoformat(),
            closed_at=datetime.now(timezone.utc).isoformat(),
            html_url="https://example.com/issues/201",
        )

        entries = build_risk_assessment_entries(
            "vpn", [accepted_risk_issue], "2026-Q2", checkout_dir, system_criticality="Low"
        )

    problems = []
    identity_entries = [e for e in entries if e.category == "identity-resolution"]
    if len(identity_entries) != 1:
        problems.append(f"expected exactly one Identity resolution/VPN entry, got {len(identity_entries)}")
    else:
        entry = identity_entries[0]
        finding = entry.findings[0]
        if finding.consecutive_periods != 1:
            problems.append(
                f"expected consecutive_periods=1 for an accepted-risk finding despite appearing in "
                f"Q1's report too (as Open) - got {finding.consecutive_periods}"
            )
        if entry.likelihood != "Low":
            problems.append(
                f"expected Likelihood=Low for a settled, accepted-risk finding - got {entry.likelihood}"
            )

    status = "PASS" if not problems else "FAIL"
    print(
        f"[{status}] recurrence-excludes-accepted-risk — an accepted-risk finding scores as isolated "
        "(consecutive_periods=1), not recurring, even though its Issue number appeared in a prior "
        "period's report too (as Open)"
    )
    for p in problems:
        print(f"         {p}")
    return not problems


def main() -> None:
    results = [
        case_remediated_finding_not_scored_as_recurring(),
        case_accepted_risk_finding_not_scored_as_recurring(),
    ]
    total, passed = len(results), sum(results)
    print(f"\n{passed}/{total} cases passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
