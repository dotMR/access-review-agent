"""Risk Assessment (SPEC.md §5, Milestone 8): a deterministic scoring
layer (Impact/Likelihood/Risk Rating lookups) and a genuine-synthesis
layer (narrative), kept deliberately separate — the tables are
reproducible from fixed inputs, the narrative is real reasoning over
them, and conflating the two would make neither easy to verify on its
own terms.

read_prior_report (SPEC.md §3) is a local file read from the repo
checkout, not a GitHub API call — it parses a previously-committed report
file (Milestone 7's own output) back into {category: {issue_numbers}},
reusing the fact that Issue format was designed to mirror report columns
the same way grounding.py and reports.py already do, just one level up
(report file, not Issue body).
"""

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from access_review_agent.github.adapter import IssueInfo
from access_review_agent.reports import CATEGORY_DISPLAY, category_of, parse_issue_body, parse_issue_title, status_of
from access_review_agent.tools.policy import DEFAULT_POLICY_CONFIG_PATH, read_policy


@dataclass
class FindingSummary:
    issue_number: int
    identity: str
    status: str  # Open / Remediated / Accepted risk
    consecutive_periods: int  # audits this finding has appeared in, including this one


@dataclass
class RiskAssessmentEntry:
    category: str
    system_name: str
    likelihood: str
    impact: str
    risk_rating: str
    findings: list[FindingSummary]

# VPN's binary none/granted access level (see the earlier role-access-mapping.yaml
# fix) doesn't map onto the Impact table's read/write/admin axis at all -
# that axis predates VPN's own vocabulary. Deliberate simplification,
# decided explicitly rather than left implicit: "granted" is treated as
# write-equivalent - active/interactive access, not read-only, but not
# elevated/administrative either.
ACCESS_LEVEL_FOR_IMPACT = {"read": "read", "write": "write", "admin": "admin", "granted": "write"}


def parse_report_issue_numbers(content: str) -> dict[str, set[int]]:
    """Parse a per-system report file back into {category: {issue_numbers}} -
    which categories had findings, and which specific Issues, in that
    period's report. Used for quarterly-recurrence counting only, not for
    re-deriving full finding detail (reports.py's parse_issue_body does
    that, from the live Issue itself, not from a report snapshot).
    """
    display_to_category = {v: k for k, v in CATEGORY_DISPLAY.items()}
    result: dict[str, set[int]] = {}
    sections = re.split(r"^### (.+)$", content, flags=re.MULTILINE)
    for i in range(1, len(sections), 2):
        header, body = sections[i], sections[i + 1]
        category = next((key for display, key in display_to_category.items() if header.startswith(display)), None)
        if category is None:
            continue
        result[category] = {int(n) for n in re.findall(r"\[#(\d+)\]", body)}
    return result


def read_prior_report(checkout_dir: Path, period: str, system_name: str) -> dict[str, set[int]] | None:
    """Local file read of a past per-system report (SPEC.md §3) - not a
    GitHub API call. None if that period's report doesn't exist yet
    (e.g. this is the first quarter, or an earlier gap).
    """
    path = checkout_dir / "reports" / period / f"{system_name}.md"
    if not path.exists():
        return None
    return parse_report_issue_numbers(path.read_text())


_GENERATED_AT_RE = re.compile(r"^- \*\*Report generated:\*\* (\S+)", re.MULTILINE)


def read_prior_report_generated_at(checkout_dir: Path, period: str) -> datetime | None:
    """The immediately preceding period's own aggregate report's real
    "Report generated" timestamp - None if that period's report doesn't
    exist yet (e.g. this is the first quarter).

    Used to scope Risk Assessment to genuinely-this-quarter findings
    (SPEC.md §5) without comparing against period_bounds' SIMULATED
    calendar quarter boundaries, which real closed_at timestamps can't
    be trusted against outside of real, un-simulated production use: a
    live trial that simulates three quarters within a single real day
    (Milestone 12) closes issues with real "today" timestamps regardless
    of which simulated quarter they represent, so a wall-clock-only
    check can't tell "closed during simulated Q2" from "closed during
    simulated Q3" - they're both really today. Comparing against the
    PRIOR period's own report-generation moment instead asks a real,
    sequential question with no simulated calendar involved at all: did
    this closure happen after the last time we generated a report for
    the prior period, or before it (already covered there, whatever
    simulated period is nominally in effect). Correct in genuine
    production too, where periods advance in real time anyway.
    """
    path = checkout_dir / "reports" / previous_period(period) / "aggregate.md"
    if not path.exists():
        return None
    match = _GENERATED_AT_RE.search(path.read_text())
    return datetime.fromisoformat(match.group(1)) if match else None


