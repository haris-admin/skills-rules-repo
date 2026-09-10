# Jurisdiction obligations reference — data sovereignty & regulated markets

Companion to the `data-sovereignty-market-screen` skill. **Australia-first**: AU is the operating
jurisdiction and its obligations are enforced now. Canada / US / EU are "design so we can comply
later" only.

> **Dates move.** This file is a structured checklist, not a live tracker. Confirm any date or
> "in force" claim against `caduceus-compliance-watch` (which holds the maintained key-dates list)
> and the primary source before relying on it. Last reconciled: 2026-09-10.

---

## Australia — the operating jurisdiction

### Data residency / sovereignty
- **Standing rule:** all application data, backups, logs, and infrastructure in AWS
  `ap-southeast-2` (Sydney). No exceptions for "small", "synthetic-looking", or "just a test".
- **"Available in AU" ≠ "processed in AU".** Require a region-specific endpoint / inference
  profile / data-residency commitment confirmed in writing (vendor docs, DPA, AWS region listing).
  Bedrock's own entitlement APIs do not distinguish AU-region from global-only availability.
- Cloud provider account structure and region posture: see `cloud-provider-account-research`.

### Privacy Act 1988 (+ 2024 reforms and expected further tranches)
- **APP 8 — cross-border disclosure:** the discloser stays accountable for an overseas recipient's
  handling; need reasonable steps + a lawful basis. Real personal data leaving AU = a dated
  decision, never an inference.
- **Automated decision-making transparency (APP 1.7 / 1.8):** privacy policies must disclose
  substantially automated decisions that significantly affect individuals. Commencement target
  ~10 December 2026.
- **Statutory tort — serious invasions of privacy:** in force since 2025. Directly relevant to any
  recording, transcription, surveillance, tracking, or monitoring feature.
- **Children's Online Privacy Code:** OAIC-developed, expected ~end 2026. Applies if under-18s can
  realistically use the product.
- **Sensitive information** includes **biometric and voice data**, health, racial/ethnic origin,
  criminal record, sexual orientation, political/religious/union membership. Higher consent bar,
  data-minimisation expectation, generally no secondary use.
- OAIC enforcement powers and penalties materially increased (2022–2024).

### AI-specific (Australia)
- **Voluntary AI Safety Standard** (10 guardrails) — Sept 2024. Treat as the baseline design
  target.
- **Proposed mandatory guardrails for high-risk AI** — government consultation ran 2024; legislation
  expected. Financial crime, identity, safety-relevant, and consequential-decision use cases are
  "high-risk". Design to the voluntary standard now.
- **AS ISO/IEC 42001:2023** — AI management system standard. The Buy Australian AI / Cognisys
  cohort accreditation path.
- **NAIC "Guidance for AI Adoption"** (six essential practices; supersedes the earlier VAISS
  framing, ~21 Oct 2025) — the National AI Centre's practical guidance, referenced by the Buy
  Australian AI Partnership.
- **APP 1.7/1.8 ADM transparency** (above) is the nearest-term hard AI obligation.

### Sector / adjacent (apply only if in scope)
- **AML/CTF Amendment Act 2024 (Tranche 2)** — in force 1 Jul 2026; AML/CTF Rules 2025. Reliance
  (s 37A safe harbour / s 37B assessment), case-by-case (s 38), agency (s 37). A software or
  evidence provider is **never a relied-upon party** and carries no CDD liability. Full mechanics
  in `caduceus-compliance-watch`.
- **APRA CPS 230** (operational risk management, material service providers) — in force 1 Jul 2025.
  Applies indirectly when selling to APRA-regulated entities.
- **ASIC / AFSL** obligations if providing financial product advice or dealing.
- **Consumer Data Right (CDR)** if ingesting accredited banking/energy/non-bank-lending data.
- **AGDIS (Digital ID)** private-sector participation — phased, private sector from ~30 Nov 2026.
- **Security of Critical Infrastructure Act (SOCI)** — if the system is designated critical
  infrastructure or a critical service to one.
