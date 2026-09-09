"""Report rendering: per-system and aggregate, SPEC.md §6.

Reports are downstream rendering of already-gated Issue data (Milestone
7's own "Proves" line) - not a fresh detection re-run. By the time the
quarterly trigger fires, push-triggered runs have already opened Issues
throughout the quarter (SPEC.md §2); the quarterly report just rolls that
existing Issue-tracker state up via list_issues, parsing each Issue's
title/body back into the same fields _format_body wrote them from -
Issue format (SPEC.md §4) was deliberately designed to mirror the report
table's own columns ("reuses each category's own report-row columns...
rather than a separate, invented convention") for exactly this reuse, not
as an ad hoc parsing shortcut.

The Escalations section still renders as an explicit "not yet
implemented" placeholder, not an empty table - it depends on Milestone 9,
which doesn't exist yet. Rendering an empty table would falsely imply the
computation ran and found nothing; it never ran at all. Risk Assessment
(Milestone 8) follows the same discipline for any *caller* that doesn't
supply `risk_assessment_rows` - the placeholder always describes "not
provided for this call," never "not built," once the feature exists.
"""

import re
from typing import Any

from access_review_agent.github.adapter import IssueInfo

CATEGORY_ORDER = [
    "orphaned",
    "dormant-admin",
    "unapproved",
    "identity-resolution",
    "drift",
    "dormant-ad-hoc",
]
CATEGORY_DISPLAY = {
    "orphaned": "Orphaned access",
    "dormant-admin": "Dormant admin-level access",
    "unapproved": "Unapproved access",
    "identity-resolution": "Identity resolution",
    "drift": "Drift",
    "dormant-ad-hoc": "Dormant ad-hoc access",
}
SYSTEM_ORDER = ["aws", "github", "salesforce", "finance_erp", "vpn"]
SYSTEM_DISPLAY = {
    "aws": "AWS",
    "github": "GitHub",
    "salesforce": "Salesforce",
    "finance_erp": "Finance ERP",
    "vpn": "VPN",
}
SYSTEM_LABEL = {name: name.replace("_", "-") for name in SYSTEM_ORDER}

MODEL_NOTE = (
    "Tier 1 (Orphaned, Dormant admin-level, Dormant ad-hoc, Unapproved, Drift): "
    "plain Python, no model call (ADR-0006). Tier 2 (Identity resolution): "
    "claude-haiku-4-5-20251001 via the Agent SDK."
)

NOT_YET_IMPLEMENTED = "_Not yet implemented — lands in {milestone}. No rows below are a real computation._"
RISK_ASSESSMENT_NOT_PROVIDED = (
    "_No Risk Assessment data provided for this report (risk_assessment_rows was not "
    "passed to build_aggregate_report). No rows below are a real computation._"
)


class _MissingFieldAsNA(dict):
    """A row missing an expected field - e.g. an older Issue whose body
    predates a _format_body field-set change - renders "N/A" for that
    cell rather than crashing report generation entirely.
    """

    def __missing__(self, key: str) -> str:
        return "N/A"


def status_of(issue: IssueInfo) -> str:
    if issue.state == "open":
        return "Open"
    return "Accepted risk" if "accepted-risk" in issue.labels else "Remediated"


def category_of(issue: IssueInfo) -> str | None:
    return next((label for label in issue.labels if label in CATEGORY_DISPLAY), None)


def parse_issue_title(title: str) -> str:
    """Extract the identity/identifier from a title of the form
    "{Category} — {identity} ({System})" (SPEC.md §4).
    """
    match = re.match(r"^.+? — (.+) \(.+\)$", title)
    return match.group(1) if match else title


def parse_issue_body(body: str) -> dict[str, str]:
    """Parse an Issue body written by github/issues.py's _format_body back
    into a field dict, keyed by a normalized version of each bolded label.
    """
    fields: dict[str, str] = {}
    role_changes: list[str] = []
    for line in body.split("\n\n"):
        match = re.match(r"^\*\*(.+?):\*\*\s*(.*)$", line.strip(), re.DOTALL)
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()
        if key.startswith("Role change"):
            role_changes.append(f"{key.replace('Role change', '').strip(' ()')}: {value}")
        else:
            normalized = re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")
            fields[normalized] = value
    if role_changes:
        fields["role_changes"] = "; ".join(role_changes)
    return fields


