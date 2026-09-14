# Access Review Agent

A joiner-mover-leaver access review agent that reasons through ambiguous cases a rules engine can't — and knows when to say "not enough evidence" instead of guessing. It's running for real: every Issue, report, and quarterly Release in this repository was produced by the agent itself, against its own live data, not a simulation.

**→ Start with [`WALKTHROUGH.md`](./WALKTHROUGH.md)** for a guided, quarter-by-quarter tour linking every claim to the real GitHub artifact behind it.

## Why this exists

I posted a thought on LinkedIn while thinking about my next role: you can't credibly sell customers transformational AI while your own internal operations still run on the manual processes AI is meant to replace. This project is that thesis made concrete.

Joiner-mover-leaver access review is normally a periodic, manual checklist — exactly the kind of control a well-staffed team lets slip, not from indifference but because continuously reviewing every system is tedious. This agent runs that review continuously instead, reasoning through cases a lookup can't: a shared login that's either a documented exception or a real violation depending on a justification note nobody but a human — or this agent — would actually read. When the evidence isn't there, it says so instead of guessing — and every claim it makes cites the specific record behind it.

It cross-references HR and IT access data against policy to flag orphaned, dormant (admin-level and ad-hoc), unapproved, drifted, and identity-resolution findings, and runs on three triggers: push-triggered whenever a commit touches source access data, HR data, or policy config in this repository; a monthly cron for an informational summary; and a quarterly cron for the formal audit record (`SPEC.md` §2).

**Status:** v1 complete — all 12 milestones built and merged; see `development-plan.md` for the full build story and `docs/adr/0008-go-live-with-real-demo-data-in-main-repo.md` for the decision to run it for real, here. What "complete" means in practice:

- Real detection across five finding types (orphaned, dormant admin-level, dormant ad-hoc, unapproved, drift), plus Identity resolution via the Agent SDK for cases a lookup can't resolve
- Real GitHub Issue writing and Actions dispatch, on all three real triggers — push, monthly, quarterly
- Real Risk Assessment scoring and narrative synthesis, Escalation/Accepted-Risk lifecycle mechanics, and per-system failure isolation
- Real tagged quarterly Releases, gated behind human-in-the-loop approval
- The full three-quarter demo timeline, run for real against this repository's own data — not a scratch copy

## Reviewing the repository

Three artifacts, in order of how current they are:

1. **GitHub Issues** are the live, continuously-updated source of truth — every Finding gets one the moment it's detected (`SPEC.md` §4), not just at report time. Filter by label to see current state directly: `is:open` for everything still needing attention, `label:escalated` for what's been raised to the Reviewer, `label:accepted-risk` (these are *closed* Issues — see the status note below) for what's been formally accepted rather than fixed. Category labels (`orphaned`, `dormant-admin`, `dormant-ad-hoc`, `unapproved`, `identity-resolution`, `drift`) and system labels (`aws`, `github`, `salesforce`, `finance-erp`, `vpn`) narrow further.
2. **`reports/monthly/<period>/<system>.md`** is the informational nudge — every currently open finding for one system, refreshed monthly. Useful for a quick read on what's outstanding ahead of the next formal record, but it's explicitly not evidentiary: no sign-off, and closed items (remediated or accepted-risk) don't appear here at all, only what's still open.
3. **`reports/<period>/aggregate.md`** is the formal audit-evidence record — the one an external auditor would actually read and cite. Executive summary, resolution-status rollup, the Risk Assessment section, and Escalations, with links out to `reports/<period>/<system>.md` for line-item detail per system. Each quarter's Release (tagged `<period>`, e.g. `2026-Q1`) bundles all six report files plus the aggregate's PDF export — start there for the fastest "what happened this quarter" read, since the Release body already summarizes the same headline numbers.

**A closed Issue isn't always a fixed one.** Applying the `accepted-risk` label closes the Issue, the same action as remediation — the label is what distinguishes "fixed" from "formally accepted as an acceptable risk" on an otherwise identical closed state (ADR-0005). Check for that label before assuming a closed Issue means the access was actually revoked.

## Documentation

- **`CONTEXT.md`** — glossary and actors; the vocabulary everything else uses.
- **`SPEC.md`** — the settled, implementation-facing shape: data schemas, trigger/dispatch rules, the tool registry, finding definitions, report structure, guardrails.
- **`development-plan.md`** — the walking-skeleton build order, milestone by milestone.
- **`eval-cases.md`** — the 40-case eval suite each milestone is graded against.
- **`design-doc.md`** — the design rationale.
- **`future-capabilities.md`** — reasoning-capability candidates considered but not built, kept separate so the design doc stays focused on what actually exists.
- **`docs/adr/`** — architecturally significant decisions (Context/Decision/Consequences), one file per decision.
- **`access-control-policy.md`**, **`role-access-mapping.yaml`**, **`policy-config.yaml`** — the policy this agent enforces: human-readable Principles, the Role → Access Mapping and System Criticality, and the machine-consumed thresholds and scoring tables, respectively.
- **`demo-timeline.md`** — the concrete, commit-by-commit scenario this repository's own history is seeded from.
- **`WALKTHROUGH.md`** — a guided tour through this repository's own live demo run, linking every beat to a real Issue, report, or Release.