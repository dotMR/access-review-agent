# Development Plan

A walking-skeleton build order: every milestone is a working, end-to-end slice — never a component built in isolation and integrated later. Each one names what's built, what it proves, and which `eval-cases.md` cases become a required-passing gate before moving to the next milestone. Small pieces, always testable, always real (even Milestone 1 talks to a real tool, not a mock of the whole system).

**Runtime: Python.** The Claude Agent SDK is officially available for Python and TypeScript only, with symmetric feature coverage (subagents, hooks, MCP, permissions, sessions) — the SDK itself doesn't favor either. Python was chosen for ecosystem fit with this project's actual workload: `csv`/`pandas` for the core reconciliation logic (reading and joining HRIS/access CSVs, anti-joins, threshold comparisons), and mature HTML/Markdown-to-PDF rendering (WeasyPrint, ReportLab) for the aggregate report's PDF export, versus TypeScript's comparatively thin tabular-data tooling and its PDF options mostly routing through a headless browser. GitHub API access uses a third-party library (PyGithub or similar) rather than GitHub's own first-party Octokit, a real but minor trade-off against the ecosystem fit on the other two points.

---

## Milestone 1 — Read one file, apply one deterministic check, print the result

Orphaned detection (AWS only) — the simplest category: an anti-join plus a status check, no thresholds. **Plain Python, no model call** (ADR-0006) — a deterministic check gains nothing from an LLM, not even a cheap one; the read-and-validate functions in `tools/` and the detection logic in `detection/orphaned.py` are the real implementation. Output is a logged finding, not yet an Issue. (An initial version of this milestone did route Orphaned through the Agent SDK before ADR-0006 corrected course — that working integration code is preserved, not lost, in `reference/milestone-6-agent-sdk-patterns/` for reuse once Milestone 6 actually needs it.)

