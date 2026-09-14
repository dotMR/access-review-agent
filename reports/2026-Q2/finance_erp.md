# Access Review — Finance ERP — 2026-Q2

- **Report generated:** 2026-09-14T07:13:15.617489+00:00
- **Data snapshot:** [`5e55a4f`](https://github.com/dotMR/access-review-agent/tree/5e55a4f57ce1136498ee1019fb25e152160f3a4d)
- **Model:**
    - Orphaned, Dormant admin-level, Dormant ad-hoc, Unapproved, Drift: deterministic rule-based checks, no AI model involved
    - Identity resolution: Claude Haiku 4.5 (Anthropic), for judgment on ambiguous cases
- **Reporting period:** 2026-Q2
- **Asset Owner:** TBD
- **Committed to:** `reports/2026-Q2/finance_erp.md`

One of these is generated per Information System (AWS, GitHub, Salesforce, Finance ERP, VPN) each quarter. This is the line-item evidence; the aggregated Quarterly Audit Report links to these rather than repeating their contents.

## Summary

| Category | Open | Remediated | Accepted risk | Total |
| :-- | --: | --: | --: | --: |
| Orphaned access | 0 | 0 | 0 | 0 |
| Dormant admin-level access | 1 | 0 | 0 | 1 |
| Unapproved access | 0 | 0 | 0 | 0 |
| Identity resolution | 0 | 0 | 0 | 0 |
| Drift | 0 | 0 | 0 | 0 |
| Dormant ad-hoc access | 0 | 0 | 0 | 0 |
| **Total** | 1 | 0 | 0 | 1 |

## Findings

### Orphaned access

_No findings._

### Dormant admin-level access (90-day threshold)

| Identity | Access detail | Expected per policy | Last used | Days dormant | Status | Issue |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| Dana Whitfield | `admin` access to finance_erp | Revoke if unused &gt; 90 consecutive days | 2026-04-26 | 140 | Open | [#61](https://github.com/dotMR/access-review-agent/issues/61) |

### Unapproved access

_No findings._

### Identity resolution

_No findings._

### Drift

_No findings._

### Dormant ad-hoc access (180-day threshold)

_No findings._

## Sign-off

I attest that the findings above for Finance ERP have been reviewed and, where applicable, remediated or formally accepted as risk.

- **Asset Owner:** TBD
- **Date:** _(pending sign-off)_
