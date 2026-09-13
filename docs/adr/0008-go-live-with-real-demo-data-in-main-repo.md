# 0008. Going live with real demo data in the main repo

**Status:** accepted

## Context

The main repo has been dry-run-only since Milestone 2 (ADR-0007), by deliberate design — every one of `production.yml`, `monthly-report.yml`, and `quarterly-audit.yml` carries a comment to that effect, each ending with some form of "flipping it to real mode is a deliberate, separate decision." This ADR is that decision.

Milestone 12 validated the entire pipeline for real, four times, against throwaway scratch repos (`-scratch`, `-scratch-2`, `-scratch-3`, `-scratch-4`) specifically so the main repo could stay clean until this exact moment — every defect those trials found was fixed and reverified live before this decision was made (`development-plan.md`, Milestone 12).

This is a portfolio project. A reviewer landing on it gets far more out of browsing real, live Issues, reports, and tagged Releases than out of reading a spec and simulating the outcome by hand. A `WALKTHROUGH.md` linking to real, permanent GitHub artifacts — matching what the three later scratch trials already have — is the natural next artifact, but it needs somewhere real and permanent to link to.

Alternative considered: keep main dry-run indefinitely and point a reviewer at `access-review-agent-scratch-4` as "here's what a real run looks like." Rejected — a scratch repo is explicitly throwaway (four generations already, and disposable by name and by convention), an awkward permanent reference for a portfolio piece, and it splits a reader's attention across two repos for something that belongs in one.

## Decision

Flip `GITHUB_WRITE_MODE` to `real` permanently in the main repo's `production.yml`, `monthly-report.yml`, and `quarterly-audit.yml` — removing the "SCRATCH-REPO COPY, never merge this back" framing those files have carried since Milestone 12, since main is now the real target, not a copy of one. Add the `quarterly-release-approval` environment (required reviewer: the repo owner) and an `ANTHROPIC_API_KEY` secret directly to the main repo. Run `demo-timeline.md`'s full seeding sequence for real against main — the same sequence already proven four times against scratch repos — producing three genuine, permanently-published quarterly Releases. Then add `WALKTHROUGH.md`, linking to that real state.

The fictional company and its data (`access-control-policy.md`'s own disclaimer: "purely an illustrative document with fake data for a fictional company") don't change — only where the demonstration lives.

## Consequences

- `data/`, `reports/`, and the Issue tracker in the main repo stop being empty and become the project's own live evidentiary record — the same content structure `SPEC.md` and the three `templates/report-template-*.md` files already describe, genuinely populated for the first time.
- The "SCRATCH-REPO COPY... never merge this back" comment blocks in all three workflow files are removed; `GITHUB_WRITE_MODE: real` plus the two secrets become the committed, permanent configuration, not a scratch-only overlay layered on top of a dry-run default.
- Every future push to a data file `production.yml` watches, and every monthly/quarterly trigger, now performs real writes against the main repo. Local development against this codebase needs to be deliberate about not re-triggering the live pipeline by accident (e.g. avoid pushing test edits to the exact `data/*.csv` / `policy-config.yaml` / `role-access-mapping.yaml` paths those workflows watch).
- No further scratch-repo trials are needed to validate correctness — Milestone 12's four already did that job exhaustively. A future change to detection or reporting behavior should get its own eval coverage and, if warranted, its own fresh disposable scratch trial before it ever touches the now-live main repo — not the reverse.
- The three eventual Releases inherit the same real-vs-simulated-calendar characteristic already documented from the scratch trials (an escalation's "this period" placement depends on real wall-clock overlap with a simulated quarter, per the Milestone 12 write-up) — expected, not a defect, exactly as in every prior trial.
