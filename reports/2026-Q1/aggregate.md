# Quarterly Access Review Audit Report — 2026-Q1

- **Report generated:** 2026-09-14T06:36:03.800079+00:00
- **Data snapshot:** [`7da17ee`](https://github.com/dotMR/access-review-agent/tree/7da17ee0ad75b43766a5a462dab275fe987179c4)
- **Model:**
    - Orphaned, Dormant admin-level, Dormant ad-hoc, Unapproved, Drift: deterministic rule-based checks, no AI model involved
    - Identity resolution: Claude Haiku 4.5 (Anthropic), for judgment on ambiguous cases
- **Reporting period:** 2026-Q1
- **Systems in scope:** AWS, GitHub, Salesforce, Finance ERP, VPN
- **ISO 27001:2022 controls addressed:** A.5.15 (Access control), A.5.16 (Identity management), A.5.18 (Access rights), A.8.2 (Privileged access rights)
- **SOC 2 Common Criteria addressed:** CC6.1 (Logical access controls), CC6.2 (Access provisioning and de-provisioning), CC6.3 (Role-based access, least privilege, and segregation of duties)
- **Committed to:** `reports/2026-Q1/aggregate.md`

This is the formal audit-evidence record for the period — the rollup of the five per-system reports below. It aggregates and links to their line-item findings rather than repeating them.

## Executive summary

5 findings identified this quarter across 6 finding categories and 5 Information Systems.

- Remediated: 0
- Open: 5
- Accepted as risk: 0

## Trend

| Period | Total | Open | Remediated | Accepted risk | Δ Total |
| :-- | --: | --: | --: | --: | --: |
| 2026-Q1 | 5 | 5 | 0 | 0 | N/A, first period |

## Methodology

The Access Review Agent performed an automated cross-reference of each Information System's access records (Access/IT System) against the HRIS and the Access Policy Repository, per the Operational review and Compliance review Principles in access-control-policy.md.

## Resolution status by system

| System | Open | Remediated | Accepted risk | Total | Detail |
| :-- | --: | --: | --: | --: | :-- |
| AWS | 2 | 0 | 0 | 2 | [aws.md](./aws.md) |
| GitHub | 0 | 0 | 0 | 0 | [github.md](./github.md) |
| Salesforce | 1 | 0 | 0 | 1 | [salesforce.md](./salesforce.md) |
| Finance ERP | 1 | 0 | 0 | 1 | [finance-erp.md](./finance-erp.md) |
| VPN | 1 | 0 | 0 | 1 | [vpn.md](./vpn.md) |
| **Total** | 5 | 0 | 0 | 5 | |

Line-item detail for every finding lives in the per-system reports linked above and in the Appendix, not here.

## Findings by category (aggregate)

| Category | Open | Remediated | Accepted risk | Total |
| :-- | --: | --: | --: | --: |
| Orphaned access | 1 | 0 | 0 | 1 |
| Dormant admin-level access | 1 | 0 | 0 | 1 |
| Unapproved access | 1 | 0 | 0 | 1 |
| Identity resolution | 1 | 0 | 0 | 1 |
| Drift | 0 | 0 | 0 | 0 |
| Dormant ad-hoc access | 1 | 0 | 0 | 1 |

## Risk Assessment

| Category | System | Likelihood | Impact | Risk Rating | Treatment |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Unapproved access | AWS | Low | Medium | Low | Issue &#35;64 appears only in the current audit, representing an isolated finding rather than a recurring pattern across multiple audit cycles. This single occurrence suggests a one-time administrative oversight or provisioning gap rather than a systemic weakness in AWS access controls. Prompt remediation to resolve the unapproved access for Mike Truk is necessary.<br><br>Recommendation: Direct remediation of issue &#35;64 is required, but no process-level access control enhancements are warranted based on this isolated single-audit finding. |
| Orphaned access | AWS | Low | Medium | Low | Issue &#35;63 constitutes an isolated finding in this audit period with no evidence of recurrence across prior audit cycles. The single-issue nature combined with a Low risk rating indicates this does not represent a persistent or systemic pattern requiring process-level remediation. Recommendation: No process-level action is required; the identified issue should proceed through standard remediation procedures. |
| Dormant ad-hoc access | Salesforce | Low | Low | Low | Issue &#35;62 appears only in the current audit and has not recurred across multiple audit cycles. The low likelihood and low impact ratings indicate this represents an isolated finding rather than a systemic pattern requiring process-level intervention.<br><br>Recommendation: No action is needed. |
| Dormant admin-level access | Finance ERP | Low | High | Medium | Issue &#35;61 is an isolated finding appearing only in the current audit cycle, not persisting from prior assessments, indicating a one-off incident rather than a recurring access-control pattern in the finance_erp system. The high impact designation warrants timely remediation of this specific concern, though the absence of recurrence suggests no underlying process failures requiring systemic intervention.<br><br>Recommendation: No action is needed since this is an isolated occurrence not indicative of recurring access-control deficiencies. |
| Identity resolution | VPN | Low | Low | Low | Issue &#35;65 (vpn-legacy-4402) represents an isolated identity-resolution gap in the VPN system, appearing in this audit cycle only with uniformly low likelihood and impact ratings. The finding is not part of a recurring pattern, as it has not persisted across multiple consecutive audits. Standard closure procedures should resolve the underlying control deficiency without requiring systemic process changes.<br><br>Recommendation: No action is needed as this represents an isolated finding in a single audit cycle. |

## Escalations this period

_No escalations this period._

## Reviewer attestation

I have reviewed this report and the underlying per-system reports, and accept this as the formal audit-evidence record for the period stated above.

- **Security/Compliance Reviewer:** TBD
- **Date:** _(pending sign-off)_

## Appendix

- Per-system reports: [AWS](./aws.md) · [GitHub](./github.md) · [Salesforce](./salesforce.md) · [Finance ERP](./finance-erp.md) · [VPN](./vpn.md)
- Data snapshot: [`7da17ee`](https://github.com/dotMR/access-review-agent/tree/7da17ee0ad75b43766a5a462dab275fe987179c4)
- PDF export: bundled as a Release asset (`aggregate.pdf`) alongside the tagged commit - see the Releases page for this period, not this Markdown file's own directory.

---
<!-- Out of scope (not shown in this report): Dormant admin-level's, Dormant ad-hoc's, and Drift's own monthly Operational/SLA variants, and the Unapproved-access grant-time gate — see SPEC.md §8. -->