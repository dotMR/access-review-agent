"""The `Finding` shape (SPEC.md §4): the central domain object every
detection module produces, `grounding.py` validates, and `github/
issues.py` renders into an Issue.

Until now this shape existed only implicitly, as a `dict[str, Any]`
constructed the same way independently in each of `detection/*.py`'s
five Tier 1 modules plus Identity resolution - inconsistent with every
other structured shape in this codebase (`IssueInfo`, `IssueResult`,
`RiskAssessmentEntry`, etc.), all of which are typed.

What this buys, honestly: this project has no type checker wired into
CI (no mypy/pyright config anywhere), so a `TypedDict` here catches
nothing at merge time - a typo'd key or wrong-shaped value still only
fails at runtime, exactly as it did before. What it actually gives you
is (1) live typo/shape feedback from whatever language server your
editor runs while you're writing the code, and (2) one place that
documents what a Finding actually contains across all six categories,
instead of that shape being implicit and scattered across six files'
dict literals. A dataclass (real attribute access, matching this
codebase's other structured shapes) was considered and deferred: every
existing `finding["x"]` dict literal and subscript access keeps working
unchanged under a `TypedDict`, where a dataclass would mean rewriting
all of them across `detection/*.py`, `grounding.py`, `github/issues.py`,
and `orchestrator.py` for the same non-enforced benefit.
"""

from typing import Any, NotRequired, TypedDict


class SourceRecord(TypedDict):
    file: str
    employee_id: str


class Finding(TypedDict):
    """Fields present on every Finding regardless of category, plus the
    category-specific extras (all optional - only the categories that
    use a given field set it). `employee_name` is itself optional: an
    Identity resolution Finding has no cleanly resolved employee name to
    give (SPEC.md §4), only the raw identifier already in `employee_id`.
    """

    category: str
    system_name: str
    employee_id: str
    access_level: str
    expected_per_policy: str
    date_detected: str
    source_record: SourceRecord

    # Orphaned, Dormant admin-level, Dormant ad-hoc, Unapproved, Drift
    employee_name: NotRequired[str]
    # Dormant admin-level, Dormant ad-hoc
    last_used_date: NotRequired[str]
    days_dormant: NotRequired[int]
    # Unapproved
    granted_date: NotRequired[str]
    approved_by: NotRequired[str | None]
    # Drift
    role_change_history: NotRequired[list[Any]]
    # Identity resolution
    resolution_outcome: NotRequired[str]
    evidence: NotRequired[str]
    claimed_owner_employee_id: NotRequired[str]
