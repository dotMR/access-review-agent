"""Regression guard for the per-system/aggregate reports' Data snapshot
field (design-doc.md's "tagging the exact commit, pinning
code, policy, and data snapshot together").

Why this exists: found during the second live trial's report review -
every report's Data snapshot line permanently read "N/A (manual/local
run)," the default, because no caller of build_per_system_report/
build_aggregate_report ever supplied a real value. A fourth instance of
this milestone's recurring "field that looks real but nothing ever
wires it" pattern (Escalations-this-period table, trend line, Release
body escalation count).

Fixed by generate_quarterly_reports resolving checkout_dir's real
current commit (`git rev-parse HEAD`, the same mechanism
create_quarterly_release already uses for tagging) and linking it as a
`tree/<sha>` GitHub URL.

Mocks list_issues (real-API-only, never dry-run-gated); get_adapter is
mocked with a small recording adapter so committed content can be
inspected directly. checkout_dir is a real, git-initialized temp
directory (not just a plain temp dir), since `git rev-parse HEAD`
needs an actual repo to resolve against - a real checkout always has
one; a bare temp dir doesn't unless this test creates it.
"""

import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

SCRATCH_REPO = "dotMR/access-review-agent-scratch"


class _RecordingAdapter:
    def __init__(self):
        self.committed: dict[str, str] = {}

    def commit_report(self, repo_full_name, path, content, message):
        from access_review_agent.github.adapter import ReportCommitResult

        self.committed[path] = content
        return ReportCommitResult(path=path, commit_sha="fake", html_url=None, dry_run=False)


def _mock_issue(number, category, system):
    from access_review_agent.github.adapter import IssueInfo

    return IssueInfo(
        number=number,
        title=f"{category.replace('-', ' ').title()} access — Someone {number} ({system})",
        body=(
            f"**Access detail:** `write` access to {system}\n\n"
            "**Expected per policy:** N/A\n\n"
            f"**Source record:** `access_{system}.csv`, row matching `employee_id=E{number}`"
        ),
        state="open",
        labels=[category, system.replace("_", "-")],
        created_at=datetime.now(timezone.utc).isoformat(),
        closed_at=None,
        html_url=f"https://example.com/issues/{number}",
    )


async def case_data_snapshot_resolves_to_real_commit() -> bool:
    from access_review_agent.orchestrator import generate_quarterly_reports

    with tempfile.TemporaryDirectory() as tmp:
        checkout_dir = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=checkout_dir, check=True)
        subprocess.run(
            ["git", "-c", "user.name=test", "-c", "user.email=test@example.com",
             "commit", "-q", "--allow-empty", "-m", "init"],
            cwd=checkout_dir, check=True,
        )
        head_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=checkout_dir, capture_output=True, text=True, check=True
        ).stdout.strip()

        issues = [_mock_issue(201, "unapproved", "aws")]
        with (
            patch("access_review_agent.orchestrator.list_issues", return_value=issues),
            patch("access_review_agent.orchestrator.get_adapter", return_value=_RecordingAdapter()) as get_adapter,
        ):
            await generate_quarterly_reports(SCRATCH_REPO, "2026-Q1", checkout_dir, generate_narrative=False)
            committed = get_adapter.return_value.committed

    aggregate_content = committed["reports/2026-Q1/aggregate.md"]
    per_system_content = committed["reports/2026-Q1/aws.md"]
    expected_link = f"https://github.com/{SCRATCH_REPO}/tree/{head_sha}"

    problems = []
    for name, content in [("aggregate", aggregate_content), ("per-system", per_system_content)]:
        if "N/A (manual/local run)" in content:
            problems.append(f"{name} report still shows the 'N/A (manual/local run)' placeholder")
        if head_sha[:7] not in content:
            problems.append(f"{name} report doesn't show the real commit's short SHA ({head_sha[:7]})")
        if expected_link not in content:
            problems.append(f"{name} report doesn't link to the real commit ({expected_link})")

    status = "PASS" if not problems else "FAIL"
    print(
        f"[{status}] data-snapshot-real-commit — every report's Data snapshot field resolves to "
        "checkout_dir's real current commit, not the permanent 'N/A' placeholder"
    )
    for p in problems:
        print(f"         {p}")
    return not problems


async def main() -> None:
    results = [await case_data_snapshot_resolves_to_real_commit()]
    total, passed = len(results), sum(results)
    print(f"\n{passed}/{total} cases passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
