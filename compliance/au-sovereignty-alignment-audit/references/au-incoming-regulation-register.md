# Australian incoming-regulation register

The checklist the `au-sovereignty-alignment-audit` skill runs shipped solutions against. Ordered
roughly by nearness / impact. **Confirm every date against `caduceus-compliance-watch` and the
primary source before acting** — this is a working register, not the source of truth for dates.

Last reconciled: 2026-09-10.

| # | Obligation | Commences | Applies to us if… | What alignment looks like |
|---|---|---|---|---|
| 1 | **Data residency — `ap-southeast-2`** | in force (standing) | always | 100% of real-data processing, storage, backups, logs, infra in Sydney. Zero unconfirmed/non-AU routes for real data. |
| 2 | **AML/CTF Tranche 2** (Amendment Act 2024, Rules 2025) | 1 Jul 2026 | selling to / enabling reporting entities | product is an evidence/provenance/audit pipe; never a relied-upon party; carries no CDD liability; copy makes no compliance guarantee |
| 3 | **APRA CPS 230** (operational risk, material service providers) | 1 Jul 2025 | a customer is APRA-regulated | able to answer material-service-provider due diligence; documented resilience, incident, and exit provisions |
| 4 | **Statutory tort — serious invasions of privacy** | in force (2025) | any recording / transcription / monitoring / tracking feature | consent + notice, minimised capture, no covert collection, defensible purpose |
| 5 | **Privacy Act — ADM transparency (APP 1.7/1.8)** | ~10 Dec 2026 | any substantially automated decision that significantly affects a person | privacy policy discloses ADM; internal register of ADM points; human-review path documented |
| 6 | **AGDIS / Digital ID — private sector** | phased; private sector ~30 Nov 2026 | doing identity verification / relying on Digital ID | accreditation path understood; not claiming AGDIS participation prematurely |
| 7 | **Proposed mandatory guardrails for high-risk AI** | expected (consultation done 2024) | high-risk use (financial crime, identity, safety, consequential decisions) | designed to the 10 voluntary guardrails now; testing/eval evidence; human oversight; kill switch; documentation |
| 8 | **AS ISO/IEC 42001 + NAIC "Guidance for AI Adoption"** | current (voluntary / cohort) | pursuing Buy Australian AI / approved-supplier status | AI management system practices in place; gap assessment done; cert plan if cohort offers it |
| 9 | **Children's Online Privacy Code** | ~end 2026 | under-18s can realistically use the product | age assurance considered; default-private for minors; no behavioural targeting of minors |
| 10 | **Consumer Data Right (CDR)** | in force, sectors expanding | ingesting accredited banking/energy/lending data | accreditation or representative/outsourced model; CDR data segregation |
| 11 | **Security of Critical Infrastructure (SOCI)** | in force | system designated critical infrastructure or critical service to one | risk management program, incident reporting readiness |
| 12 | **OAIC enforcement posture + expected further Privacy Act tranches** | ongoing | always (PII) | breach response plan; data minimisation; APP compliance reviewed; watch for "fair and reasonable" test, direct right of action, small-business exemption removal |
| 13 | **EU AI Act Art 50 (AI-interaction disclosure)** | 2 Aug 2026 | any EU user can interact with an AI feature (extraterritorial) | AI clearly discloses it is AI; synthetic media marked — build the disclosure even if EU is "prepare only", it is cheap and also good AU practice |

## Cross-market "prepare, don't build" one-liners (do not action without a named opportunity)

- **Canada:** ADM-transparency notice (Quebec Law 25) + a Canadian data-region option would cover
  most near-term need; watch AIDA reintroduction.
- **US:** SOC 2 Type II + a US data-region option + CCPA-style access/deletion/opt-out plumbing.
- **EU:** #13 above + an EU data-region option + SCC-ready DPA + GDPR rights plumbing.

## Maintenance

- Add a row whenever `caduceus-compliance-watch`, a Gmail briefing, or a news monitor surfaces a
  new AU obligation with a commencement date.
- When an obligation fully commences and we are confirmed aligned, keep the row (change "Commences"
  to "in force") — do not delete; the audit still checks it for regression.
- Keep this in sync with `caduceus-compliance-watch`'s "Key dates" block — that skill owns the
  authoritative dates; this register owns the "does it apply / what does aligned look like" mapping.