- **My Health Records Act / healthcare identifiers** — only if touching health data.

---

## Canada — prepare, do not build for

- **PIPEDA** (federal private sector) + provincial: **Quebec Law 25** (fully in force Sept 2024 —
  ADM transparency, data portability, privacy-by-default, breach reporting), BC PIPA, Alberta PIPA.
- **AIDA** (Artificial Intelligence and Data Act, Bill C-27) — lapsed on prorogation early 2025;
  watch for reintroduction and a possible narrower AI bill.
- **Data residency:** no blanket federal mandate for private sector; federal *government* has
  residency directives; some provinces (BC, NS historically) restrict public-sector personal data
  to Canada.
- **OSFI B-13** (technology and cyber risk) + **E-23** (model risk) for federally regulated
  financial institutions.
- **Design-for note:** an ADM-transparency notice and a Canadian data-region option would cover
  most of this; keep them cheap to add.

## United States — prepare, do not build for

- **No federal privacy law.** State patchwork: **CCPA/CPRA** (California) plus ~20 states with
  comprehensive laws (Virginia, Colorado, Connecticut, Utah, Texas, Oregon, Montana, and more —
  count rising). Common threads: access/deletion/opt-out rights, sensitive-data limits, data-broker
  rules.
- **Sectoral federal:** GLBA + FTC Safeguards Rule (financial), HIPAA (health), COPPA (under-13),
  GLBA/ECOA/FCRA (credit decisions).
- **AI:** no federal statute. **Colorado AI Act** (consequential-decision AI, effective 2026),
  **NYC Local Law 144** (automated employment decision tools), **FTC Act §5** enforcement against
  unfair/deceptive AI, proliferating state deepfake/disclosure laws. **NIST AI RMF** is the
  voluntary reference.
- **Enterprise/gov expectations:** SOC 2 Type II is table stakes; FedRAMP for federal; StateRAMP
  for states.
- **Data residency:** rarely statutory; frequently a contractual/procurement requirement.
- **Design-for note:** SOC 2 controls, a US data-region option, and CCPA-style rights plumbing
  cover the majority.

## European Union / EEA — prepare, do not build for

- **GDPR** + **ePrivacy Directive** (cookies/tracking/electronic comms). Extraterritorial where
  offering goods/services to, or monitoring, EU data subjects.
- **EU AI Act** (Regulation 2024/1689, in force Aug 2024) — extraterritorial. Prohibited practices
  (Feb 2025), GPAI obligations (Aug 2025), **Art 50 transparency** for AI interacting with humans /
  synthetic media (Aug 2026), high-risk obligations staged Aug 2026 → Aug 2027 → Aug 2028. A voice
  agent that talks to people triggers Art 50 disclosure.
- **International transfers:** adequacy decision, SCCs + transfer impact assessment, or BCRs
  (post-Schrems II). AU has **no EU adequacy decision** — transfers AU↔EU need SCCs+TIA.
- **EU Data Act** (in force Sept 2025 — data access/portability, cloud switching, unfair terms),
  **DSA/DMA** (if a platform/gatekeeper), **NIS2** (cybersecurity, if in scope).
- **Data residency:** GDPR does not mandate EU-only storage, but EU-data-boundary offerings are a
  common public-sector and enterprise requirement.
- **Design-for note:** an AI-interaction disclosure, an EU data-region option, an SCC-ready DPA,
  and GDPR rights plumbing cover the baseline.

---

## How to use this in the screen

1. Fill the AU rows for real — they gate the build.
2. For CA/US/EU, write **one line per market** on what would be required and confirm today's
   architecture doesn't foreclose it (region-pinned data plane, swappable providers, ADM/disclosure
   hooks, rights plumbing as a later add).
3. Escalate to a lawyer for: any real cross-border personal-data flow, any high-risk AI decision,
   any new sensitive-data category, any "we think this is probably fine" on a hard gate.