def _counts_table(issues: list[IssueInfo], rows: list[tuple[str, str]]) -> list[str]:
    """Render a Category | Open | Remediated | Accepted risk | Total table
    for `rows` (label, display_name) pairs, plus a Total row.
    """
    lines = ["| Category | Open | Remediated | Accepted risk | Total |", "| :-- | --: | --: | --: | --: |"]
    total = {"open": 0, "remediated": 0, "accepted": 0}
    for label, display in rows:
        matching = [i for i in issues if label in i.labels]
        open_n = sum(1 for i in matching if status_of(i) == "Open")
        remediated_n = sum(1 for i in matching if status_of(i) == "Remediated")
        accepted_n = sum(1 for i in matching if status_of(i) == "Accepted risk")
        total["open"] += open_n
        total["remediated"] += remediated_n
        total["accepted"] += accepted_n
        lines.append(f"| {display} | {open_n} | {remediated_n} | {accepted_n} | {len(matching)} |")
    grand_total = total["open"] + total["remediated"] + total["accepted"]
    lines.append(
        f"| **Total** | {total['open']} | {total['remediated']} | {total['accepted']} | {grand_total} |"
    )
    return lines


def _escape_table_cell(value: str) -> str:
    """Escape a value parsed from an Issue's title/body for safe embedding
    in a Markdown table cell. Issues are editable by anyone with write
    access to this repo's Issues, not just the agent that originally
    opened them - the same untrusted-content risk github/issues.py's
    _as_literal() defends against when *writing* an Issue body applies
    here too when *reading* one back into a report. A literal `|`
    would also break the table's column structure regardless of mention/
    reference risk, so it's escaped unconditionally, not just wrapped.
    """
    value = value.replace("|", "\\|")
    # Single-pass substitution, not chained .replace() calls: both
    # replacement strings ("&#64;", "&#35;") themselves contain "#", so
    # a second .replace("#", ...) pass would corrupt the first
    # substitution's own output. re.sub with a callback only matches
    # against the original text, never re-scans what it just inserted.
    return re.sub(r"[@#]", lambda m: {"@": "&#64;", "#": "&#35;"}[m.group()], value)


def _finding_rows(issues: list[IssueInfo], category: str) -> list[dict[str, Any]]:
    rows = []
    for issue in issues:
        if category_of(issue) != category:
            continue
        fields = {k: _escape_table_cell(v) for k, v in parse_issue_body(issue.body).items()}
        rows.append(
            {
                "identity": _escape_table_cell(parse_issue_title(issue.title)),
                "status": status_of(issue),
                "issue_number": issue.number,
                "issue_url": issue.html_url,
                **fields,
            }
        )
    return rows


def _render_category_section(title: str, header: str, row_fmt: str, rows: list[dict[str, Any]]) -> list[str]:
    lines = [f"### {title}", "", header]
    if not rows:
        header_row = header.split("\n", 1)[0]
        n_columns = header_row.count("|") - 1
        lines.append("| No findings" + " |" * (n_columns - 1) + " |")
    else:
        for row in rows:
            lines.append(row_fmt.format_map(_MissingFieldAsNA(row)))
    lines.append("")
    return lines


