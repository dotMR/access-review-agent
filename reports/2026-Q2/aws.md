# Access Review — AWS — 2026-Q2

- **Report generated:** 2026-09-14T07:13:15.617489+00:00
- **Data snapshot:** [`5e55a4f`](https://github.com/dotMR/access-review-agent/tree/5e55a4f57ce1136498ee1019fb25e152160f3a4d)
- **Model:**
    - Orphaned, Dormant admin-level, Dormant ad-hoc, Unapproved, Drift: deterministic rule-based checks, no AI model involved
    - Identity resolution: Claude Haiku 4.5 (Anthropic), for judgment on ambiguous cases
- **Reporting period:** 2026-Q2
- **Asset Owner:** TBD
- **Committed to:** `reports/2026-Q2/aws.md`

One of these is generated per Information System (AWS, GitHub, Salesforce, Finance ERP, VPN) each quarter. This is the line-item evidence; the aggregated Quarterly Audit Report links to these rather than repeating their contents.

## Summary

| Category | Open | Remediated | Accepted risk | Total |
| :-- | --: | --: | --: | --: |
| Orphaned access | 0 | 1 | 0 | 1 |
| Dormant admin-level access | 0 | 0 | 0 | 0 |
| Unapproved access | 1 | 0 | 0 | 1 |
| Identity resolution | 0 | 0 | 0 | 0 |
| Drift | 1 | 0 | 0 | 1 |
| Dormant ad-hoc access | 0 | 0 | 0 | 0 |
| **Total** | 2 | 1 | 0 | 3 |

## Findings

### Orphaned access

| Identity | Access detail | Expected per policy | Date detected | Time to revoke | Status | Issue |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| Ronnis Pawgood | `write` access to aws | None (terminated 2026-09-13) | 2026-09-13 | same day as detection (Orphaned SLA — access-control-policy.md, Operational review) | Remediated | [#63](https://github.com/dotMR/access-review-agent/issues/63) |

### Dormant admin-level access (90-day threshold)

_No findings._

### Unapproved access

| Identity | Access detail | Expected per policy | Date granted | Approved by | Status | Issue |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| Mike Truk | `write` access to aws | A recorded approval (auto or Asset Owner) on file | 2026-09-13 | none on file | Open | [#64](https://github.com/dotMR/access-review-agent/issues/64) |

### Identity resolution

_No findings._

### Drift

| Identity | Access detail | Expected per policy | Role changed | Status | Issue |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Karl Dandleton | `write` access to aws | 'admin' (baseline for current role 'Asset Owner') | `2026-09-14`: `Software Engineer` → `Asset Owner` | Open | [#69](https://github.com/dotMR/access-review-agent/issues/69) |

### Dormant ad-hoc access (180-day threshold)

_No findings._

## Sign-off

I attest that the findings above for AWS have been reviewed and, where applicable, remediated or formally accepted as risk.

- **Asset Owner:** TBD
- **Date:** _(pending sign-off)_
