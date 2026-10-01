# Monthly Operational Flags — GitHub — 2026-09

- **Report generated:** 2026-10-01T02:40:46.950465+00:00
- **Asset Owner:** TBD
- **Committed to:** `reports/monthly/2026-09/github.md`

An informational nudge, not a compliance deadline. Lists every currently open Finding for GitHub, any category, including Orphaned.

This report runs a full reconciliation check every month, the same detection logic as any other run. A Finding it catches is still Evidentiary/quarterly, with no SLA of its own; this report does not gate Escalation or change its category's escalation eligibility.

## Open items

| Category | Identity | Access detail | Expected per policy | Open since | Issue |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Identity resolution | svc-cicd-deploy | `write` access to github | Individual Usage — access must be assigned to a specific employee, or a Service Account with a documented, currently-active owner (access-control-policy.md, Individual Usage / Service Account Ownership) | 2026-09-14 | [#71](https://github.com/dotMR/access-review-agent/issues/71) |
| Dormant admin-level access | Bobson Dugnutt | `admin` access to github | Revoke if unused &gt; 90 consecutive days | 2026-09-14 | [#68](https://github.com/dotMR/access-review-agent/issues/68) |