def previous_period(period: str) -> str:
    year_str, q_str = period.split("-Q")
    year, quarter = int(year_str), int(q_str)
    if quarter == 1:
        return f"{year - 1}-Q4"
    return f"{year}-Q{quarter - 1}"


_TOTAL_ROW_RE = re.compile(
    r"^\|\s*\*\*Total\*\*\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|", re.MULTILINE
)


def read_period_history(checkout_dir: Path, period: str) -> list[dict[str, int | str]]:
    """Every earlier period's own {period, open, remediated, accepted_risk,
    total} - parsed back out of each period's already-committed aggregate
    report's "Resolution status by system" Total row (a local file read,
    not a GitHub API call - same "reuse what's already there" discipline
    as read_prior_report), walking backward from `period` until a
    period's aggregate report doesn't exist yet. Returned oldest-first,
    for the Trend section's multi-quarter table - `period`'s own row
    isn't included here, since it's still being built by the same call
    that needs this history, not yet committed to disk.
    """
    history: list[dict[str, int | str]] = []
    walk = period
    while True:
        walk = previous_period(walk)
        path = checkout_dir / "reports" / walk / "aggregate.md"
        if not path.exists():
            break
        match = _TOTAL_ROW_RE.search(path.read_text())
        if not match:
            break
        open_n, remediated_n, accepted_n, total_n = (int(x) for x in match.groups())
        history.append(
            {"period": walk, "open": open_n, "remediated": remediated_n, "accepted_risk": accepted_n, "total": total_n}
        )
    history.reverse()
    return history


def period_bounds(period: str) -> tuple[str, str]:
    """[start, end) ISO date strings for a "YYYY-Qn" period - the
    quarter's first day and the day after its last, so a timestamp string
    comparison (start <= ts < end) is enough to place a moment inside or
    outside it. Used by generate_quarterly_reports's Escalations-this-
    period filtering - see that function's own docstring for why.
    """
    year_str, q_str = period.split("-Q")
    year, quarter = int(year_str), int(q_str)
    start_month = (quarter - 1) * 3 + 1
    start = f"{year:04d}-{start_month:02d}-01"
    if start_month == 10:
        end = f"{year + 1:04d}-01-01"
    else:
        end = f"{year:04d}-{start_month + 3:02d}-01"
    return start, end


def count_consecutive_periods(
    issue_number: int,
    category: str,
    current_period: str,
    checkout_dir: Path,
    system_name: str,
    max_lookback: int = 2,
) -> int:
    """How many consecutive periods, ending at current_period, has this
    Issue appeared in `category`'s section of the system's report? Always
    at least 1 - the caller only calls this for Issues actually present
    in the current period's own data. Capped at max_lookback+1 (3 by
    default) since Likelihood only distinguishes 1 / 2 / 3+, not exact
    counts beyond that.
    """
    count = 1
    period = current_period
    for _ in range(max_lookback):
        period = previous_period(period)
        prior = read_prior_report(checkout_dir, period, system_name)
        if prior is None or issue_number not in prior.get(category, set()):
            break
        count += 1
    return count


def likelihood_from_consecutive_periods(count: int) -> str:
    if count <= 1:
        return "Low"
    if count == 2:
        return "Medium"
    return "High"


