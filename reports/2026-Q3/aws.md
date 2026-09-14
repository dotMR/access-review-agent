# Access Review — AWS — 2026-Q3

- **Report generated:** 2026-09-14T07:21:08.083086+00:00
- **Data snapshot:** [`545ed7e`](https://github.com/dotMR/access-review-agent/tree/545ed7e2ada397aebade1b44568d0e698315601c)
- **Model:**
    - Orphaned, Dormant admin-level, Dormant ad-hoc, Unapproved, Drift: deterministic rule-based checks, no AI model involved
    - Identity resolution: Claude Haiku 4.5 (Anthropic), for judgment on ambiguous cases
- **Reporting period:** 2026-Q3
- **Asset Owner:** TBD
- **Committed to:** `reports/2026-Q3/aws.md`

One of these is generated per Information System (AWS, GitHub, Salesforce, Finance ERP, VPN) each quarter. This is the line-item evidence; the aggregated Quarterly Audit Report links to these rather than repeating their contents.

## Summary

| Category | Open | Remediated | Accepted risk | Total |
| :-- | --: | --: | --: | --: |
| Orphaned access | 0 | 2 | 0 | 2 |
| Dormant admin-level access | 0 | 0 | 0 | 0 |
| Unapproved access | 1 | 0 | 0 | 1 |
| Identity resolution | 0 | 0 | 0 | 0 |
| Drift | 1 | 0 | 0 | 1 |
| Dormant ad-hoc access | 0 | 0 | 0 | 0 |
| **Total** | 2 | 2 | 0 | 4 |

## Findings

### Orphaned access

| Identity | Access detail | Expected per policy | Date detected | Time to revoke | Status | Issue |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| Cecilia Tisio | `write` access to aws | None (terminated 2026-09-14) | 2026-09-14 | same day as detection (Orphaned SLA — access-control-policy.md, Operational review) | Remediated | [#70](https://github.com/dotMR/access-review-agent/issues/70) |
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
