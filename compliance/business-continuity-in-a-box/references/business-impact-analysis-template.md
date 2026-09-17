# Business Impact Analysis (BIA) Template & Methodology

A standardized framework for evaluating operational dependencies, quantifying financial, regulatory, and reputational downtime impacts, and determining recovery metrics (MTD, RTO, RPO, WRT) in accordance with **ISO 22301** and **APRA CPS 230**.

---

## 1. Key Metrics & Definitions

- **Maximum Tolerable Downtime (MTD)**: The maximum duration a business process can be inoperative before irreversible damage occurs to viability, legal compliance, or solvency.
- **Recovery Time Objective (RTO)**: The targeted duration within which a system or process must be fully restored to operation following an outage ($\text{RTO} \le \text{MTD}$).
- **Work Recovery Time (WRT)**: The time required after systems are restored to verify data integrity, clear backlogs, and return to normal production operations ($\text{RTO} + \text{WRT} \le \text{MTD}$).
- **Recovery Point Objective (RPO)**: The maximum allowable age of data loss measured in time (e.g., 5 minutes of transaction logs).
- **Minimum Viable Operating Level (MVOL)**: The bare-minimum system throughput or functional scope required to sustain emergency operations during an active incident.

---

## 2. Quantitative Impact Scoring Matrix

Score each impact dimension on a 1–5 scale based on outage duration:

| Scale | Financial Loss | Regulatory & Legal Exposure | Customer & Reputational Impact | Operational Impairment |
| :---: | :--- | :--- | :--- | :--- |
| **1 (Negligible)** | $< \$1,000$ AUD | None; within normal operational variances | Minor cosmetic inconvenience; $< 5$ inquiries | Workaround exists; minimal manual effort |
| **2 (Low)** | $\$1,000 - \$10,000$ AUD | Informal inquiry possible; no breach | $< 5\%$ users affected; minor SLA credit | Routine internal delays; no external block |
| **3 (Moderate)** | $\$10,000 - \$50,000$ AUD | Reportable incident threshold (non-material) | Core workflow disrupted for $< 20\%$ users | Upstream dependencies delayed; manual queue |
| **4 (Severe)** | $\$50,000 - \$250,000$ AUD | Mandatory regulator notification (OAIC/AUSTRAC) | High-profile enterprise complaints; churn risk | Core customer transactions fully blocked |
| **5 (Catastrophic)** | $> \$250,000$ AUD | Formal enforcement, license suspension, APRA action | Public scandal, breach of contracts, class action | Complete collapse of business infrastructure |

---

## 3. Critical Business Function (CBF) Inventory Template

Use this structure to catalog and evaluate every system component:

```markdown
### CBF-[ID]: [Function Name]
- **Primary Owner**: [Name & Role]
- **Criticality Tier**: Tier 0 / Tier 1 / Tier 2 / Tier 3
- **Business Description**: [Brief description of what this function delivers]
- **Minimum Viable Operating Level (MVOL)**: [e.g., 50% capacity, read-only search, manual review]
- **Time-Phased Impact**:
  - *At 1 Hour*: [Financial / Reg / Reputational score]
  - *At 4 Hours*: [Financial / Reg / Reputational score]
  - *At 24 Hours*: [Financial / Reg / Reputational score]
  - *At 72 Hours*: [Financial / Reg / Reputational score]
- **Recovery Targets**:
  - **MTD**: [e.g., 2 hours]
  - **RTO**: [e.g., 30 minutes]
  - **RPO**: [e.g., 5 minutes]
  - **WRT**: [e.g., 30 minutes]
- **Dependencies**:
  - *Upstream Inputs*: [e.g., Cloudflare DNS, AWS RDS, Stripe Webhooks]
  - *Downstream Dependents*: [e.g., Client Portal, Webhook Delivery]
  - *External Vendors*: [e.g., ASIC Registry, SendGrid, Auth0]
  - *Personnel Requirements*: [e.g., 1 Backend On-Call Engineer]
- **Degraded Operating Procedure**: [What manual or fallback process can be run while down?]
```

---

## 4. Sample BIA Matrix: B2B RegTech / Fintech Platform (e.g. AMLHive)

| Function ID | Critical Business Function | Owner | Tier | MTD | RTO | RPO | Upstream Dependencies | Regulatory / Financial Impact | Degraded Mode Workaround |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- | :--- |
| **CBF-01** | Real-Time AML/PEP Screening API | Lead Eng | Tier 0 | 1 hr | 15 min | 0 min | AWS Sydney, Postgres Aurora, Redis cache | AUSTRAC reporting breach, \$50k/hr SLA penalty | Serve cached high-risk lists; queue non-critical checks |
| **CBF-02** | User Authentication & Session Auth | SecOps | Tier 0 | 2 hr | 30 min | 5 min | Auth0 / Cognito, Redis session store | Complete user lockout, customer escalations | Fallback read-only JWT validation mode |
| **CBF-03** | ASIC / ABR Registry Sync Pipeline | Data Eng | Tier 1 | 8 hr | 2 hr | 1 hr | ASIC InfoTrack API, Batch Queue worker | Stale entity data, delayed onboarding | Use cached 24-hr company snapshot with stale disclaimer |
| **CBF-04** | Client Verification Certificate PDF Gen | Product | Tier 1 | 12 hr | 3 hr | 15 min | Chromium headless, S3 storage bucket | Clients unable to finalize onboarding audits | Email raw JSON verification summary to compliance officer |
| **CBF-05** | Monthly Billing & Invoice Dispatch | Finance | Tier 2 | 48 hr | 12 hr | 24 hr | Stripe Billing API, Accounting Webhook | Cash collection delay, zero regulatory breach | Grace period extension on all active subscriptions |
| **CBF-06** | Historical Audit Trail Search | Comp Lead | Tier 2 | 24 hr | 6 hr | 1 hr | OpenSearch cluster, S3 Glacier archive | Internal investigation delay, minor audit friction | Point-in-time SQL direct dump query from replica |

---

## 5. Dependency Vulnerability Analysis Checklist

- [ ] **Single Point of Failure (SPOF) Detection**: Does any Tier-0/1 function rely on a single cloud provider, single availability zone, or single human maintainer?
- [ ] **Data Residency Compliance**: If failing over to a secondary cloud region or third-party backup, is all data retained within sovereign Australian borders (APRA CPS 234 / Privacy Act)?
- [ ] **Third-Party SLA Mismatch**: Does an upstream vendor offer 99.5% uptime (3.6 hours downtime/month) while your customer contract promises 99.9% uptime (43 minutes downtime/month)?
- [ ] **Credential Isolation**: Are failover secrets and disaster recovery access keys stored outside the compromised primary infrastructure perimeter?
