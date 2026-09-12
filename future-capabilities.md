# Future Capabilities

Reasoning-capability candidates surfaced during design but not built for this project's current scope — genuinely developed sketches (why each clears the "does this need AI, not just automation" bar, a concrete artifact shape), not just names on a list. Each stays here until (if ever) picked up as real scope, at which point it moves into `design-doc.md` and `SPEC.md` proper. None are scheduled; nothing in `development-plan.md` commits to building any of them.

For mechanisms that *are* built but not fully activated (Dormant admin-level's/ad-hoc's and Drift's own Operational cadence; the grant-time Unapproved gate; contractor end-date expiry) — see `SPEC.md` §8's "Out of scope" list instead. Those are smaller and tightly coupled to existing categories.

## Predictive prioritization: forward-looking, not just retrospective

Same stress-test as Identity resolution: does helping the Reviewer *ahead of* the audit, not just reporting after it closes, need AI or just automation? Early-warning thresholds (flagging dormant access at 60 days as "approaching") don't count — just a second, earlier deterministic rule. What does: remediation-velocity synthesis, running the same reasoning the agent already does retrospectively (did this finding stay open past the cycle boundary) forward instead — given how a specific Asset Owner/system/category has historically behaved, surface "this is trending toward still being open at audit time" ahead of the formal report. Not a fourth mechanism, the same reasoning-over-evidence capability pointed at a different question, with the same citation discipline (which prior findings the prediction is based on).

**Status: out of scope for this build.** Depends on closed-Issue history deep enough to compute real velocity baselines, which `demo-timeline.md`'s three simulated quarters don't generate; a real deployment would accumulate this from actual operating history.

## Certification-triage by novelty (thin note, not developed)

Distinct from Predictive prioritization (that forecasts whether one open finding will still be unresolved by audit time): given everything flagged this cycle, which findings actually warrant the Reviewer's limited attention versus which are recurring, already-understood patterns — a novelty judgment, not a severity ranking. Real IGA practice does something like this. A fixed severity ranking would be deterministic and not AI-necessary; the load-bearing part would be comparing a new finding's context against the pattern of prior findings/decisions to judge genuine novelty.

**Status: out of scope for this build**, and less developed than the other candidates here — no artifact shape sketched yet.

## Policy-to-config drift detection: same engine, self-directed

Does verifying that `policy-config.yaml`/`role-access-mapping.yaml` still faithfully reflect `access-control-policy.md`'s prose need AI, or is a diff enough? Surfaced from an accepted risk `design-doc.md` and ADR-0004 both already name — the policy/config split can drift out of alignment, judged acceptable at the time, before a reasoning engine existed that could check it cheaply.

A literal diff/checksum doesn't count — fires on every legitimate edit, not just ones introducing a mismatch, pure noise. Semantic comparison does: confirming `access-control-policy.md`'s "dormant and unused for more than 90 consecutive days" still matches `policy-config.yaml`'s `admin_level_days: 90` is reading comprehension against a specific value, not a string match — citing which Principle, which config key, rather than asserting a verdict with no traceable basis. Same restraint property as Identity resolution: decline to assert drift when a mapping is genuinely ambiguous rather than guessing.

**Scope is narrower than it sounds.** Works cleanly for the *parametric* Principles, each mapping to exactly one `policy-config.yaml` value (Dormant Admin-level's 90 days, Dormant Ad-hoc's 180, Orphaned's same-day SLA). Doesn't extend to `role-access-mapping.yaml`'s Role → Access table against the Role-based Access Principle — that's a process requirement, not a specific value, so there's nothing concrete in the prose to compare each row against; judging whether the table itself still reflects least privilege would be a harder, more subjective call, out of scope here too.

**Concrete shape, sketched not built.** Not a Finding in `CONTEXT.md`'s sense — a discrepancy in the agent's own inputs, not a person's access. Same "synthesis, not a Finding, but still needs a human-facing artifact" pattern as Risk Assessment Entries: no per-item GitHub Issue, but a labeled Issue (`policy-config-review`) for genuinely flagged mismatches, reusing the CAPA-style process-level labeling already sketched for Risk Assessment's systemic treatment recommendations.

**Status: out of scope for this build**, cheapest of the three candidates here — no new architecture or tool, reuses the reasoning engine built for Identity resolution nearly as-is.
