"""Regression guard for the aggregate quarterly report's Trend section
(SPEC.md §5/§6; demo-timeline.md's "First real trend line, comparing
against Q1" / "Trend line continues" narrative beats).

Why this exists: found during Milestone 12's live-trial review of a
freshly-generated Q3 report - every quarter's Executive Summary said
"N/A, no prior period," even Q3, because build_aggregate_report's
trend_note parameter was never supplied by any caller. Fixed via
risk_assessment.read_prior_aggregate_total (a single prior-vs-current
comparison, buried as one bullet in the Executive Summary).

Later given real design attention (found the single bullet too easy to
miss for something this meaningful): replaced with a dedicated "##
Trend" section - a genuine multi-quarter table (period, total, open,
remediated, accepted risk, delta vs. the row above it), not just a
two-period comparison, via the newer risk_assessment.read_period_history.

Mocks list_issues (real-API-only, never dry-run-gated); get_adapter is
mocked with a small recording adapter so the committed aggregate content
can be inspected directly, since generate_quarterly_reports returns
ReportCommitResult objects (paths), not report text. checkout_dir is a
real, git-initialized temp directory (generate_quarterly_reports also
resolves the Data snapshot field via `git rev-parse HEAD` against it,
so a bare temp dir without a real repo would fail that step first).
"""

import subprocess
import sys
import tempfile
from datetime import datetime, timezone
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


def _write_aggregate(checkout_dir: Path, period: str, open_n: int, remediated_n: int, accepted_n: int) -> None:
    """A minimal but real aggregate.md, matching exactly the two things
    read_period_history parses back out of it: the Resolution status
    Total row's four counts. Nothing else in the file needs to be real.
    """
    total_n = open_n + remediated_n + accepted_n
    period_dir = checkout_dir / "reports" / period
    period_dir.mkdir(parents=True)
    (period_dir / "aggregate.md").write_text(
        f"# Quarterly Access Review Audit Report — {period}\n\n"
        "## Resolution status by system\n\n"
        "| System | Open | Remediated | Accepted risk | Total | Detail |\n"
        "| :-- | --: | --: | --: | --: | :-- |\n"
        f"| **Total** | {open_n} | {remediated_n} | {accepted_n} | {total_n} | |\n"
    )


def _trend_section(aggregate_content: str) -> str:
    return aggregate_content.split("## Trend", 1)[1].split("## Methodology", 1)[0]


async def case_multi_quarter_history_all_rows_present() -> bool:
    """Three prior quarters on disk plus the one being generated now -
    every row must appear, each with its own delta against the row
    directly above it, not just a two-period comparison.
    """
    from access_review_agent.orchestrator import generate_quarterly_reports

    with tempfile.TemporaryDirectory() as tmp:
        checkout_dir = Path(tmp)
        _git_init(checkout_dir)
        _write_aggregate(checkout_dir, "2025-Q3", open_n=5, remediated_n=3, accepted_n=0)  # total 8
        _write_aggregate(checkout_dir, "2025-Q4", open_n=2, remediated_n=1, accepted_n=2)  # total 5
        _write_aggregate(checkout_dir, "2026-Q1", open_n=3, remediated_n=4, accepted_n=1)  # total 8

        issues = [_mock_issue(101, "unapproved", "aws"), _mock_issue(102, "unapproved", "github")]
        with (
            patch("access_review_agent.orchestrator.list_issues", return_value=issues),
            patch("access_review_agent.orchestrator.get_adapter", return_value=_RecordingAdapter()) as get_adapter,
        ):
            await generate_quarterly_reports(SCRATCH_REPO, "2026-Q2", checkout_dir, generate_narrative=False)
            aggregate_content = get_adapter.return_value.committed["reports/2026-Q2/aggregate.md"]

    section = _trend_section(aggregate_content)
    problems = []
    expected_rows = [
        ("2025-Q3", "8", "N/A, first period"),
        ("2025-Q4", "5", "-3"),
        ("2026-Q1", "8", "+3"),
        ("2026-Q2", "2", "-6"),
    ]
    for period, total, delta in expected_rows:
        row_line = next((line for line in section.splitlines() if line.startswith(f"| {period} ")), None)
        if row_line is None:
            problems.append(f"expected a row for {period} in the Trend table, found none")
            continue
        if f"| {total} |" not in row_line:
            problems.append(f"{period}'s row: expected total {total} - got: {row_line}")
        if delta not in row_line:
            problems.append(f"{period}'s row: expected delta '{delta}' - got: {row_line}")

    status = "PASS" if not problems else "FAIL"
    print(
        f"[{status}] trend-multi-quarter-history — every earlier period gets its own row with its "
        "own delta against the row above it, not just a two-period comparison"
    )
    for p in problems:
        print(f"         {p}")
    return not problems


async def case_first_quarter_renders_real_one_row_table() -> bool:
    """No prior aggregate report on disk at all - must still render a
    genuine one-row table (just this period), not a fabricated
    comparison or an error placeholder.
    """
    from access_review_agent.orchestrator import generate_quarterly_reports

    with tempfile.TemporaryDirectory() as tmp:
        checkout_dir = Path(tmp)
        _git_init(checkout_dir)
        issues = [_mock_issue(201, "orphaned", "vpn")]
        with (
            patch("access_review_agent.orchestrator.list_issues", return_value=issues),
            patch("access_review_agent.orchestrator.get_adapter", return_value=_RecordingAdapter()) as get_adapter,
        ):
            await generate_quarterly_reports(SCRATCH_REPO, "2026-Q1", checkout_dir, generate_narrative=False)
            aggregate_content = get_adapter.return_value.committed["reports/2026-Q1/aggregate.md"]

    section = _trend_section(aggregate_content)
    data_rows = [line for line in section.splitlines() if line.startswith("| 2026-Q1 ")]
    problems = []
    if len(data_rows) != 1:
        problems.append(f"expected exactly one data row (2026-Q1 itself) - got {len(data_rows)}")
    elif "N/A, first period" not in data_rows[0]:
        problems.append(f"expected 'N/A, first period' for a genuine first quarter - got: {data_rows[0]}")

    status = "PASS" if not problems else "FAIL"
    print(
        f"[{status}] trend-first-quarter — a quarter with no prior aggregate report on disk still "
        "renders a real one-row table, not a fabricated comparison"
    )
    for p in problems:
        print(f"         {p}")
    return not problems


async def main() -> None:
    results = [
        await case_multi_quarter_history_all_rows_present(),
        await case_first_quarter_renders_real_one_row_table(),
    ]
    total, passed = len(results), sum(results)
    print(f"\n{passed}/{total} cases passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
