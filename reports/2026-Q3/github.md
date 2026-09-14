# Access Review — GitHub — 2026-Q3

- **Report generated:** 2026-09-14T07:21:08.083086+00:00
- **Data snapshot:** [`545ed7e`](https://github.com/dotMR/access-review-agent/tree/545ed7e2ada397aebade1b44568d0e698315601c)
- **Model:**
    - Orphaned, Dormant admin-level, Dormant ad-hoc, Unapproved, Drift: deterministic rule-based checks, no AI model involved
    - Identity resolution: Claude Haiku 4.5 (Anthropic), for judgment on ambiguous cases
- **Reporting period:** 2026-Q3
- **Asset Owner:** TBD
- **Committed to:** `reports/2026-Q3/github.md`

One of these is generated per Information System (AWS, GitHub, Salesforce, Finance ERP, VPN) each quarter. This is the line-item evidence; the aggregated Quarterly Audit Report links to these rather than repeating their contents.

## Summary

| Category | Open | Remediated | Accepted risk | Total |
| :-- | --: | --: | --: | --: |
| Orphaned access | 0 | 0 | 0 | 0 |
| Dormant admin-level access | 1 | 0 | 0 | 1 |
| Unapproved access | 0 | 0 | 0 | 0 |
| Identity resolution | 1 | 0 | 0 | 1 |
| Drift | 0 | 0 | 0 | 0 |
| Dormant ad-hoc access | 0 | 0 | 0 | 0 |
| **Total** | 2 | 0 | 0 | 2 |

## Findings

### Orphaned access

_No findings._

### Dormant admin-level access (90-day threshold)

| Identity | Access detail | Expected per policy | Last used | Days dormant | Status | Issue |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| Bobson Dugnutt | `admin` access to github | Revoke if unused &gt; 90 consecutive days | 2026-06-11 | 95 | Open | [#68](https://github.com/dotMR/access-review-agent/issues/68) |

### Unapproved access

_No findings._

### Identity resolution

| Access record (`employee_id` or local identifier) | Access detail | Resolution | Evidence cited | Date detected | Status | Issue |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| svc-cicd-deploy | `write` access to github | `stale-ownership` | `The provisioning_note clearly identifies Cecilia Tisio (Platform Engineering) as the accountable owner of this CI/CD service account. Cecilia Tisio is found in HRIS as E9301 but her status is terminated as of 2026-09-14.` | 2026-09-14 | Open | [#71](https://github.com/dotMR/access-review-agent/issues/71) |

### Drift

_No findings._

### Dormant ad-hoc access (180-day threshold)

_No findings._

## Sign-off

I attest that the findings above for GitHub have been reviewed and, where applicable, remediated or formally accepted as risk.

- **Asset Owner:** TBD
- **Date:** _(pending sign-off)_
