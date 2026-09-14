# Access Review — VPN — 2026-Q3

- **Report generated:** 2026-09-14T07:21:08.083086+00:00
- **Data snapshot:** [`545ed7e`](https://github.com/dotMR/access-review-agent/tree/545ed7e2ada397aebade1b44568d0e698315601c)
- **Model:**
    - Orphaned, Dormant admin-level, Dormant ad-hoc, Unapproved, Drift: deterministic rule-based checks, no AI model involved
    - Identity resolution: Claude Haiku 4.5 (Anthropic), for judgment on ambiguous cases
- **Reporting period:** 2026-Q3
- **Asset Owner:** TBD
- **Committed to:** `reports/2026-Q3/vpn.md`

One of these is generated per Information System (AWS, GitHub, Salesforce, Finance ERP, VPN) each quarter. This is the line-item evidence; the aggregated Quarterly Audit Report links to these rather than repeating their contents.

## Summary

| Category | Open | Remediated | Accepted risk | Total |
| :-- | --: | --: | --: | --: |
| Orphaned access | 0 | 0 | 0 | 0 |
| Dormant admin-level access | 0 | 0 | 0 | 0 |
| Unapproved access | 0 | 1 | 0 | 1 |
| Identity resolution | 0 | 0 | 1 | 1 |
| Drift | 0 | 0 | 0 | 0 |
| Dormant ad-hoc access | 0 | 0 | 0 | 0 |
| **Total** | 0 | 1 | 1 | 2 |

## Findings

### Orphaned access

_No findings._

### Dormant admin-level access (90-day threshold)

_No findings._

### Unapproved access

| Identity | Access detail | Expected per policy | Date granted | Approved by | Status | Issue |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| Todd Bonzalez | `granted` access to vpn | A recorded approval (auto or Asset Owner) on file | 2026-09-14 | none on file | Remediated | [#67](https://github.com/dotMR/access-review-agent/issues/67) |

### Identity resolution

| Access record (`employee_id` or local identifier) | Access detail | Resolution | Evidence cited | Date detected | Status | Issue |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| vpn-legacy-4402 | `granted` access to vpn | `unresolved` | `The identifier 'vpn-legacy-4402' does not match any current HRIS employee_id, and the provisioning_note is empty with no identifying information. While the record is actively used, there is no evidence to confidently match it to a specific employee.` | 2026-09-13 | Accepted risk | [#65](https://github.com/dotMR/access-review-agent/issues/65) |

### Drift

_No findings._

### Dormant ad-hoc access (180-day threshold)

_No findings._

## Sign-off

I attest that the findings above for VPN have been reviewed and, where applicable, remediated or formally accepted as risk.

- **Asset Owner:** TBD
- **Date:** _(pending sign-off)_
