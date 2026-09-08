"""Dry-run-capable GitHub adapter.

Per iam-review-agent-design.md's Local vs. remote section: a single
entrypoint, with the one thing that genuinely differs between local and
remote (talking to GitHub) isolated behind a flag - real API calls in one
implementation, logging-only in another. Dry-run is the default: real
writes require explicit opt-in (GITHUB_WRITE_MODE=real), not opt-out,
since an accidental write is harder to undo than a missed one.

Same env var name (GITHUB_TOKEN) whether it's a local PAT or a GitHub
Actions secret - the code never knows which source it came from.
"""

import os
import subprocess
from dataclasses import dataclass
from typing import Protocol

from github import Auth, Github


@dataclass
class IssueResult:
    number: int | None  # None in dry-run mode
    html_url: str | None
    title: str
    body: str
    labels: list[str]
    dry_run: bool


class GitHubAdapter(Protocol):
    def create_issue(
        self, repo_full_name: str, title: str, body: str, labels: list[str]
    ) -> IssueResult: ...


class DryRunAdapter:
    """Logs what would happen. Never touches the network."""

    def create_issue(
        self, repo_full_name: str, title: str, body: str, labels: list[str]
    ) -> IssueResult:
        print(f"[DRY RUN] Would open Issue on {repo_full_name}:")
        print(f"  Title:  {title}")
        print(f"  Labels: {labels}")
        print(f"  Body:\n{body}")
        return IssueResult(
            number=None, html_url=None, title=title, body=body, labels=labels, dry_run=True
        )


class RealAdapter:
    """Makes real GitHub API calls via PyGithub."""

    def __init__(self, token: str):
        self._client = Github(auth=Auth.Token(token))

    def create_issue(
        self, repo_full_name: str, title: str, body: str, labels: list[str]
    ) -> IssueResult:
        repo = self._client.get_repo(repo_full_name)
        issue = repo.create_issue(title=title, body=body, labels=labels)
        return IssueResult(
            number=issue.number,
            html_url=issue.html_url,
            title=title,
            body=body,
            labels=labels,
            dry_run=False,
        )


def _resolve_token() -> str | None:
    """GITHUB_TOKEN env var first (works locally via .env or a GitHub
    Actions secret, same name either way). Falls back to `gh auth token`
    for local dev convenience only - CI always has GITHUB_TOKEN set
    directly, this fallback never runs there.
    """
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    try:
        result = subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() or None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def get_adapter() -> GitHubAdapter:
    """Select the adapter based on GITHUB_WRITE_MODE. Anything other than
    "real" (including unset) is dry-run - the safe default.
    """
    if os.environ.get("GITHUB_WRITE_MODE") != "real":
        return DryRunAdapter()

    token = _resolve_token()
    if not token:
        raise RuntimeError(
            "GITHUB_WRITE_MODE=real requires GITHUB_TOKEN (or a working `gh` "
            "auth session for local dev) to be available"
        )
    return RealAdapter(token)
