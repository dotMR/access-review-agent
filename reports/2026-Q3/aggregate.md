# Quarterly Access Review Audit Report — 2026-Q3

- **Report generated:** 2026-10-01T05:03:02.025199+00:00
- **Data snapshot:** [`386e06d`](https://github.com/dotMR/access-review-agent/tree/386e06d85cbe505d78a2c7ccf8c646d742924942)
- **Model:**
    - Orphaned, Dormant admin-level, Dormant ad-hoc, Unapproved, Drift: deterministic rule-based checks, no AI model involved
    - Identity resolution: Claude Haiku 4.5 (Anthropic), for judgment on ambiguous cases
- **Reporting period:** 2026-Q3
- **Systems in scope:** AWS, GitHub, Salesforce, Finance ERP, VPN
- **ISO 27001:2022 controls addressed:** A.5.15 (Access control), A.5.16 (Identity management), A.5.18 (Access rights), A.8.2 (Privileged access rights)
- **SOC 2 Common Criteria addressed:** CC6.1 (Logical access controls), CC6.2 (Access provisioning and de-provisioning), CC6.3 (Role-based access, least privilege, and segregation of duties)
- **Committed to:** `reports/2026-Q3/aggregate.md`

This is the formal audit-evidence record for the period — the rollup of the five per-system reports below. It aggregates and links to their line-item findings rather than repeating them.

## Executive summary

10 findings identified this quarter across 6 finding categories and 5 Information Systems.

- Remediated: 3
- Open: 6
- Accepted as risk: 1

## Trend

| Period | Total | Open | Remediated | Accepted risk | Δ Total |
| :-- | --: | --: | --: | --: | --: |
| 2026-Q1 | 5 | 5 | 0 | 0 | N/A, first period |
| 2026-Q2 | 8 | 5 | 2 | 1 | +3 |
| 2026-Q3 | 10 | 6 | 3 | 1 | +2 |

## Methodology

The Access Review Agent performed an automated cross-reference of each Information System's access records (Access/IT System) against the HRIS and the Access Policy Repository, per the Operational review and Compliance review Principles in access-control-policy.md.

## Resolution status by system

| System | Open | Remediated | Accepted risk | Total | Detail |
| :-- | --: | --: | --: | --: | :-- |
| AWS | 2 | 2 | 0 | 4 | [aws.md](./aws.md) |
| GitHub | 2 | 0 | 0 | 2 | [github.md](./github.md) |
| Salesforce | 1 | 0 | 0 | 1 | [salesforce.md](./salesforce.md) |
| Finance ERP | 1 | 0 | 0 | 1 | [finance-erp.md](./finance-erp.md) |
| VPN | 0 | 1 | 1 | 2 | [vpn.md](./vpn.md) |
| **Total** | 6 | 3 | 1 | 10 | |

Line-item detail for every finding lives in the per-system reports linked above and in the Appendix, not here.

## Findings by category (aggregate)

| Category | Open | Remediated | Accepted risk | Total |
| :-- | --: | --: | --: | --: |
| Orphaned access | 0 | 2 | 0 | 2 |
| Dormant admin-level access | 2 | 0 | 0 | 2 |
| Unapproved access | 1 | 1 | 0 | 2 |
| Identity resolution | 1 | 0 | 1 | 2 |
| Drift | 1 | 0 | 0 | 1 |
| Dormant ad-hoc access | 1 | 0 | 0 | 1 |

## Risk Assessment

| Category | System | Likelihood | Impact | Risk Rating | Treatment |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Orphaned access | AWS | Low | Medium | Low | _(narrative synthesis disabled for this run — set generate_narrative=True / ENABLE_RISK_ASSESSMENT_NARRATIVE=true to generate; Likelihood/Impact/Risk Rating above are still real, computed values)_ |
| Drift | AWS | Medium | Medium | Medium | _(narrative synthesis disabled for this run — set generate_narrative=True / ENABLE_RISK_ASSESSMENT_NARRATIVE=true to generate; Likelihood/Impact/Risk Rating above are still real, computed values)_ |
| Unapproved access | AWS | High | Medium | High | _(narrative synthesis disabled for this run — set generate_narrative=True / ENABLE_RISK_ASSESSMENT_NARRATIVE=true to generate; Likelihood/Impact/Risk Rating above are still real, computed values)_ |
| Identity resolution | GitHub | Low | Medium | Low | _(narrative synthesis disabled for this run — set generate_narrative=True / ENABLE_RISK_ASSESSMENT_NARRATIVE=true to generate; Likelihood/Impact/Risk Rating above are still real, computed values)_ |
| Dormant admin-level access | GitHub | Medium | Medium | Medium | _(narrative synthesis disabled for this run — set generate_narrative=True / ENABLE_RISK_ASSESSMENT_NARRATIVE=true to generate; Likelihood/Impact/Risk Rating above are still real, computed values)_ |
| Dormant ad-hoc access | Salesforce | High | Low | Medium | _(narrative synthesis disabled for this run — set generate_narrative=True / ENABLE_RISK_ASSESSMENT_NARRATIVE=true to generate; Likelihood/Impact/Risk Rating above are still real, computed values)_ |
| Dormant admin-level access | Finance ERP | High | High | Critical | _(narrative synthesis disabled for this run — set generate_narrative=True / ENABLE_RISK_ASSESSMENT_NARRATIVE=true to generate; Likelihood/Impact/Risk Rating above are still real, computed values)_ |

## Escalations this period

| Finding | System | Category | Open since | Escalated | Status | Issue |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| Ronnis Pawgood | AWS | Orphaned access | 2026-09-13T13:14:46+00:00 | 2026-09-14T06:33:55+00:00 | Remediated | [#63](https://github.com/dotMR/access-review-agent/issues/63) |

## Reviewer attestation

I have reviewed this report and the underlying per-system reports, and accept this as the formal audit-evidence record for the period stated above.

- **Security/Compliance Reviewer:** TBD
- **Date:** _(pending sign-off)_

## Appendix

- Per-system reports: [AWS](./aws.md) · [GitHub](./github.md) · [Salesforce](./salesforce.md) · [Finance ERP](./finance-erp.md) · [VPN](./vpn.md)
- Data snapshot: [`386e06d`](https://github.com/dotMR/access-review-agent/tree/386e06d85cbe505d78a2c7ccf8c646d742924942)
- PDF export: bundled as a Release asset (`aggregate.pdf`) alongside the tagged commit - see the Releases page for this period, not this Markdown file's own directory.

---
<!-- Out of scope (not shown in this report): Dormant admin-level's, Dormant ad-hoc's, and Drift's own monthly Operational/SLA variants, and the Unapproved-access grant-time gate — see SPEC.md §8. -->