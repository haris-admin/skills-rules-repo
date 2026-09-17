# Tabletop Exercise Playbook & Simulation Drills

A comprehensive simulation playbook containing 4 ready-to-run tabletop disaster scenarios, structured inject schedules, evaluation scorecards, and regulatory audit artifacts meeting **APRA CPS 230** and **ISO 22301** requirements.

---

## 1. Simulation Planning & Roles

- **Frequency**: Conduct at least once every 12 months, or within 60 days of a major architectural overhaul.
- **Duration**: 90 to 120 minutes.
- **Participants**:
  - **Exercise Director / Facilitator**: Introduces injects, manages simulation time, observes dynamics.
  - **Incident Commander (IC)**: Manages response, makes strategic calls.
  - **Technical Responders**: SRE, DevOps, App Security, Core Engineers.
  - **Business / Legal Responders**: Communications Lead, General Counsel, Compliance Officer, Executive Sponsor.
  - **Evaluation Observers**: Neutral note-takers evaluating compliance against predefined rubrics.

---

## 2. Four Ready-to-Run Simulation Scenarios

### Scenario A: Cloud Region Catastrophe & Primary DB Crash
- **Context**: A major physical event disables AWS `ap-southeast-2` (Sydney). The active Aurora database crashes mid-transaction.
- **Key Testing Objectives**: RTO/RPO adherence, cross-region standby promotion, split-brain prevention, customer status broadcasting.
- **Inject Schedule**:
  - **T+00m (Inject 1)**: Monitoring alerts fire across all services; HTTP 502/504 errors spike to 95%. AWS status dashboard displays degraded core networking in Sydney.
  - **T+20m (Inject 2)**: AWS announces multi-hour power disruption at the primary availability zone. Automated replica promotion in Melbourne fails due to an expired IAM role permission.
  - **T+45m (Inject 3)**: Enterprise customers begin calling executive sponsors complaining about broken customer onboarding. An enterprise client threatens immediate SLA breach penalty.
  - **T+75m (Inject 4)**: Primary AWS zone begins flickering back online before data synchronization is re-established, creating a severe split-brain risk.

### Scenario B: Ransomware & Privileged Identity Compromise
- **Context**: An engineer's workstation was infected via a zero-day infostealer. Attackers accessed GitHub and AWS root-level credentials, encrypting S3 buckets and threatening data leaks.
- **Key Testing Objectives**: Out-of-band communication activation, credential revocation speed, immutable backup recovery, OAIC Notifiable Data Breach (NDB) 72-hour assessment.
- **Inject Schedule**:
  - **T+00m (Inject 1)**: Responders find an extortion note on the root domain (`readme_decrypt.txt`) and production database tables dropped or locked.
  - **T+20m (Inject 2)**: The corporate Slack and Google Workspace accounts are locked out; attackers revoked admin privileges.
  - **T+45m (Inject 3)**: Attackers post on X/Twitter claiming to have exfiltrated 50,000 Australian entity records and threatening to notify media in 2 hours.
  - **T+75m (Inject 4)**: The legal counsel asks whether the OAIC, AUSTRAC, and APRA must be formally notified immediately.

### Scenario C: Material Upstream Service Provider Collapse (APRA CPS 230)
- **Context**: The primary external identity and government registry integration (e.g. ASIC or identity document verification vendor) suffers an unannounced 72-hour collapse.
- **Key Testing Objectives**: Degradation mode activation, manual review workarounds, customer communication, queue buffer management.
- **Inject Schedule**:
  - **T+00m (Inject 1)**: Upstream registry API returns HTTP 503 Service Unavailable. Thousands of inbound verification requests begin failing and backlogging.
  - **T+20m (Inject 2)**: Vendor account representative confirms a nationwide database failure with no estimated time of restoration for at least 48 hours.
  - **T+45m (Inject 3)**: Customer onboarding funnel drops to 0%. Operations team attempts manual lookups but gets overwhelmed with 800 pending requests.
  - **T+75m (Inject 4)**: High-priority institutional client demands an offline manual verification protocol with signed compliance warranties.

### Scenario D: Key Personnel Incapacitation (Key Man Risk)
- **Context**: The sole lead DevOps / Cloud Architect is abruptly hospitalized during an off-hours infrastructure incident, and production secrets are inaccessible.
- **Key Testing Objectives**: Documentation accessibility, secret escrow retrieval, multi-person authorization, operational continuity without single points of human failure.
- **Inject Schedule**:
  - **T+00m (Inject 1)**: Production TLS certificate expires; automated renewal failed. Website displays security warning to all visitors.
  - **T+20m (Inject 2)**: On-call attempts to reach Lead DevOps Architect; phone unreachable. No other team member has direct access to the DNS registrar account.
  - **T+45m (Inject 3)**: Responders attempt to retrieve emergency backup credentials from password vault, but require an out-of-band second factor held on the missing engineer's phone.
  - **T+75m (Inject 4)**: CEO must authorize break-glass account recovery with domain registrar.

---

## 3. Tabletop Evaluation Rubric & Scorecard

Score each category from 1 (Unsatisfactory) to 5 (Exemplary):

| Evaluation Dimension | Scoring Criteria | Score (1–5) | Observations / Notes |
| :--- | :--- | :---: | :--- |
| **1. Command & Control** | Clear IC established within 10 mins; structured SitReps distributed; roles respected without chaotic overlap. | | |
| **2. Technical Execution** | Runbooks followed accurately; failover steps executed safely; split-brain avoided; smoke tests performed. | | |
| **3. Comms & Transparency** | External status page updated within 20 mins; customers informed; clear FAQs provided to customer success. | | |
| **4. Regulatory & Legal** | Mandatory notification clocks identified (OAIC 72h / APRA CPS 230); legal privilege preserved; records kept. | | |
| **5. RTO / RPO Target Feasibility**| Recovery achieved within stated RTO targets; data loss kept within stated RPO limits. | | |

**Overall Readiness Grade**:
- **$\ge 22 / 25$**: High Operational Resilience (Pass)
- **$18 - 21 / 25$**: Moderate Resilience (Conditional Pass, remediate minor gaps in 30 days)
- **$< 18 / 25$**: High Vulnerability (Fail, mandatory re-test in 60 days)

---

## 4. Corrective Action Plan (CAP) Register

Document all identified deficiencies immediately following the hotwash review:

| CAP ID | Finding / Vulnerability | Root Cause | Corrective Action | Owner | Target Date | Status |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: |
| **CAP-01** | Standby replica promotion failed due to expired IAM permissions | Lack of automated role validation | Add automated Terraform drift detection test for cross-region DR roles | SRE Lead | 14 days | Open |
| **CAP-02** | External statuspage login required compromised corporate SSO | Single sign-on dependency | Provision hardware YubiKey with direct local credentials for status page | SecOps | 7 days | Open |
| **CAP-03** | No degraded manual fallback for ASIC registry outage | Design assumed 100% vendor uptime | Implement cached-entity fallback with disclaimer banner in UI | Product | 30 days | Open |