def build_per_system_report(
    system_name: str,
    period: str,
    issues: list[IssueInfo],
    generated_at: str,
    data_snapshot_ref: str = "N/A (manual/local run)",
    asset_owner_name: str = "TBD",
) -> str:
    """One per-system evidentiary report (SPEC.md §6). `issues` should
    already be filtered to this system (the caller does that once via
    list_issues + label filtering, not per category).
    """
    system_display = SYSTEM_DISPLAY[system_name]
    lines = [
        f"# Access Review — {system_display} — {period}",
        "",
        f"**Report generated:** {generated_at}",
        f"**Data snapshot:** {data_snapshot_ref}",
        f"**Model:** {MODEL_NOTE}",
        f"**Reporting period:** {period}",
        f"**Asset Owner:** {asset_owner_name}",
        f"**Committed to:** `reports/{period}/{system_name}.md`",
        "",
        "One of these is generated per Information System (AWS, GitHub, Salesforce, "
        "Finance ERP, VPN) each quarter. This is the line-item evidence; the "
        "aggregated Quarterly Audit Report links to these rather than repeating "
        "their contents.",
        "",
        "## Summary",
        "",
    ]
    lines += _counts_table(issues, [(c, CATEGORY_DISPLAY[c]) for c in CATEGORY_ORDER])
    lines += ["", "## Findings", ""]

    lines += _render_category_section(
        "Orphaned access",
        "| Identity | Access detail | Expected per policy | Date detected | Time to revoke | Status | Issue |\n"
        "| :-- | :-- | :-- | :-- | :-- | :-- | :-- |",
        "| {identity} | {access_detail} | {expected_per_policy} | {date_detected} | {time_to_revoke} | "
        "{status} | [#{issue_number}]({issue_url}) |",
        _finding_rows(issues, "orphaned"),
    )
    lines += _render_category_section(
        "Dormant admin-level access (90-day threshold)",
        "| Identity | Access detail | Expected per policy | Last used | Days dormant | Status | Issue |\n"
        "| :-- | :-- | :-- | :-- | :-- | :-- | :-- |",
        "| {identity} | {access_detail} | {expected_per_policy} | {last_used} | {days_dormant} | "
        "{status} | [#{issue_number}]({issue_url}) |",
        _finding_rows(issues, "dormant-admin"),
    )
    lines += _render_category_section(
        "Unapproved access",
        "| Identity | Access detail | Expected per policy | Date granted | Approved by | Status | Issue |\n"
        "| :-- | :-- | :-- | :-- | :-- | :-- | :-- |",
        "| {identity} | {access_detail} | {expected_per_policy} | {date_granted} | {approved_by} | "
        "{status} | [#{issue_number}]({issue_url}) |",
        _finding_rows(issues, "unapproved"),
    )
    lines += _render_category_section(
        "Identity resolution",
        "| Access record (`employee_id` or local identifier) | Access detail | Resolution | "
        "Evidence cited | Date detected | Status | Issue |\n| :-- | :-- | :-- | :-- | :-- | :-- | :-- |",
        "| {identity} | {access_detail} | {resolution_outcome} | {evidence} | {date_detected} | "
        "{status} | [#{issue_number}]({issue_url}) |",
        _finding_rows(issues, "identity-resolution"),
    )
    lines += _render_category_section(
        "Drift",
        "| Identity | Access detail | Expected per policy | Role changed | Status | Issue |\n"
        "| :-- | :-- | :-- | :-- | :-- | :-- |",
        "| {identity} | {access_detail} | {expected_per_policy} | {role_changes} | "
        "{status} | [#{issue_number}]({issue_url}) |",
        _finding_rows(issues, "drift"),
    )
    lines += _render_category_section(
        "Dormant ad-hoc access (180-day threshold)",
        "| Identity | Access detail | Expected per policy | Last used | Days dormant | Status | Issue |\n"
        "| :-- | :-- | :-- | :-- | :-- | :-- | :-- |",
        "| {identity} | {access_detail} | {expected_per_policy} | {last_used} | {days_dormant} | "
        "{status} | [#{issue_number}]({issue_url}) |",
        _finding_rows(issues, "dormant-ad-hoc"),
    )

    lines += [
        "## Sign-off",
        "",
        f"I attest that the findings above for {system_display} have been reviewed and, "
        "where applicable, remediated or formally accepted as risk.",
        "",
        f"**Asset Owner:** {asset_owner_name}",
        "**Date:** _(pending sign-off)_",
        "",
    ]
    return "\n".join(lines)


