# Tech Debt

Known code-quality and architecture issues, tracked separately from GitHub Issues since this repo's own Issue tracker is the live audit-evidence trail (README.md) once the demo timeline runs against it, not an engineering backlog — mixing the two would muddy exactly the thing that tracker needs to stay trustworthy for.

Sourced from an EM-level code review (two lanes: architecture/code quality, testing/security/ops) run against the codebase as it stood after Milestone 11 and the docs/comments-brevity passes. The one Blocking finding from that review (no exception handling around real GitHub write calls) is already fixed — see `orchestrator.py`/`lifecycle.py` and PR #30. Everything below is real but non-blocking.

Reviewed periodically, not necessarily kept perfectly live between passes — check items off as they're fixed; re-audit occasionally for staleness the same way the other docs were tonight.

## High

- [x] ~~No `Finding` type~~ — **Done** (`finding.py`, `Finding` `TypedDict`). Note the claim above overstated it: with no type checker wired into CI, this doesn't "remove a correctness risk" the way it first sounded — nothing catches a typo at merge time either way, before or after. What it actually buys: live editor/language-server feedback while writing code, and one place that documents the real shape across all six categories instead of that shape being implicit and scattered across six files. Considered a dataclass (matches every other structured shape in this codebase) but deferred it — would mean rewriting every `finding["x"]` access across `detection/*.py`, `grounding.py`, `github/issues.py`, and `orchestrator.py` for the same non-enforced benefit; a `TypedDict` needed zero call-site changes.
- [ ] **`run_full_reconciliation` is a god function** (~100 lines: dedup-key construction, per-system detection loop, identity resolution, issue-opening, remediation re-check, lifecycle checks, three nested try/except levels), returning an untyped dict whose shape has to be hand-documented in prose because the type system can't express it. Decompose into named helpers; consider a dataclass for the return shape.
- [x] ~~The Agent-SDK query→extract-result boilerplate is duplicated verbatim in three places~~ — **Done** (`agent_sdk.run_query`, used by `narrative.py`'s synthesis/judge calls and `detection/identity_resolution.py`'s `_query_resolution`).

## Medium

- [ ] `orchestrator.py` mixes unrelated concerns at the module level (push-triggered reconciliation, monthly reports, quarterly reports, and Release creation all in one file) — worth splitting by concern.
- [ ] All five `detection/*.py` modules duplicate the same ~5-line data-loading preamble (load access rows + HRIS rows + build `hris_by_id`) and the same `source_record` construction, verbatim. The modules are otherwise admirably consistent in shape — this is the one place that consistency should have become a shared helper instead of copy-paste.
- [ ] No config-shape validation for YAML inputs, unlike CSVs' `REQUIRED_COLUMNS` check (`tools/access_data.py`, `tools/hris.py`). A malformed `policy-config.yaml` fails with a bare `KeyError` deep inside an unrelated function rather than a clear boundary error.
- [ ] `run_full_reconciliation`'s `check_lifecycle` flag now silently gates three unrelated behaviors (Escalation/Accepted-Risk checks, duplicate-Issue prevention, remediation re-check) — the name undersells what it controls; worth a rename or splitting into independently-controllable flags.
- [ ] No caching on `read_policy()` (re-parses YAML from disk on every call, invoked per-finding/per-category) or on `RealAdapter`'s `get_repo()` calls (fresh API call in every method — an N+1 pattern in `lifecycle.py`'s per-issue loops). Invisible at demo scale, real at production scale.
- [ ] The CI-wired eval suite's "credential-free" guarantee is an *emergent* property of fixture content (no fixture happens to contain a dangling `employee_id`), not an *enforced* one — no test asserts `cost_usd == 0` or mocks the Agent SDK call directly. Currently safe only because `ANTHROPIC_API_KEY` genuinely isn't set as a CI secret (confirmed) — an accidental safety net, not a designed one. Harden with an explicit assertion or mock in one of the `verify_*.py` scripts.

## Low

- [ ] `grounding.py::_validate_drift` has a stray mid-function `import json`, inconsistent with every other module's top-of-file imports.
- [ ] Minor type-hint gaps: `_build_release_payload`'s `all_issues: list` (no type param), `make_read_access_data_tool`/`make_read_hris_tool` missing return type annotations.
- [ ] `grounding.py`'s `_validate_dormant_admin`/`_validate_dormant_ad_hoc` duplicate the days-dormant recomputation almost verbatim.
- [ ] `production.yml`'s "Determine changed files" step interpolates `${{ github.event.before }}`/`${{ github.sha }}` directly into a shell block, inconsistent with every other workflow's careful `env:`-routing that the repo's own comments call out as the fix for exactly this pattern. Low actual risk (both values are GitHub-computed SHAs, not attacker text) but worth matching the established style.
- [ ] `claude-agent-sdk>=0.1.0` has no upper bound in `pyproject.toml`, for a pre-1.0 SDK this project has already hit one real silent-breakage gotcha with (see `reference/milestone-6-agent-sdk-patterns/README.md`).
- [ ] `.env.example` documents `ANTHROPIC_API_KEY` but not `GITHUB_TOKEN`/`GITHUB_WRITE_MODE`, a minor local-onboarding gap.
- [ ] Unconfirmed: possibly no eval case covers one access record simultaneously tripping two categories at once (e.g. dormant-admin *and* unapproved on the same row) — detection functions run independently per category and the orchestrator just concatenates findings. Worth a quick check, not a confirmed gap.
