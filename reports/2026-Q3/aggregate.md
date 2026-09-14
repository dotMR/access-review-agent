# Quarterly Access Review Audit Report — 2026-Q3

- **Report generated:** 2026-09-14T07:21:08.083086+00:00
- **Data snapshot:** [`545ed7e`](https://github.com/dotMR/access-review-agent/tree/545ed7e2ada397aebade1b44568d0e698315601c)
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
| Orphaned access | AWS | Low | Medium | Low | Issue &#35;70 concerning orphaned AWS access (Cecilia Tisio) was identified in this audit and has been remediated, indicating a prompt response by system maintainers to the access anomaly. The finding appears in this audit only with status already resolved, characterizing this as an isolated incident rather than a recurring pattern across consecutive audit periods.<br><br>Recommendation: No action is needed; the isolated finding was resolved within this audit cycle. |
| Drift | AWS | Medium | Medium | Medium | This finding reflects a recurring control gap rather than an isolated incident. Issue &#35;69 has remained open across two consecutive audit cycles, indicating that drift in AWS access controls is persisting without remediation between review periods. The pattern suggests insufficient prioritization or resource allocation to address the underlying access-control drift mechanisms.<br><br>Recommendation: Define and assign explicit ownership with measurable remediation milestones for Issue &#35;69, including automated controls or periodic validation processes to prevent further drift accumulation in AWS access across future audit cycles. |
| Unapproved access | AWS | High | Medium | High | The unapproved AWS access issue documented in &#35;64 has remained open across three consecutive audits, establishing a clear pattern of non-remediation rather than an isolated gap. This persistence across multiple audit cycles indicates that existing escalation and follow-up procedures are insufficient to drive closure of these access violations. The recurring status demonstrates a systemic weakness in the approval workflow or remediation accountability that requires intervention.<br><br>Recommendation: Establish a dedicated remediation owner for unapproved AWS access issues with explicit closure deadlines and mandatory escalation to leadership if any issues remain open across consecutive audit cycles. |
| Identity resolution | GitHub | Low | Medium | Low | Issue &#35;71 (svc-cicd-deploy) appears solely within the current audit period, representing an isolated finding without evidence of recurrence across multiple audit cycles. The open status indicates the concern remains unresolved operationally, but its non-recurring presence suggests a context-specific or newly emerged issue rather than a systemic control gap. Given that this is the first appearance in the audit trail, there is no pattern of persistence that would warrant a process-level intervention.<br><br>Recommendation: No process-level action is required; standard remediation procedures should address the open issue, with monitoring in the next audit cycle to confirm it does not establish a recurring pattern. |
| Dormant admin-level access | GitHub | Medium | Medium | Medium | The dormant administrator access in GitHub represents a recurring control gap that persists across two consecutive audit cycles, as evidenced by Issue &#35;68 remaining open. The failure to remediate this finding within a single audit period indicates insufficient prioritization or process ownership for administrative access governance. This prolonged exposure elevates risk by extending the window during which stale credentials could be compromised or misused.<br><br>Recommendation: Assign explicit ownership and establish a formal remediation deadline for deactivating, rotating, or transferring all dormant administrative accounts in GitHub, with documented completion evidence required before the next audit cycle. |
| Dormant ad-hoc access | Salesforce | High | Low | Medium | The dormant ad-hoc access issue in Salesforce (&#35;62) is a recurring finding that has persisted across three consecutive audit cycles, demonstrating a systemic failure to remediate access gaps despite prior identification. While the low impact rating reflects the limited damage potential of inactive accounts, the high likelihood underscores a pattern of inadequate deprovisioning or periodic access hygiene procedures. The extended open status over multiple audit windows indicates this is not a one-off oversight but an operational control deficiency requiring escalated attention.<br><br>Recommendation: Establish a formal quarterly dormant account review and remediation process for Salesforce with documented cleanup timelines and executive accountability to resolve this recurring access control gap. |
| Dormant admin-level access | Finance ERP | High | High | Critical | Dana Whitfield's dormant administrative account (Issue &#35;61) remains open across three consecutive audit cycles, indicating a persistent pattern rather than an isolated incident. The unresolved status despite multiple audit notices suggests existing escalation processes have not produced remediation. A recurring finding of this severity in a Critical-rated financial systems access control warrants formal enforcement or procedural escalation.<br><br>Recommendation: Establish a mandatory remediation timeline with defined owner and escalation authority; if account deactivation cannot proceed, document explicit business justification and implement compensating controls approved by system owner and audit. |

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
- Data snapshot: [`545ed7e`](https://github.com/dotMR/access-review-agent/tree/545ed7e2ada397aebade1b44568d0e698315601c)
- PDF export: bundled as a Release asset (`aggregate.pdf`) alongside the tagged commit - see the Releases page for this period, not this Markdown file's own directory.

---
<!-- Out of scope (not shown in this report): Dormant admin-level's, Dormant ad-hoc's, and Drift's own monthly Operational/SLA variants, and the Unapproved-access grant-time gate — see SPEC.md §8. -->