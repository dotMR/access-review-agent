# Monthly Operational Flags — Salesforce — 2026-01

- **Report generated:** 2026-09-14T06:33:57.040021+00:00
- **Asset Owner:** TBD
- **Committed to:** `reports/monthly/2026-01/salesforce.md`

An informational nudge, not a compliance deadline. Lists every currently open Finding for Salesforce, any category, including Orphaned.

This report runs a full reconciliation check every month, the same detection logic as any other run. A Finding it catches is still Evidentiary/quarterly, with no SLA of its own; this report does not gate Escalation or change its category's escalation eligibility.

## Open items

| Category | Identity | Access detail | Expected per policy | Open since | Issue |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Dormant ad-hoc access | Sleve McDichael | `read` access to salesforce | Role baseline is 'none'; ad-hoc grant unused &gt; 180 consecutive days | 2026-09-13 | [#62](https://github.com/dotMR/access-review-agent/issues/62) |
