"""Regression guard: confirms run_full_reconciliation doesn't re-open a
new Issue for a finding that's still present but already has an open
Issue from a prior run.

Why this exists: found live during Milestone 12's scratch-repo trial,
not designed in speculatively. A push touching system_hr.csv (or
policy-config.yaml/role-access-mapping.yaml) fans out to all five
systems (dispatch.py) - so a run that re-detects an already-known,
still-open finding (nothing about it changed) had nothing to recognize
"there's already an open Issue for this" and opened a brand new
duplicate every time. Every eval fixture before this test was a
single-shot detection check against fresh data, so none of them ever
exercised running detection twice against unchanged data - the exact
shape of run that triggered this live.

Mocks list_issues (the one call run_full_reconciliation makes that's
never dry-run-gated - always a real API call per its own docstring) so
this stays credential-free; create_issue/close_issue/apply_label/
add_comment all go through the default DryRunAdapter already, no
mocking needed there.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

FIXTURE_DIR = Path(__file__).resolve().parent.parent / "evals" / "cases" / "partial-failure-isolation"
SCRATCH_REPO = "dotMR/access-review-agent-scratch"


async def case_duplicate_issue_skipped() -> bool:
    from access_review_agent.github.adapter import IssueInfo
    from access_review_agent.orchestrator import run_full_reconciliation

    # Exactly the title _format_title would compute for the fixture's own
    # GitHub Unapproved finding (Github Employee, E9202) - a prior run's
    # Issue for the SAME finding, still open, nothing about it changed.
    already_open = IssueInfo(
        number=101,
        title="Unapproved access — Github Employee (GitHub)",
        body="pre-existing",
        state="open",
        labels=["unapproved", "github"],
        created_at=datetime.now(timezone.utc).isoformat(),
        closed_at=None,
        html_url="https://example.com/issues/101",
    )

    with patch("access_review_agent.orchestrator.list_issues", return_value=[already_open]):
        results = await run_full_reconciliation(
            FIXTURE_DIR, SCRATCH_REPO, systems=None, check_lifecycle=True
        )

    problems = []
    github_result = results["systems"]["github"]
    if github_result["detected"] != 1:
        problems.append(f"expected 1 finding detected for github, got {github_result['detected']}")
    if len(github_result["opened"]) != 0:
        problems.append(f"expected 0 Issues opened for github (already open) - got {len(github_result['opened'])}")
    if len(github_result["skipped_existing"]) != 1:
        problems.append(
            f"expected the github finding to be recorded as skipped_existing - got {github_result['skipped_existing']}"
        )

    # A different system's genuinely-new finding (no matching open Issue
    # in the mock) must still open normally - dedup isn't a blanket freeze.
    salesforce_result = results["systems"]["salesforce"]
    if len(salesforce_result["opened"]) != 1:
        problems.append(
            f"expected salesforce's finding (no existing Issue for it) to open normally - "
            f"got {len(salesforce_result['opened'])} opened"
        )

    status = "PASS" if not problems else "FAIL"
    print(
        f"[{status}] duplicate-issue-prevention — a finding whose title matches an already-open "
        "Issue is skipped, not re-opened, while genuinely new findings still open normally"
    )
    for p in problems:
        print(f"         {p}")
    return not problems


async def main() -> None:
    results = [await case_duplicate_issue_skipped()]
    total, passed = len(results), sum(results)
    print(f"\n{passed}/{total} cases passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