def build_aggregate_report(
    period: str,
    per_system_issues: dict[str, list[IssueInfo]],
    generated_at: str,
    data_snapshot_ref: str = "N/A (manual/local run)",
    trend_note: str = "N/A, no prior period",
    reviewer_name: str = "TBD",
    risk_assessment_rows: list[dict[str, Any]] | None = None,
) -> str:
    """`risk_assessment_rows`, when given, is a list of {category,
    system_name, likelihood, impact, risk_rating, narrative} dicts
    (Milestone 8) — one per (category, system) pair with at least one
    Finding this quarter. None (the default) renders the "not yet
    implemented" placeholder, matching Milestone 7's behavior for a
    caller that hasn't computed Risk Assessment at all.
    """
    all_issues = [i for issues in per_system_issues.values() for i in issues]
    total_findings = len(all_issues)
    n_remediated = sum(1 for i in all_issues if status_of(i) == "Remediated")
    n_open = sum(1 for i in all_issues if status_of(i) == "Open")
    n_accepted = sum(1 for i in all_issues if status_of(i) == "Accepted risk")

    lines = [
        f"# Quarterly Access Review Audit Report — {period}",
        "",
        "**Report generated:** " + generated_at,
        f"**Data snapshot:** {data_snapshot_ref}",
        f"**Model:** {MODEL_NOTE}",
        f"**Reporting period:** {period}",
        "**Systems in scope:** AWS, GitHub, Salesforce, Finance ERP, VPN",
        "**ISO 27001:2022 controls addressed:** A.5.15 (Access control), A.5.16 (Identity "
        "management), A.5.18 (Access rights), A.8.2 (Privileged access rights)",
        "**SOC 2 Common Criteria addressed:** CC6.1 (Logical access controls), CC6.2 "
        "(Access provisioning and de-provisioning), CC6.3 (Role-based access, least "
        "privilege, and segregation of duties)",
        f"**Committed to:** `reports/{period}/aggregate.md`",
        "",
        "This is the formal audit-evidence record for the period, the rollup of the "
        "five per-system reports below. It does not repeat their line-item findings, "
        "only aggregates and links to them, so the two can never drift out of sync "
        "with each other.",
        "",
        "## Executive summary",
        "",
        f"{total_findings} findings identified this quarter across {len(CATEGORY_ORDER)} finding "
        f"categories and {len(SYSTEM_ORDER)} Information Systems. {n_remediated} remediated, "
        f"{n_open} open, {n_accepted} accepted as risk. {trend_note}",
        "",
        "## Methodology",
        "",
        "The Access Review Agent performed an automated cross-reference of each "
        "Information System's access records (Access/IT System) against the HRIS and "
        "the Access Policy Repository, per the Operational review and Compliance "
        "review Principles in access-control-policy.md. Findings are categorized per "
        "policy: orphaned, dormant (admin-level), unapproved, identity resolution, "
        "and drift access.",
        "",
        "## Resolution status by system",
        "",
        "| System | Open | Remediated | Accepted risk | Total | Detail |",
        "| :-- | --: | --: | --: | --: | :-- |",
    ]
    for system_name in SYSTEM_ORDER:
        issues = per_system_issues.get(system_name, [])
        open_n = sum(1 for i in issues if status_of(i) == "Open")
        remediated_n = sum(1 for i in issues if status_of(i) == "Remediated")
        accepted_n = sum(1 for i in issues if status_of(i) == "Accepted risk")
        link = f"[{system_name.replace('_', '-')}.md](./{system_name.replace('_', '-')}.md)"
        lines.append(
            f"| {SYSTEM_DISPLAY[system_name]} | {open_n} | {remediated_n} | {accepted_n} | "
            f"{len(issues)} | {link} |"
        )
    lines.append(
        f"| **Total** | {n_open} | {n_remediated} | {n_accepted} | {total_findings} | |"
    )

    lines += ["", "## Findings by category (aggregate)", ""]
    lines += _counts_table(all_issues, [(c, CATEGORY_DISPLAY[c]) for c in CATEGORY_ORDER])[:-1]
    # drop the Total row here - SPEC's aggregate template has no Total row on this table
    lines += [
        "",
        "Line-item detail for every finding lives in the per-system reports linked "
        "above and in the Appendix, not here.",
        "",
        "## Risk Assessment",
        "",
    ]
    if risk_assessment_rows is None:
        lines += [RISK_ASSESSMENT_NOT_PROVIDED, ""]
    lines += [
        "| Category | System | Likelihood | Impact | Risk Rating | Narrative & treatment recommendation |",
        "| :-- | :-- | :-- | :-- | :-- | :-- |",
    ]
    if risk_assessment_rows:
        for row in risk_assessment_rows:
            lines.append(
                f"| {CATEGORY_DISPLAY[row['category']]} | {SYSTEM_DISPLAY[row['system_name']]} | "
                f"{row['likelihood']} | {row['impact']} | {row['risk_rating']} | "
                f"{_escape_table_cell(row['narrative'])} |"
            )
    lines += [
        "",
        "## Escalations this period",
        "",
        NOT_YET_IMPLEMENTED.format(milestone="Milestone 9"),
        "",
        "| Finding | System | Category | Open since | Escalated | Issue |",
        "| :-- | :-- | :-- | :-- | :-- | :-- |",
        "",
        "## Reviewer attestation",
        "",
        "I have reviewed this report and the underlying per-system reports, and "
        "accept this as the formal audit-evidence record for the period stated above.",
        "",
        f"**Security/Compliance Reviewer:** {reviewer_name}",
        "**Date:** _(pending sign-off)_",
        "",
        "## Appendix",
        "",
        "- Per-system reports: "
        + " · ".join(
            f"[{SYSTEM_DISPLAY[s]}](./{s.replace('_', '-')}.md)" for s in SYSTEM_ORDER
        ),
        f"- Data snapshot: {data_snapshot_ref}",
        "- PDF export: _not yet implemented (out of scope per SPEC.md §8's Deferred section)_",
        "",
        "---",
        "<!-- Out of scope (not shown in this report): Dormant admin-level's, Dormant "
        "ad-hoc's, and Drift's own monthly Operational/SLA variants, and the "
        "Unapproved-access grant-time gate — see SPEC.md §8. -->",
    ]
    return "\n".join(lines)
