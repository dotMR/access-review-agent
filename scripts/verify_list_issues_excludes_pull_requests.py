"""Regression guard: list_issues must never count a pull request as a
tracked finding.

Why this exists: found live, in the main repo, right after ADR-0008's
go-live - the quarterly Release body read "65 findings identified this
quarter... 60 remediated" against a report that correctly said 5. Every
scratch-repo live trial (Milestone 12) only ever pushed directly to
`main`, never opening a real PR there, so this went unnoticed until this
repo's own real PRs (#44 onward) and real demo Issues coexisted for the
first time.

GitHub's Issues API (`GET /repos/{owner}/{repo}/issues`, what PyGithub's
`repo.get_issues()` calls) returns pull requests too - PRs are a
superset of Issues in GitHub's own data model. Per-system/category
report tables filter by this project's own labels (a PR never carries
"aws", "orphaned", etc.), so those stayed correct throughout - but
`_build_release_payload`'s `summary_counts(all_issues)` call counts the
raw list list_issues returns with no such filtering, so it directly
inherited every merged PR as a phantom "Remediated" finding.

Fixed in list_issues itself (github/adapter.py) rather than at each call
site, so every caller - present and future - is protected the same way
the label-filtered report paths always were: `issue.pull_request` is
`None` for a genuine Issue and a real object for a PR (PyGithub's own
`Issue.pull_request` property), filtered out before an IssueInfo is ever
built.

Mocks PyGithub's Github/Repository/Issue classes directly (list_issues
makes a real PyGithub call, unlike every other function in this codebase
that already accepts a repo_full_name and gets mocked one level up, at
orchestrator.list_issues) - a minimal stand-in with just the attributes
list_issues actually reads.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


class _FakeLabel:
    def __init__(self, name):
        self.name = name


class _FakeIssue:
    def __init__(self, number, title, state, labels, pull_request=None):
        self.number = number
        self.title = title
        self.body = "fake body"
        self.state = state
        self.labels = [_FakeLabel(name) for name in labels]
        self.created_at = MagicMock(isoformat=lambda: "2026-01-01T00:00:00+00:00")
        self.closed_at = None
        self.html_url = f"https://example.com/issues/{number}"
        # None for a genuine Issue; PyGithub sets this to a real
        # IssuePullRequest object for a PR - the exact attribute
        # list_issues filters on.
        self.pull_request = pull_request


def case_pull_requests_excluded_from_list_issues() -> bool:
    from access_review_agent.github.adapter import list_issues

    real_issue = _FakeIssue(5, "Orphaned access — Someone (AWS)", "open", ["orphaned", "aws"])
    merged_pr = _FakeIssue(44, "Fix some bug", "closed", [], pull_request=object())
    open_pr = _FakeIssue(61, "Work in progress", "open", [], pull_request=object())

    fake_repo = MagicMock()
    fake_repo.get_issues.return_value = [real_issue, merged_pr, open_pr]
    fake_client = MagicMock()
    fake_client.get_repo.return_value = fake_repo

    with (
        patch("access_review_agent.github.adapter.Github", return_value=fake_client),
        patch("access_review_agent.github.adapter._resolve_token", return_value="fake-token"),
    ):
        issues = list_issues("dotMR/access-review-agent")

    problems = []
    numbers = {i.number for i in issues}
    if numbers != {5}:
        problems.append(f"expected only the real Issue (#5) to survive - got {sorted(numbers)}")

    status = "PASS" if not problems else "FAIL"
    print(
        f"[{status}] list-issues-excludes-pull-requests — a real Issue is kept, both an open and "
        "a merged pull request are excluded, even though GitHub's own API returns all three"
    )
    for p in problems:
        print(f"         {p}")
    return not problems


def main() -> None:
    results = [case_pull_requests_excluded_from_list_issues()]
    total, passed = len(results), sum(results)
    print(f"\n{passed}/{total} cases passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
