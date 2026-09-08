"""Issue formatting and creation: SPEC.md §4's Issue format, gated by the
grounding guardrail.

open_issue() is the one function Milestone 2 needs to prove: a real Issue
opens with the correct title/body/labels, and an ungrounded finding does
not open one. Only the "orphaned" category is wired up here - grounding.py
only validates that category so far, and adding a new category to this
module means adding its grounding check first, not the other way around.
"""

from pathlib import Path
from typing import Any

from access_review_agent.github.adapter import GitHubAdapter, IssueResult, get_adapter
from access_review_agent.grounding import validate_finding

CATEGORY_TITLES = {
    "orphaned": "Orphaned access",
}

SYSTEM_DISPLAY_NAMES = {
    "aws": "AWS",
    "github": "GitHub",
    "salesforce": "Salesforce",
    "finance_erp": "Finance ERP",
    "vpn": "VPN",
}


def _format_title(finding: dict[str, Any]) -> str:
    category = finding["category"]
    system_name = finding["system_name"]
    identity = finding.get("employee_name") or finding["employee_id"]
    category_display = CATEGORY_TITLES.get(category, category)
    system_display = SYSTEM_DISPLAY_NAMES.get(system_name, system_name)
    return f"{category_display} — {identity} ({system_display})"


def _format_body(finding: dict[str, Any]) -> str:
    source = finding["source_record"]
    lines = [
        f"**Access detail:** {finding['access_level']} access to {finding['system_name']}",
        f"**Expected per policy:** {finding['expected_per_policy']}",
    ]

    if finding["category"] == "orphaned":
        lines.append(f"**Date detected:** {finding['date_detected']}")
        lines.append(
            "**Time to revoke:** same day as detection (Orphaned SLA — "
            "access-control-policy.md, Operational review)"
        )

    lines.append(
        f"**Source record:** `{source['file']}`, row matching "
        f"`employee_id={source['employee_id']}`"
    )
    return "\n\n".join(lines)


def _format_labels(finding: dict[str, Any]) -> list[str]:
    category_label = finding["category"]
    system_label = finding["system_name"].replace("_", "-")
    return [category_label, system_label]


def open_issue(finding: dict[str, Any], repo_full_name: str, data_dir: Path) -> IssueResult:
    """Validate `finding` against source data (the grounding gate), then
    open a GitHub Issue for it via the dry-run-capable adapter.

    Raises GroundingError (from grounding.py) without opening anything if
    the finding doesn't hold up against data_dir's source records.
    """
    validate_finding(finding, data_dir)

    adapter: GitHubAdapter = get_adapter()
    return adapter.create_issue(
        repo_full_name=repo_full_name,
        title=_format_title(finding),
        body=_format_body(finding),
        labels=_format_labels(finding),
    )
