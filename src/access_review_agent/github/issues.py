"""Issue formatting and creation: SPEC.md §4's Issue format, gated by the
grounding guardrail.

open_issue() is the function Milestone 2 proved: a real Issue opens with
the correct title/body/labels, and an ungrounded finding does not open
one. A category is wired up here only once grounding.py has its own
validator for it - adding a new category means adding its grounding
check first, not the other way around (Milestone 3 added the four
Tier 1 categories that came after Orphaned; Identity resolution and
Drift's Tier 2 reasoning-based cousins are not in scope until
Milestone 6 onward).
"""

from pathlib import Path
from typing import Any

from access_review_agent.github.adapter import GitHubAdapter, IssueResult, get_adapter
from access_review_agent.grounding import validate_finding

CATEGORY_TITLES = {
    "orphaned": "Orphaned access",
    "dormant-admin": "Dormant admin-level access",
    "dormant-ad-hoc": "Dormant ad-hoc access",
    "unapproved": "Unapproved access",
    "drift": "Drift",
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

    category = finding["category"]
    if category == "orphaned":
        lines.append(f"**Date detected:** {finding['date_detected']}")
        lines.append(
            "**Time to revoke:** same day as detection (Orphaned SLA — "
            "access-control-policy.md, Operational review)"
        )
    elif category in ("dormant-admin", "dormant-ad-hoc"):
        lines.append(f"**Last used:** {finding['last_used_date']}")
        lines.append(f"**Days dormant:** {finding['days_dormant']}")
    elif category == "unapproved":
        lines.append(f"**Date granted:** {finding['granted_date']}")
        lines.append(f"**Approved by:** {finding['approved_by'] or 'none on file'}")
    elif category == "drift":
        for change in finding["role_change_history"]:
            lines.append(
                f"**Role change ({change['date']}):** {change['old_role']} → {change['new_role']}"
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
