# Development Plan

**Status:** v1 complete — all 12 milestones built and merged. See Milestone 12 below for the live-trial story.

A walking-skeleton build order: every milestone is a working, end-to-end slice — never a component built in isolation and integrated later. Each one names what's built, what it proves, and which `eval-cases.md` cases become a required-passing gate before moving on. Small pieces, always testable, always real.

**Runtime: Python.** The Claude Agent SDK is officially available for Python and TypeScript only, with symmetric feature coverage — the SDK itself doesn't favor either. Python fits this project's actual workload better: `csv`/`pandas` for the core reconciliation logic, and mature HTML/Markdown-to-PDF rendering for the aggregate report's PDF export, versus TypeScript's thinner tabular-data tooling. GitHub API access uses a third-party library (PyGithub) rather than GitHub's own Octokit — a minor trade-off against the ecosystem fit on the other two points.

---

## Milestone 1 — Read one file, apply one deterministic check, print the result

Orphaned detection (AWS only) — an anti-join plus a status check, no thresholds. **Plain Python, no model call** (ADR-0006): a deterministic check gains nothing from an LLM. Output is a logged finding, not yet an Issue.

Also builds `validate_finding()` now, not in Milestone 2 — independently re-reads source data to confirm a claimed finding is true, defense-in-depth against bugs in detection itself. Building it now closes a real gap in this milestone's own eval gate: a finding matching `expected.json` for the wrong reason would otherwise still pass.