Also builds the grounding/citation **validation logic** now, not in Milestone 2 — `validate_finding()`, which independently re-reads the source data to confirm a claimed finding is actually true. For Tier 1 this is defense-in-depth against bugs in the detection code itself, not hallucination (deterministic Python can't hallucinate) — but it runs the same way regardless of whether a finding came from Python or, later, a model, so the write-gate in front of `open_issue` (Milestone 2) never needs to special-case which. Building it now closes a real gap in this milestone's own eval gate — without it, a finding that happens to match `expected.json` for the wrong reason would still pass.

Two orchestration surfaces are in play from the start, and they're not on the same schedule. The **production workflow** (push-triggered on data commits, monthly/quarterly cron) stays deferred to Milestone 5 exactly as before — it depends on dispatch logic, Issue-writing, and reports that don't exist yet. The **eval/CI workflow** (`iam-review-agent-design.md`'s Evals section — a separate workflow, triggered on any PR touching agent code/prompts/tools) was held off deliberately once real API cost showed up during Milestone 1's original Agent-SDK-based version — but with Tier 1 now running no model call at all, that specific cost objection no longer applies to Milestones 1, 3, 4, and 5. Worth revisiting explicitly once Tier 2 (Milestone 6 onward) reintroduces real per-run cost, rather than assuming the original decision still holds unexamined.

**Proves:** the read-and-validate-and-detect pipeline works against real fixture data, with every claimed finding independently confirmed against the source data rather than just pattern-matched against `expected.json`.
**Gate:** Tier 1 cases 1–3 (Orphaned) pass. Eval case 37 (grounding/citation) also passes here — moved up from Milestone 2, see above.

## Milestone 2 — First real write: `open_issue`, reusing the grounding gate

Add `open_issue` (title/body/label format from `SPEC.md` §4), gated by `validate_finding()` from Milestone 1 — reused unchanged, not rebuilt, since the validation logic never depended on `open_issue` existing in the first place. This is also where the local-vs-remote ADR (deferred in `iam-review-agent-design.md` until "implementation starts," which this milestone is) gets formally filed — the design (single entrypoint, dry-run-capable adapter isolating GitHub calls, env-var-based secrets either way) is already written in that doc's Local vs. remote section, so filing it here is transcription plus whatever the real build surfaces, not fresh design work. Dry-run adapter first, real GitHub API second.

**Proves:** the agent can write to a real external system, and the grounding guardrail actually gates that write path, not just a detection-time check.
**Gate:** a real Issue opened against a scratch repo with the correct title/body/labels (verified once, by hand); Tier 3 cases 37 (grounding, routed through `open_issue` itself) and 41 (Issue formatting) pass automatically in CI via `scripts/run_milestone2.py`, dry-run only — no live GitHub call needed to check formatting or rejection.

## Milestone 3 — Round out AWS's deterministic categories

Add Dormant admin-level, Dormant ad-hoc, Unapproved, Drift to `detection/`. Still no model call (ADR-0006) — same pure-Python pattern as Orphaned, same tools, same write path, more checks. Adds the `read_policy` tool (`tools/policy.py`, SPEC.md §3) — a generic YAML reader shared by `policy-config.yaml` (thresholds) and `role-access-mapping.yaml` (the baseline-access lookup Dormant ad-hoc and Drift both need). `grounding.py` and `github/issues.py` extend to all four new categories alongside detection itself — a category isn't wired into the write path (Milestone 2) as an afterthought, it lands with its own grounding validator and Issue-body fields in the same commit as its detection logic.

The two dormancy categories' eval fixtures pin an explicit `as_of` reference date (in `expected.json`) rather than comparing against `date.today()` — a boundary case (89/90/91 days) authored against one date would otherwise silently start failing as real wall-clock time passes it. `detect_dormant_admin`/`detect_dormant_ad_hoc` take `as_of` as an optional override for exactly this reason; production calls leave it unset and get real "today." The grounding gate follows the same discipline from the source-record side: it recomputes each dormancy finding's day-count from `last_used_date` and the finding's own `date_detected`, never from `date.today()` either, so a grounding check run days after detection still agrees with what detection actually found.

**Proves:** the detection loop holds multiple check types without needing a redesign, and the write path (grounding + `open_issue`) genuinely generalizes rather than being Orphaned-specific.
**Gate:** Tier 1 cases 4–16 pass; the Issue-formatting case (41) passes for each of the four new categories too, alongside Orphaned's from Milestone 2 — all in `scripts/run_milestone3.py`, dry-run only, no credentials.

## Milestone 4 — Isolation: expand to all five systems

Build the actual architecture from ADR-0001: one shared read implementation (already existed since Milestone 1 — `tools/access_data.py`/`hris.py` were always system-agnostic), five pre-bound detection units (`units.py`'s `SystemDetectionUnit`, `system_name` fixed at construction, `detect_all()` takes no parameters), main agent as the sole orchestrator and Issue-writer (`orchestrator.py`'s `run_full_reconciliation` — the only caller of `open_issue` anywhere in the codebase; units never import `github/`). Still plain Python for all five at this point — Tier 2's reasoning-based subagents don't arrive until Milestone 6, but the isolation boundary is identical either way: what matters is that a unit of detection code (Python function or, later, an LLM tool call) can only ever reach its own system's file, not whether an LLM is involved. Still manually/locally triggered — no GitHub Actions yet.

The isolation check doesn't just assert the boundary, it tries to break it: each unit runs twice against `evals/cases/milestone4-all-systems/` (one finding per system, five different categories) — once with all five systems' files present, once against a data_dir holding *only* that unit's own access file plus HRIS, the other four absent entirely rather than merely unused. Identical success and identical findings in both runs is real evidence a unit never depended on another system's file — if it had, the isolated run would raise `FileNotFoundError`, not quietly pass.

**Proves:** the isolation boundary is structural, not just described. Verify directly: a detection unit's available data access provably cannot reach another system's file.
**Gate:** a targeted architecture check (not a numbered eval case — this is a registry-inspection test, not a data-fixture one) confirming each unit's available data access is exactly its own system's, run via `scripts/run_milestone4.py`, dry-run only, no credentials.

## Milestone 5 — Real trigger: GitHub Actions and the dispatch rule

Wire the push-triggered production workflow: single-system commits scope to one subagent, HRIS/policy-config/role-mapping commits fan out to all five, `access-control-policy.md` triggers nothing. Least-privilege `GITHUB_TOKEN` scoping (`permissions: issues: write, contents: read`) lands here too — it's a workflow-file concern, not a separate milestone.

Also the natural point to upgrade the Issue body's Source record citation (SPEC.md §4) from a bare file path to a clickable GitHub blob permalink (`.../blob/<sha>/<path>`) — the triggering commit SHA is ordinary CI context once a real trigger exists (`GITHUB_SHA` in Actions), it just has nowhere to come from before this milestone.

**Proves:** the dispatch table is real CI behavior, not just a documented rule.
**Gate:** Tier 3 cases 25–28 (dispatch) pass.

## Milestone 6 — Identity resolution: first reasoning capability

**The first point the Agent SDK is actually used** (ADR-0006) — every prior milestone's detection stayed plain Python because nothing before this genuinely needed a model. Build the four-outcome resolution logic and its restraint property (decline to guess on insufficient or ambiguous evidence), reusing the working tool-wiring/`ClaudeAgentOptions`/JSON-extraction patterns preserved in `reference/milestone-6-agent-sdk-patterns/` — copy from it, don't import it, since the surrounding code has moved on since it was written; the README there also names a non-obvious bug (extract text via `ResultMessage.result`, not by stringifying raw message objects) worth reading before re-deriving it the hard way. Model choice for this milestone is a real decision to make here, informed by what the reasoning actually requires — not inherited from the Haiku-for-Tier-1 exploration that turned out not to apply.

**Proves:** the system's first genuine LLM-reasoning step, with the citation/restraint discipline that's supposed to make it safe to automate.
**Gate:** Tier 2 cases 17–22 pass. Also verify eval case 38 (input safety) now — this is the first point `provisioning_note` content actually reaches a reasoning step, so it's the first point that guardrail can be meaningfully tested rather than just asserted.

## Milestone 7 — Reports: per-system and aggregate, `commit_report`

Build `commit_report`, wire the two evidentiary report templates, add the quarterly-audit trigger (schedule/`workflow_dispatch`).

**Proves:** committed-file output works, not just Issue-based output.
**Gate:** manual inspection against the templates — reports are downstream rendering of already-gated Issue data, so no new eval cases are needed here specifically.

## Milestone 8 — Risk Assessment

Scoring tables (ADR-0002), quarterly-only computation from `list_issues` + `read_prior_report`, narrative synthesis.

**Proves:** the second reasoning capability, and that the deterministic scoring layer (tables) and the genuine-synthesis layer (narrative) are correctly separated.
**Gate:** Tier 3 cases 29–31 (tables, including non-endpoint cells) pass deterministically; Tier 2 cases 23–24 (narrative) pass via LLM-as-judge.

## Milestone 9 — Escalation and Accepted Risk lifecycle

`apply_label`/`add_comment` mechanics for Escalation (no assignee — ADR-0005), fires-once behavior, `accepted-risk` closing the Issue.

**Proves:** the Issue lifecycle semantics that took real back-and-forth to resolve are actually implemented as decided, not just documented.
**Gate:** Tier 3 cases 34–36 pass.

## Milestone 10 — Monthly Operational Flags

The monthly trigger, full detection re-run (not just a `list_issues` read — the ADR-0003 revision), `commit_report` to `reports/monthly/`.

**Proves:** the quiet-system gap is actually closed, not just designed to be.
**Gate:** Tier 3 cases 32–33 pass.

## Milestone 11 — Partial failure, Release, publish gate

Per-system failure isolation (one bad file doesn't block the other four), Release tag/title/body/assets (`create_release`), the human-in-the-loop environment protection rule gating publish.

**Proves:** the last two guardrails (fail-loud completeness, human-in-the-loop) are real CI behavior.
**Gate:** Tier 3 case 39 passes; a real tagged Release with all seven assets is produced end-to-end.

## Milestone 12 — Full demo timeline replay

Run `demo-timeline.md`'s actual 14-commit sequence end-to-end against a real (or realistic sandbox) repo, producing the complete three-quarter artifact trail.

**Proves:** everything holds together as one coherent story, not just as isolated passing tests.
**Gate:** the resulting Issues, reports, and Releases match `demo-timeline.md`'s narrative beats. This is also the first point real tool-call-count data exists — set the tool-call/iteration cap (`SPEC.md` §3, still unpinned) from this run, closing the last deferred item in the spec.

---

**Past Milestone 12:** the out-of-scope candidates already sketched (Dormant/Drift's own Operational tier, the grant-time Unapproved gate, contractor end-date expiry — see `SPEC.md` §8; Predictive prioritization, Certification-triage by novelty, Policy-to-config drift detection — see `future-capabilities.md`) are natural next milestones whenever this project picks back up past v1. None are scheduled; nothing here commits to building any of them.
