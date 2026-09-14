# Guided Walkthrough

This repo's `data/`, `reports/`, and Issue tracker aren't hypothetical — they're this project's own live evidentiary record, produced by running `demo-timeline.md`'s scenario for real against real GitHub state. This walkthrough is a tour through the three quarters it produced: what happened, what it demonstrates, and exactly where to look, linking every claim to the real Issue, report, or Release behind it.

**Before you start:** [Issues](https://github.com/dotMR/access-review-agent/issues?q=is%3Aissue) is the live, continuously-updated source of truth — everything below just points you to the right ones at the right time. One thing worth knowing going in: a closed Issue isn't always a fixed one — applying the `accepted-risk` label closes the Issue the same way remediation does, so check for that label before assuming access was revoked (see `access-control-policy.md`'s Accepted Risk principle for the full reasoning).

---

## Q1 2026 — five categories, one live escalation

Five findings opened from a clean repo — every category gets its first real Issue.

| Finding | Issue | What to notice |
| :-- | :-- | :-- |
| Dana Whitfield, dormant admin (Finance ERP) | [#61](https://github.com/dotMR/access-review-agent/issues/61) | Stays open all three quarters — the strongest recurring thread in the whole trial |
| Sleve McDichael, dormant ad-hoc (Salesforce) | [#62](https://github.com/dotMR/access-review-agent/issues/62) | Same — watch its Risk Assessment recurrence deepen |
| Ronnis Pawgood, orphaned access (AWS) | [#63](https://github.com/dotMR/access-review-agent/issues/63) | **The live escalation — see below** |
| Mike Truk, unapproved access (AWS) | [#64](https://github.com/dotMR/access-review-agent/issues/64) | A second recurring thread, lower criticality than #61 |
| vpn-legacy-4402, unresolved identity (VPN) | [#65](https://github.com/dotMR/access-review-agent/issues/65) | The agent declines to guess — becomes accepted risk starting in Q2, see below |

**The live escalation, start to finish.** Issue #63 opened the same day Ronnis Pawgood was terminated. The next real day, elapsed time (not a simulated date) pushed it past its same-day SLA — the agent's own re-check caught it and posted [the escalation comment](https://github.com/dotMR/access-review-agent/issues/63#issuecomment-5659991728), applying the `escalated` label.

Every Risk Assessment row here is isolated — nothing has had a second quarter yet to show a pattern.

**Read:** [Q1 aggregate report](https://github.com/dotMR/access-review-agent/blob/main/reports/2026-Q1/aggregate.md) · [Q1 Release](https://github.com/dotMR/access-review-agent/releases/tag/2026-Q1)

---

## Q2 2026 — remediation, escalation, and accepted risk

| What happened | Issue | What to notice |
| :-- | :-- | :-- |
| Ronnis Pawgood's AWS access genuinely revoked | [#63](https://github.com/dotMR/access-review-agent/issues/63) (closed) | Read [the remediation comment](https://github.com/dotMR/access-review-agent/issues/63#issuecomment-5660281453) — the agent re-checked and found the access genuinely gone, closed it automatically. Still carries the `escalated` label from Q1; a closed Issue keeps its real history |
| Todd Bonzalez's VPN access flagged, then corrected, within the same quarter | [#67](https://github.com/dotMR/access-review-agent/issues/67) (closed) | Opened, then closed minutes later by [this remediation comment](https://github.com/dotMR/access-review-agent/issues/67#issuecomment-5660287309) once the access record was corrected — a genuine flag-then-fix inside one quarter, not just a narrative description of one |
| Bobson Dugnutt's dormant GitHub admin grant | [#68](https://github.com/dotMR/access-review-agent/issues/68) | Caught by an ordinary push, not the monthly report — see the note below |
| Karl Dandleton's role change without matching access | [#69](https://github.com/dotMR/access-review-agent/issues/69) | Drift's first appearance this trial |
| vpn-legacy-4402 investigated and accepted as risk | [#65](https://github.com/dotMR/access-review-agent/issues/65) (closed) | Read [the accepted-risk comment](https://github.com/dotMR/access-review-agent/issues/65#issuecomment-5660308108) — closed before Q2's own report generated, so it already shows as settled below |

**Escalation fires once.** The same push that opens #67 (Todd Bonzalez's VPN grant) also re-runs the check that escalates overdue findings, across every open Issue, not just the ones tied to that push. Issue #63 gets re-checked here too: the same-day SLA is still missed, but it already carries the `escalated` label, so no second escalation comment is posted. Confirm it yourself — #63 carries exactly two comments for its whole life: [the original escalation](https://github.com/dotMR/access-review-agent/issues/63#issuecomment-5659991728) and [the later remediation](https://github.com/dotMR/access-review-agent/issues/63#issuecomment-5660281453), nothing in between.

**Bobson Dugnutt's dormant GitHub grant.** Simulating "90 days idle" means editing the access record directly — that edit touches the same file a push already watches, so ordinary push-triggered detection catches it in the same run. The monthly report (`reports/monthly/2026-05/github.md`) independently re-confirms the finding on its own cadence.

**Accepted risk, settled within the quarter it's decided.** Labeling an Issue `accepted-risk` doesn't close it by itself — closing happens on the next reconciliation pass (a push-triggered run, or a monthly report), the same mechanism that closes a remediated Issue. Here, that reconciliation pass ran before Q2's own report generated, so #65 already shows as closed and accepted risk in [Q2's aggregate report](https://github.com/dotMR/access-review-agent/blob/main/reports/2026-Q2/aggregate.md) — read its Risk Assessment row for Identity resolution/VPN: a single, isolated acceptance, Likelihood Low, with no claim of persisting across multiple quarters.

**Worth comparing directly:** the Risk Assessment rows for #61 (Finance ERP, 2nd consecutive quarter, High Impact) and #68 (GitHub, brand new, Medium Impact) are the *same category* on two different systems, with two different Impact ratings — the report is making a real criticality distinction, not applying one score uniformly.

**Read:** [Q2 aggregate report](https://github.com/dotMR/access-review-agent/blob/main/reports/2026-Q2/aggregate.md) · [Q2 Release](https://github.com/dotMR/access-review-agent/releases/tag/2026-Q2)

---

## Q3 2026 — deeper recurrence, a second Identity resolution case

| What happened | Issue | What to notice |
| :-- | :-- | :-- |
| Cecilia Tisio's termination sets up Orphaned access, revoked the same day | [#70](https://github.com/dotMR/access-review-agent/issues/70) (closed) | Opened, then closed minutes later by [this remediation comment](https://github.com/dotMR/access-review-agent/issues/70#issuecomment-5660430640) — the SLA met cleanly, the direct contrast with Q1's #63 missing it |
| Cecilia Tisio's departure also surfaces a stale-ownership Identity resolution case | [#71](https://github.com/dotMR/access-review-agent/issues/71) | She was the documented owner of `svc-cicd-deploy` (Q1's clean happy-path case); her departure makes that ownership stale. One event, one finding no other check could see. Stays open |
| #61 and #64 both reach a third consecutive quarter | [#61](https://github.com/dotMR/access-review-agent/issues/61) / [#64](https://github.com/dotMR/access-review-agent/issues/64) | Finance ERP's Dormant admin-level reaches **Critical**, AWS's Unapproved reaches **High** — different Impact from different System Criticality, same recurrence depth |
| #68 reaches its 2nd consecutive quarter | [#68](https://github.com/dotMR/access-review-agent/issues/68) | Contrast this against #61/#64's third quarter — the scoring is genuinely discriminating by history, not just by category |

**What's absent from Q3's Risk Assessment table, and why.** #63 (remediated in Q2), #65 (accepted as risk in Q2), and #67 (also remediated in Q2) don't have their own rows here, even though AWS and VPN both appear in other rows. Risk Assessment shows only findings still open, or ones settled after the prior quarter's own report was generated — a resolution that already had its own row in an earlier quarter's report doesn't get a second one. Compare Q2's own table, where all three got exactly one row, in the quarter their resolution was genuinely new. Seven rows total in [Q3's own table](https://github.com/dotMR/access-review-agent/blob/main/reports/2026-Q3/aggregate.md) — count them.

**The escalation landing in Q3's own record.** Q3's own Escalations table shows #63's real escalation event, because the real September calendar date happens to overlap the simulated quarter's own bounds. Q1 and Q2 correctly show none, for the same real-calendar reason, not a gap: an escalation's "this period" placement is governed by the real timestamp on its comment, and every comment in this trial carries a real September timestamp regardless of which simulated quarter it represents.

**Read:** [Q3 aggregate report](https://github.com/dotMR/access-review-agent/blob/main/reports/2026-Q3/aggregate.md) · [Q3 Release](https://github.com/dotMR/access-review-agent/releases/tag/2026-Q3)

---

## The trend line across all three quarters

Each aggregate report's Trend section carries every earlier quarter's own row forward, oldest first, with a running delta:

| Period | Total | Open | Remediated | Accepted risk | Δ Total |
| :-- | --: | --: | --: | --: | --: |
| 2026-Q1 | 5 | 5 | 0 | 0 | N/A, first period |
| 2026-Q2 | 8 | 5 | 2 | 1 | +3 |
| 2026-Q3 | 10 | 6 | 3 | 1 | +2 |

The full table only appears starting in Q2 — Q1's own Trend section is a single row with no prior period to compare against, handled as a real answer ("first period"), not an error or an empty table.
