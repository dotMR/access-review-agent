# Development Plan

A walking-skeleton build order: every milestone is a working, end-to-end slice — never a component built in isolation and integrated later. Each one names what's built, what it proves, and which `eval-cases.md` cases become a required-passing gate before moving to the next milestone. Small pieces, always testable, always real (even Milestone 1 talks to a real tool, not a mock of the whole system).

**Runtime: Python.** The Claude Agent SDK is officially available for Python and TypeScript only, with symmetric feature coverage (subagents, hooks, MCP, permissions, sessions) — the SDK itself doesn't favor either. Python was chosen for ecosystem fit with this project's actual workload: `csv`/`pandas` for the core reconciliation logic (reading and joining HRIS/access CSVs, anti-joins, threshold comparisons), and mature HTML/Markdown-to-PDF rendering (WeasyPrint, ReportLab) for the aggregate report's PDF export, versus TypeScript's comparatively thin tabular-data tooling and its PDF options mostly routing through a headless browser. GitHub API access uses a third-party library (PyGithub or similar) rather than GitHub's own first-party Octokit, a real but minor trade-off against the ecosystem fit on the other two points.

---

## Milestone 1 — Read one file, apply one deterministic check, print the result

Single subagent (AWS only), `read_access_data` + `read_hris` tools, Orphaned detection only (the simplest category: an anti-join plus a status check, no thresholds). Output is a logged finding, not yet an Issue.

Also builds the grounding/citation **validation logic** now, not in Milestone 2 — `validate_finding()`, which independently re-reads the source data to confirm a claimed finding is actually true, trusting nothing about what happened during the model's own tool calls. This is split from Milestone 2 deliberately: the validation logic itself doesn't depend on `open_issue` existing, and building it now closes a real gap in this milestone's own eval gate — without it, a hallucinated finding that happens to match `expected.json` would pass. Milestone 2 reuses this function unchanged as the gate in front of `open_issue`; it isn't rebuilt there.

Two orchestration surfaces are in play from the start, and they're not on the same schedule. The **production workflow** (push-triggered on data commits, monthly/quarterly cron) stays deferred to Milestone 5 exactly as before — it depends on dispatch logic, Issue-writing, and reports that don't exist yet. The **eval/CI workflow** (`iam-review-agent-design.md`'s Evals section — a separate workflow, triggered on any PR touching agent code/prompts/tools) is cheap enough not to defer: it needs nothing but a runnable eval script, which this milestone already produces. Sequencing within this milestone: get the three cases passing **locally first** — debugging the SDK integration and CI at the same time is worse than one at a time — then wire the eval CI workflow before calling the milestone done. From here on, "Gate: Tier X cases pass" means CI verifies it on every push, not that someone ran a script locally once.

**Proves:** the read-tool-to-reasoning pipeline works against real fixture data, verified in CI, with every claimed finding independently confirmed against the source data rather than just pattern-matched against `expected.json`.
**Gate:** Tier 1 cases 1–3 (Orphaned) pass, locally first, then in the eval CI workflow. Eval case 37 (grounding/citation) also passes here — moved up from Milestone 2, see above.

## Milestone 2 — First real write: `open_issue`, reusing the grounding gate

Add `open_issue` (title/body/label format from `SPEC.md` §4), gated by `validate_finding()` from Milestone 1 — reused unchanged, not rebuilt, since the validation logic never depended on `open_issue` existing in the first place. This is also where the local-vs-remote ADR (deferred in `iam-review-agent-design.md` until "implementation starts," which this milestone is) gets formally filed — the design (single entrypoint, dry-run-capable adapter isolating GitHub calls, env-var-based secrets either way) is already written in that doc's Local vs. remote section, so filing it here is transcription plus whatever the real build surfaces, not fresh design work. Dry-run adapter first, real GitHub API second.

**Proves:** the agent can write to a real external system, and the grounding guardrail actually gates that write path, not just a detection-time check.
**Gate:** a real Issue opens against a scratch repo with the correct title/body/labels; an ungrounded finding is confirmed to *not* open one.

## Milestone 3 — Round out AWS's deterministic categories

Add Dormant admin-level, Dormant ad-hoc, Unapproved, Drift to the same single subagent. No new architecture — same tools, same write path, more checks.

**Proves:** the detection loop holds multiple check types without needing a redesign.
**Gate:** Tier 1 cases 4–16 all pass.

## Milestone 4 — Subagent isolation: expand to all five systems

Build the actual architecture from ADR-0001: one shared read implementation, five pre-bound subagent instances (no `system_name` parameter), main agent as the sole orchestrator and Issue-writer. Still manually/locally triggered — no GitHub Actions yet.

**Proves:** the isolation boundary is structural, not just described. Verify directly: a subagent's tool registry provably cannot reach another system's file.
**Gate:** a targeted architecture check (not a numbered eval case — this is a registry-inspection test, not a data-fixture one) confirming each subagent's available tools are exactly its own system's.

## Milestone 5 — Real trigger: GitHub Actions and the dispatch rule

Wire the push-triggered production workflow: single-system commits scope to one subagent, HRIS/policy-config/role-mapping commits fan out to all five, `access-control-policy.md` triggers nothing. Least-privilege `GITHUB_TOKEN` scoping (`permissions: issues: write, contents: read`) lands here too — it's a workflow-file concern, not a separate milestone.

**Proves:** the dispatch table is real CI behavior, not just a documented rule.
**Gate:** Tier 3 cases 25–28 (dispatch) pass.

## Milestone 6 — Identity resolution: first reasoning capability

Build the four-outcome resolution logic and its restraint property (decline to guess on insufficient or ambiguous evidence).

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