def compute_impact(system_criticality: str, access_level: str) -> str:
    """Direct lookup, not a formula (ADR-0002) - System Criticality x
    Access Level -> Impact.
    """
    matrix = read_policy(DEFAULT_POLICY_CONFIG_PATH)["risk_assessment"]["impact_matrix"]
    mapped_level = ACCESS_LEVEL_FOR_IMPACT[access_level]
    return matrix[system_criticality.lower()][mapped_level].capitalize()


def compute_risk_rating(likelihood: str, impact: str) -> str:
    """Direct lookup, not a formula (ADR-0002) - Likelihood x Impact ->
    Risk Rating. "Critical" is reachable only here, never as an Impact
    value on its own.
    """
    matrix = read_policy(DEFAULT_POLICY_CONFIG_PATH)["risk_assessment"]["risk_rating_matrix"]
    return matrix[likelihood.lower()][impact.lower()].capitalize()


_ACCESS_LEVEL_RE = re.compile(r"`?(\w+)`?")
ACCESS_LEVEL_SEVERITY = {"read": 1, "granted": 2, "write": 2, "admin": 3}


def _extract_access_level(access_detail: str) -> str:
    """access_detail is parse_issue_body's whole-line value (e.g.
    "`write` access to aws") - pull out just the leading access-level
    token.
    """
    match = _ACCESS_LEVEL_RE.match(access_detail)
    return match.group(1) if match else access_detail


def build_risk_assessment_entries(
    system_name: str,
    issues: list[IssueInfo],
    period: str,
    checkout_dir: Path,
    system_criticality: str,
) -> list[RiskAssessmentEntry]:
    """One entry per category with at least one Finding this quarter for
    this system (SPEC.md §5's "one entry per (category, system) pair").
    Groups `issues` by category, computes each finding's own recurrence
    count - always 1 for a currently-remediated finding, regardless of
    how many periods it was open before being fixed, since a resolved
    finding isn't "recurring" - then the entry's overall Likelihood (the
    max across its findings - the most persistent finding governs the
    category+system's rating) and Impact (the highest access level among
    its findings - worst-case exposure governs), and the Risk Rating
    from those two.
    """
    by_category: dict[str, list[IssueInfo]] = {}
    for issue in issues:
        category = category_of(issue)
        if category is None:
            continue
        by_category.setdefault(category, []).append(issue)

    entries = []
    for category, category_issues in by_category.items():
        findings = []
        max_consecutive = 1
        max_access_level = "read"
        for issue in category_issues:
            fields = parse_issue_body(issue.body)
            access_level = _extract_access_level(fields.get("access_detail", ""))
            # A remediated finding is resolved, full stop - "recurring"
            # only means something for a still-live problem (Open or
            # Accepted risk). Skipping the backward-walk here rather than
            # teaching it about status: an Issue can never legitimately
            # go Remediated -> Open again under the same number (a later
            # recurrence of the same problem gets a fresh Issue - the
            # duplicate-Issue-prevention design's own "a fixed-then-later-
            # recurring finding is a genuinely new instance" rule), so
            # count_consecutive_periods's own multi-period walk is only
            # ever meaningful for an issue that's still open right now.
            if status_of(issue) == "Remediated":
                consecutive = 1
            else:
                consecutive = count_consecutive_periods(issue.number, category, period, checkout_dir, system_name)
            findings.append(
                FindingSummary(
                    issue_number=issue.number,
                    identity=parse_issue_title(issue.title),
                    status=status_of(issue),
                    consecutive_periods=consecutive,
                )
            )
            max_consecutive = max(max_consecutive, consecutive)
            if ACCESS_LEVEL_SEVERITY.get(access_level, 0) > ACCESS_LEVEL_SEVERITY.get(max_access_level, 0):
                max_access_level = access_level

        likelihood = likelihood_from_consecutive_periods(max_consecutive)
        impact = compute_impact(system_criticality, max_access_level)
        risk_rating = compute_risk_rating(likelihood, impact)
        entries.append(
            RiskAssessmentEntry(
                category=category,
                system_name=system_name,
                likelihood=likelihood,
                impact=impact,
                risk_rating=risk_rating,
                findings=findings,
            )
        )
    return entries
