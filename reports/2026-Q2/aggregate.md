# Quarterly Access Review Audit Report — 2026-Q2

- **Report generated:** 2026-09-14T07:13:15.617489+00:00
- **Data snapshot:** [`5e55a4f`](https://github.com/dotMR/access-review-agent/tree/5e55a4f57ce1136498ee1019fb25e152160f3a4d)
- **Model:**
    - Orphaned, Dormant admin-level, Dormant ad-hoc, Unapproved, Drift: deterministic rule-based checks, no AI model involved
    - Identity resolution: Claude Haiku 4.5 (Anthropic), for judgment on ambiguous cases
- **Reporting period:** 2026-Q2
- **Systems in scope:** AWS, GitHub, Salesforce, Finance ERP, VPN
- **ISO 27001:2022 controls addressed:** A.5.15 (Access control), A.5.16 (Identity management), A.5.18 (Access rights), A.8.2 (Privileged access rights)
- **SOC 2 Common Criteria addressed:** CC6.1 (Logical access controls), CC6.2 (Access provisioning and de-provisioning), CC6.3 (Role-based access, least privilege, and segregation of duties)
- **Committed to:** `reports/2026-Q2/aggregate.md`

This is the formal audit-evidence record for the period — the rollup of the five per-system reports below. It aggregates and links to their line-item findings rather than repeating them.

## Executive summary

8 findings identified this quarter across 6 finding categories and 5 Information Systems.

- Remediated: 2
- Open: 5
- Accepted as risk: 1

## Trend

| Period | Total | Open | Remediated | Accepted risk | Δ Total |
| :-- | --: | --: | --: | --: | --: |
| 2026-Q1 | 5 | 5 | 0 | 0 | N/A, first period |
| 2026-Q2 | 8 | 5 | 2 | 1 | +3 |

## Methodology

The Access Review Agent performed an automated cross-reference of each Information System's access records (Access/IT System) against the HRIS and the Access Policy Repository, per the Operational review and Compliance review Principles in access-control-policy.md.

## Resolution status by system

| System | Open | Remediated | Accepted risk | Total | Detail |
| :-- | --: | --: | --: | --: | :-- |
| AWS | 2 | 1 | 0 | 3 | [aws.md](./aws.md) |
| GitHub | 1 | 0 | 0 | 1 | [github.md](./github.md) |
| Salesforce | 1 | 0 | 0 | 1 | [salesforce.md](./salesforce.md) |
| Finance ERP | 1 | 0 | 0 | 1 | [finance-erp.md](./finance-erp.md) |
| VPN | 0 | 1 | 1 | 2 | [vpn.md](./vpn.md) |
| **Total** | 5 | 2 | 1 | 8 | |

Line-item detail for every finding lives in the per-system reports linked above and in the Appendix, not here.

## Findings by category (aggregate)

| Category | Open | Remediated | Accepted risk | Total |
| :-- | --: | --: | --: | --: |
| Orphaned access | 0 | 1 | 0 | 1 |
| Dormant admin-level access | 2 | 0 | 0 | 2 |
| Unapproved access | 1 | 1 | 0 | 2 |
| Identity resolution | 0 | 0 | 1 | 1 |
| Drift | 1 | 0 | 0 | 1 |
| Dormant ad-hoc access | 1 | 0 | 0 | 1 |

## Risk Assessment

| Category | System | Likelihood | Impact | Risk Rating | Treatment |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Drift | AWS | Low | Medium | Low | The drift issue in AWS is isolated to this audit period, with only Issue &#35;69 identified and no pattern of recurrence from prior audit cycles. This single-audit occurrence does not indicate a systemic control weakness requiring process-level intervention. The finding should be resolved through standard remediation procedures.<br><br>Recommendation: No process-level treatment is needed for an isolated, non-recurring finding. |
| Unapproved access | AWS | Medium | Medium | Medium | Issue &#35;64 has remained open across two consecutive audits without resolution, establishing this as a recurring access governance gap for AWS. The persistence of this finding across audit cycles indicates that previous remediation efforts were either insufficient or not completed, requiring escalated treatment beyond standard issue management. This recurring pattern on a medium-risk system warrants process-level intervention to prevent further cycles of non-closure.<br><br>Recommendation: Establish a formal remediation plan for issue &#35;64 with assigned accountability and a mandatory closure date, monitored through monthly access governance reviews. |
| Orphaned access | AWS | Low | Medium | Low | Issue &#35;63 represents an isolated finding in the orphaned AWS access category that was identified and remediated within this audit cycle. With a status of Remediated and appearing only once across the current audit period, there is no pattern of recurrence or persistence. The rapid resolution indicates effective incident response for this specific instance.<br><br>Recommendation: No action is needed; the isolated finding was already remediated within this audit cycle. |
| Dormant admin-level access | GitHub | Low | Medium | Low | The dormant admin access finding in GitHub identified in Issue &#35;68 is new to this audit and has not appeared in prior audits, indicating an isolated occurrence rather than a recurring pattern. With a Low risk rating, this finding does not suggest a systemic control weakness requiring process-level remediation.<br><br>Recommendation: No action is needed. |
| Dormant ad-hoc access | Salesforce | Medium | Low | Low | Issue &#35;62 represents a persistent dormant ad-hoc access gap in Salesforce, remaining open across two consecutive audits. The continued presence of this finding suggests that previous remediation attempts have not fully addressed the underlying access control vulnerabilities. Sustained corrective action is required to address the root cause and prevent further recurrence.<br><br>Recommendation: Develop and execute a formal remediation plan with defined milestones and ownership for resolving &#35;62 by the next audit period. |
| Dormant admin-level access | Finance ERP | Medium | High | High | Issue &#35;61 involving Dana Whitfield demonstrates a recurring pattern of dormant administrator access in the finance_erp system, having remained open across two consecutive audits. The persistence of this finding across multiple audit cycles indicates this is not an isolated incident but a systemic access control gap that has not been remediated. Given the High risk rating stemming from both the system's criticality and the extended exposure window, formal remediation action is overdue.<br><br>Recommendation: Establish a documented remediation plan for Issue &#35;61 with a specific deadline and assigned owner; if access cannot be immediately revoked, require written business justification approved by system and security stakeholders within 30 days. |
| Unapproved access | VPN | Low | Low | Low | Issue &#35;67 represents a single instance of unapproved VPN access that was identified and remediated within this audit cycle, showing no pattern of recurrence across multiple audits. The swift remediation indicates that the underlying access-control process functioned as intended when the exception was discovered. Given the isolated nature of this finding and its complete resolution within one audit period, no systemic process improvement is required.<br><br>Recommendation: No action needed; the finding was already resolved within this audit cycle. |
| Identity resolution | VPN | Low | Low | Low | Issue &#35;65 (vpn-legacy-4402) appears for the first time in this audit with an accepted risk status and maintains a Low risk rating across all dimensions. With only a single audit occurrence and no evidence of recurrence across consecutive audits, this finding does not constitute a persistent pattern. The organization's explicit acceptance of this risk exposure indicates it has been evaluated and deliberately managed.<br><br>Recommendation: No action is needed; the isolated, low-risk nature of this finding does not warrant process-level treatment. |

## Escalations this period

_No escalations this period._

## Reviewer attestation

I have reviewed this report and the underlying per-system reports, and accept this as the formal audit-evidence record for the period stated above.

- **Security/Compliance Reviewer:** TBD
- **Date:** _(pending sign-off)_

## Appendix

- Per-system reports: [AWS](./aws.md) · [GitHub](./github.md) · [Salesforce](./salesforce.md) · [Finance ERP](./finance-erp.md) · [VPN](./vpn.md)
- Data snapshot: [`5e55a4f`](https://github.com/dotMR/access-review-agent/tree/5e55a4f57ce1136498ee1019fb25e152160f3a4d)
- PDF export: bundled as a Release asset (`aggregate.pdf`) alongside the tagged commit - see the Releases page for this period, not this Markdown file's own directory.

---
<!-- Out of scope (not shown in this report): Dormant admin-level's, Dormant ad-hoc's, and Drift's own monthly Operational/SLA variants, and the Unapproved-access grant-time gate — see SPEC.md §8. -->