The production workflow stays deferred to Milestone 5 (needs dispatch/Issue-writing/reports that don't exist yet); the eval/CI workflow was held off until Tier 1's zero-model-call design removed the cost objection that originally blocked it.

**Proves:** the read-and-validate-and-detect pipeline works against real fixture data, with every finding independently confirmed against source data.
**Gate:** Tier 1 cases 1–3 (Orphaned) pass. Case 37 (grounding/citation) passes here too, moved up from Milestone 2.

## Milestone 2 — First real write: `open_issue`, reusing the grounding gate

Add `open_issue` (title/body/label format from `SPEC.md` §4), gated by Milestone 1's `validate_finding()` — reused unchanged. This is also where the local-vs-remote ADR gets formally filed: the design was already sketched in `iam-review-agent-design.md`, so filing it here is transcription plus whatever the real build surfaced. Dry-run adapter first, real GitHub API second.

**Proves:** the agent can write to a real external system, and the grounding guardrail gates that write path too, not just detection.
**Gate:** a real Issue opened against a scratch repo with correct title/body/labels (verified by hand); Tier 3 cases 37 and 41 pass automatically in CI via `scripts/run_milestone2.py`, dry-run only.

## Milestone 3 — Round out AWS's deterministic categories

Add Dormant admin-level, Dormant ad-hoc, Unapproved, Drift to `detection/` — same pure-Python pattern as Orphaned (ADR-0006). Adds `read_policy` (`tools/policy.py`), a generic YAML reader shared by `policy-config.yaml` and `role-access-mapping.yaml`. Each category lands with its own grounding validator and Issue-body fields in the same commit as its detection logic, not wired in as an afterthought.

The two dormancy categories' eval fixtures pin an explicit `as_of` date rather than comparing against `date.today()`, so a boundary case (89/90/91 days) doesn't silently start failing as wall-clock time passes it — `detect_dormant_admin`/`detect_dormant_ad_hoc` take `as_of` as an optional override, unset in production. The grounding gate follows the same discipline, recomputing day-counts from `last_used_date` and the finding's own `date_detected`, never `date.today()`.

**Proves:** the detection loop holds multiple check types without a redesign, and the write path genuinely generalizes past Orphaned.
**Gate:** Tier 1 cases 4–16 pass; the Issue-formatting case (41) passes for all five categories — `scripts/run_milestone3.py`, dry-run, no credentials.

## Milestone 4 — Isolation: expand to all five systems

Build the isolation architecture from ADR-0001: one shared read implementation, five pre-bound detection units (`units.py`'s `SystemDetectionUnit`), main agent as sole orchestrator/Issue-writer (`orchestrator.py`'s `run_full_reconciliation` — the only caller of `open_issue`). Still plain Python for all five systems; the isolation boundary is identical whether a unit's detection code is a Python function or, later, an LLM tool call. Still manually/locally triggered — no GitHub Actions yet.

The isolation check tries to break the boundary, not just assert it: each unit runs twice against a five-system fixture — once with all five files present, once with only its own file plus HRIS, the other four absent entirely. Identical findings both times is real evidence: a unit that depended on another system's file would raise `FileNotFoundError` in the isolated run, not quietly pass.

**Proves:** the isolation boundary is structural — a detection unit's data access provably cannot reach another system's file.
**Gate:** a targeted architecture check (not a numbered eval case), run via `scripts/run_milestone4.py`, dry-run, no credentials.

## Milestone 5 — Real trigger: GitHub Actions and the dispatch rule

Wire the push-triggered production workflow (`.github/workflows/production.yml`): single-system commits scope to one subagent, HRIS/policy/role-mapping commits fan out to all five, `access-control-policy.md` isn't in the trigger's paths at all. Least-privilege `GITHUB_TOKEN` scoping lands here too. `dispatch.py`'s `determine_dispatch()` is a pure function over a changed-file list, deliberately GitHub-Actions-agnostic — unit-tested locally and called for real from the workflow's git-diff step.

`GITHUB_WRITE_MODE` stays unset in the committed workflow (dry-run default, ADR-0007) — no `data/` directory exists yet. Verified as real CI behavior anyway: a throwaway branch pointed the workflow at the scratch repo, confirmed the trigger fires, dispatches correctly, and opens a real Issue there, then was closed without merging.

Also upgrades the Issue body's Source record citation to a clickable GitHub blob permalink — `open_issue`/`run_full_reconciliation` take an optional `commit_sha`, passed through from Actions' own `GITHUB_SHA`; eval/dry-run callers never pass one, so they keep the plain bare-filename citation.

**Proves:** the dispatch table is real CI behavior, not just a documented rule.
**Gate:** Tier 3 cases 25–28 pass — locally via `scripts/run_milestone5.py` and live via the throwaway-branch verification.

## Milestone 6 — Identity resolution: first reasoning capability

**The first point the Agent SDK is actually used** (ADR-0006) — nothing before this genuinely needed a model. Built the four-outcome resolution logic and its restraint property (decline to guess on insufficient/ambiguous evidence). `find_unresolved_candidates()` (the anti-join precondition) stays plain Python; only `resolve_identity()` does real reasoning, one Agent SDK call per candidate — `_build_finding()` constructs the rest of the Finding in Python rather than trusting the model to reproduce data it already knows.

**Model: Haiku 4.5**, chosen empirically — start cheap, verify, upgrade only if restraint proves unreliable. It didn't: all 7 cases (17–22 plus case 38, a prompt-injection attempt) passed on the first clean run, $0.0953 total.

**A pre-merge security review found one real gap**: the access record's own `identifier` was embedded directly into the user-turn prompt without being called out as untrusted the way `provisioning_note` was. Hardened the system prompt to name every incoming field untrusted, added a case targeting the identifier specifically, confirmed 8/8 pass before merging, not after.

`scripts/run_milestone6.py` is deliberately **not** wired into `eval.yml` — every run costs real money (~$0.10); run it locally/on-demand instead, a deliberate choice, not an oversight.

**Proves:** the system's first genuine LLM-reasoning step, with the citation/restraint discipline meant to make it safe to automate.
**Gate:** Tier 2 cases 17–22 pass; case 38 (input safety) verified. All via `scripts/run_milestone6.py`, run manually, not in CI.

## Milestone 7 — Reports: per-system and aggregate, `commit_report`

Built `commit_report` and the first read tool, `list_issues` — the first place the agent reads its own prior output back. `commit_report` reuses the same adapter/token/dry-run pattern as `open_issue`; `list_issues` always makes a real read (nothing to dry-run about a read with no side effect).

Report rendering (`reports.py`) parses each Issue's title/body back into fields rather than re-running detection, safe specifically because Issue format was deliberately designed to mirror the report table's own columns. A row missing an expected field (an older Issue predating a body-format change) renders "N/A" for that cell rather than crashing the report — found via a real older test Issue during manual verification.

The aggregate template's Risk Assessment and Escalations sections (Milestones 8/9, not built yet) render an explicit "not yet implemented" placeholder rather than an empty table or a silent omission. Manual verification also caught a real gap: Milestone 6's `_format_body` never wrote a "Date detected" line for `identity-resolution` — fixed.

`.github/workflows/quarterly-audit.yml` adds `workflow_dispatch` and `schedule` triggers, `GITHUB_WRITE_MODE` unset by default.

**Proves:** committed-file output works, not just Issue-based output.
**Gate:** manual inspection against the templates — reports are downstream rendering of already-gated Issue data, no new eval cases needed. Verified against real committed Issues on the scratch repo spanning all three states and five categories.

## Milestone 8 — Risk Assessment

Scoring tables (ADR-0002) and narrative synthesis, split across `risk_assessment.py` (deterministic Impact/Likelihood/Risk Rating lookups, `read_prior_report`, quarterly-recurrence counting) and `narrative.py` (the actual reasoning, plus the first LLM-as-judge grader). `read_prior_report` is a local file read, not a GitHub API call — parses a prior report back into `{category: {issue_numbers}}`, the same trick as Issue-body parsing, one level up. Recurrence counting caps at 3 (Likelihood only distinguishes 1/2/3+); a multi-finding entry takes the max Likelihood and highest-severity Impact across them.

**Real design call**: VPN's binary `none`/`granted` access level doesn't map onto the Impact table's `read`/`write`/`admin` axis. Decided explicitly: `granted` is treated as write-equivalent.

Model: Haiku 4.5 for both narrator and judge — 5/5 cases passed, $0.0395 total. The judge was checked for real discrimination, not rubber-stamping, by also grading a deliberately bad narrative and confirming it correctly failed, before trusting it against the real one.

**A second design call, surfaced mid-build**: narrative synthesis is a real Anthropic API call regardless of `GITHUB_WRITE_MODE`, and the quarterly workflow's `schedule` trigger was already live. Rather than let every scheduled run spend money silently, narrative generation got its own dedicated gate (`ENABLE_RISK_ASSESSMENT_NARRATIVE`), exposed only on `workflow_dispatch`, never on `schedule`. Deterministic scores are always computed either way; only the narrative text is gated.

`scripts/run_milestone8.py` is deliberately not wired into `eval.yml`, same reasoning as Milestone 6.

**Proves:** the second reasoning capability, and that deterministic scoring and genuine synthesis are correctly separated.
**Gate:** Tier 3 cases 29–31 (tables) pass deterministically; Tier 2 cases 23–24 (narrative) pass via LLM-as-judge. All via `scripts/run_milestone8.py`, manual, not in CI.

## Milestone 9 — Escalation and Accepted Risk lifecycle

Adds `close_issue`/`apply_label`/`add_comment` to the `GitHubAdapter`, and `lifecycle.py`: `close_accepted_risk_issues` and `escalate_overdue_issues`, both re-checking already-open Issues via `list_issues`, not detecting anything new.

**Real design call**: lifecycle checking runs unconditionally over every open Issue on every trigger, never scoped to just the systems a given push touched — Escalation's same-day SLA shouldn't depend on which system got a commit today. `run_full_reconciliation`'s return shape changed to `{"systems": {...}, "lifecycle": {...}}`, which broke and was fixed in three existing callers — a real regression the eval suite caught, not review.

Verified for real against the scratch repo: reopened a day-old closed Issue, confirmed escalation applies the label+comment (case 34) and fires only once (case 35), confirmed accepted-risk closes while preserving labels (case 36) — before building the permanent credential-free fixtures.

**Proves:** the Issue lifecycle semantics that took real back-and-forth to resolve are actually implemented as decided.
**Gate:** Tier 3 cases 34–36 pass, plus a same-day boundary case. Free/local, wired into `eval.yml`.

## Milestone 10 — Monthly Operational Flags

`generate_monthly_reports` calls the same `run_full_reconciliation` push-triggered runs use — real detection across all five systems, including lifecycle checks — then commits one monthly report per system listing every currently-open Finding. `.github/workflows/monthly-report.yml` mirrors `quarterly-audit.yml`'s pattern exactly.

**Concurrency, applied proactively**: `production.yml` and `monthly-report.yml` now share one `concurrency` group, since both call `run_full_reconciliation` with lifecycle checks and must never run concurrently with each other either — the same duplicate-escalation-comment risk Milestone 9's review caught, now closed across workflows too.

A real gap surfaced testing case 32: a dry-run `open_issue` doesn't create a real Issue, so a separate `list_issues` read afterward can never see it — not a bug, two different concerns. The eval case tests `run_full_reconciliation`'s own return value instead; `generate_monthly_reports` itself was verified manually against the real scratch repo first.

**Proves:** the quiet-system gap is actually closed, not just designed to be.
**Gate:** Tier 3 cases 32–33 pass, credentials genuinely mocked absent (the lesson from Milestone 9's CI regression, applied proactively this time). Wired into `eval.yml`.

## Milestone 11 — Partial failure, Release, publish gate

`run_full_reconciliation` wraps each system's `unit.detect_all()` in `try/except (FileNotFoundError, ValueError)`: a malformed source file is recorded as `"failed"` and the loop moves on, rather than aborting the run for all five systems. Both `run_production.py` and `generate_monthly_reports` surface any failure loudly (`::error::` annotation, non-zero exit) — but only after every other system's work has already completed.

**A real design call on PDF generation**: `SPEC.md` §8 had deferred PDF rendering out of scope, but this milestone's Gate needs a real seven-asset Release. Surfaced to the user rather than silently decided; built now with a lightweight, pure-Python solution (`markdown` + `xhtml2pdf`) — `pdf_export.render_pdf` renders the aggregate report's own already-generated Markdown, one more rendering of the same source of truth every other report already has.

**A serious, empirically-confirmed SSRF finding, caught before shipping**: a proactive security review found `_escape_table_cell` didn't HTML-escape `<`/`>`/`&` or neutralize Markdown's image syntax, so a crafted Issue could trigger a real outbound fetch through the new PDF-rendering path. Verified exploitable with a local test server (3/3 crafted payloads fired a real request); confirmed the standard `link_callback` mitigation doesn't block it. Fixed with a single-pass regex escape; re-ran the same test and confirmed zero requests afterward.

**The human-in-the-loop gate**: environment protection rules gate whole jobs, not steps, so `quarterly-audit.yml` split into `quarterly-report` (unrestricted) and a new `create-release` job gated behind a `quarterly-release-approval` environment. Release creation moved into a standalone `create_quarterly_release`, tagging whatever commit its own checkout is at (`git rev-parse HEAD`, since `github.sha` is stale by the time the gated job runs) rather than relying on cross-job state. Verified end-to-end against the scratch repo: a real tagged Release, all seven assets.

**Proves:** the last two guardrails (fail-loud completeness, human-in-the-loop) are real CI behavior.
**Gate:** Tier 3 case 39 passes, wired into `eval.yml`; a real tagged Release with all seven assets produced end-to-end.

## Milestone 12 — Full demo timeline replay

Ran `demo-timeline.md`'s seeding tool and every trigger (`production.yml`, `monthly-report.yml`, `quarterly-audit.yml`) for real against a separate scratch repo (`dotMR/access-review-agent-scratch`) with `GITHUB_WRITE_MODE=real` — the first time any write path, or the human-in-the-loop Release gate, ran against genuine GitHub state instead of the `DryRunAdapter`.

**Wiring gaps surfaced immediately.** `run_full_reconciliation` never called `detect_identity_resolution` — every live run silently produced zero Identity resolution findings. `monthly-report.yml` had `contents: read`, which would have 403'd on its first real commit. No eval fixture caught either, since all of them are single-shot checks against fresh data.

**Duplicate-Issue prevention needed building, then fixing twice more.** Re-running detection against unchanged data opened a second Issue for an already-open finding. The fix's own `system_of()` helper then broke the moment an Issue carried a third label (`accepted-risk`), producing a wrong dedup key. And accepted-risk Issues — closed, but still genuinely detected every run — weren't in the dedup set at all, re-surfacing a formally-reviewed finding as new.

**Remediation re-check/auto-close didn't exist.** `SPEC.md` §8 and `iam-review-agent-design.md`'s "Closing the loop" both described it, and `demo-timeline.md`'s own commit 12 depended on it — but Milestone 9 built Escalation and Accepted Risk and never this third mechanic. A still-open Issue whose access had genuinely been revoked just stayed open.

**An EM-style code review**, run deliberately to close out this milestone, found one Blocking gap: no exception handling on the write path (`open_issue`, `close_issue`, `apply_label`, `add_comment`) — a transient GitHub API failure on one finding would have aborted the entire run. Fixed the same way every other failure category already was: isolated per-item, loud, non-fatal. Remaining lower-priority findings are tracked in `tech-debt.md`.

**Three report-rendering bugs surfaced only once real multi-quarter data existed to render.** The aggregate report's Escalations-this-period table was hardcoded to a "not yet implemented" placeholder, months after Milestone 9 actually built Escalation. The Release body's own escalation count used a separate, non-period-aware computation that could — and did — disagree with the report's own table. The Executive Summary's trend line always read "N/A, no prior period," because nothing ever supplied it. Same lesson three times: a field that renders convincingly isn't the same as one that's actually computed.

**A sequencing lesson, not a code bug.** Q1's quarterly-audit trigger fired before `demo-timeline.md`'s own seeding commits were pushed, so Q1's report rolled up pre-existing verification-testing noise instead of the intended narrative. Quarterly reports have no date-scoping by design (correct for real production use, where each period runs once, in sequence) — so that contamination is now permanent across all three published Releases. Regenerating a published report against today's state was tried once, made things worse, and was abandoned: a past report isn't something this system reconstructs. Every mechanism itself is still genuinely proven working end-to-end; only this trial's specific Q1–Q3 story doesn't perfectly match the intended narrative.

**The last deferred spec item closed.** Two live identity-resolution queries both completed in exactly 4 turns — `SPEC.md` §3's tool-call/iteration cap is now pinned at 10 (`ClaudeAgentOptions.max_turns`), enforced in code.

**Proves:** every mechanism this project claims — detection, grounding, Escalation, Accepted Risk, remediation auto-close, the monthly quiet-system catch, Risk Assessment with real narrative synthesis, trend lines, and a human-approved tagged Release — genuinely works against real GitHub state. Ten real defects found this way never showed up in any eval case.
**Gate:** every fix landed as its own branch → PR → CI-green → merge, each with a permanent regression guard in `eval.yml` (`scripts/verify_*.py`). Three published, internally-consistent quarterly Releases; the demo-data sequencing gap is documented, not concealed.

---

**Past Milestone 12:** the out-of-scope candidates already sketched (Dormant/Drift's own Operational tier, the grant-time Unapproved gate, contractor end-date expiry — see `SPEC.md` §8; Predictive prioritization, Certification-triage by novelty, Policy-to-config drift detection — see `future-capabilities.md`) are natural next milestones whenever this project picks back up past v1. None are scheduled; nothing here commits to building any of them.
