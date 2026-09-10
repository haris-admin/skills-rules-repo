---
name: data-sovereignty-market-screen
description: >-
  Run against EVERY new idea, opportunity, venture, feature, market entry, vendor, or AI model
  before it gets built or before real data touches it. Produces a jurisdiction × obligation
  matrix (data residency + privacy + AI regulation + sector rules) with a RAG status and an
  explicit "what must be true before real data touches this" list. Australia-first: AU
  obligations are enforced now; Canada / US / EU are "design so we can comply later, don't
  build for them yet". Use when Haris proposes a new product/idea, when scoping an OpenSpec
  change that adds an external dependency or a new data flow, when evaluating a grant/accelerator
  fit (ElevenLabs, Buy Australian AI, NVIDIA Inception), or on any "should we build X" question.
  Not a substitute for legal advice and not the live regulatory-date tracker (that is
  caduceus-compliance-watch) — this is the per-opportunity gate that decides go / go-with-controls
  / not-yet.
version: 1.0.0
license: MIT
metadata:
  tags: [compliance, data-sovereignty, privacy, ai-regulation, opportunity-screen, australia, gate]
  related_skills: [caduceus-compliance-watch, ai-governance-framework, au-sovereignty-alignment-audit, pluto-portfolio-ideation, haris-serial-entrepreneur, llm-provider-evaluation, cloud-provider-account-research]
---

# Data Sovereignty & Regulated-Market Screen

Every opportunity is screened against data-sovereignty and regulated-market obligations **before**
it is built and **before** real data touches it. The output is a short matrix + a go decision, not
a research essay.

## When to use

- Haris proposes a new idea / product / venture / pivot ("what if we built…", "should we do…").
- Scoping an OpenSpec change that: adds an external vendor or AI model, opens a new data flow,
  processes a new data category (voice, biometric, health, children), or targets a new user
  segment or country.
- Assessing whether a grant / accelerator / partner program is a fit (does the program's ask
  conflict with our sovereignty posture? — e.g. a US voice-SaaS showcase vs an Australian
  approved-supplier program).
- Any "can we use provider X" / "can we store this in region Y" question.
- Before an idea goes into a build queue, a portfolio register, or an EOI.

Run it again whenever the opportunity materially changes (new region, new data category, new
provider, new model, production instead of synthetic).

## The screen (work top to bottom, stop early if a hard gate fails)

### 1. Classify the data and the actors
- **Data categories touched:** PII · sensitive info (health, biometric, **voice**, racial/ethnic,
  sexual orientation, criminal record, union/political) · financial/transaction · compliance
  records · children's data · credentials/secrets · synthetic/none.
- **Whose data:** real customers · our own staff · partner staff · public/unauthenticated users ·
  nobody (synthetic).
- **Actors that will process it:** our backend · a cloud region · an external SaaS · an LLM/model ·
  a sub-processor chain behind that SaaS.

> A person's **voice is biometric = sensitive information**. "It's only staff, not customers"
> reduces the stakes but does not exit the screen.

### 2. Australia — enforce now (hard gates)
Answer each; any ❌ blocks the build until resolved with a dated human decision.

| Check | Pass condition |
|---|---|
| **Processing & storage region** | All processing and storage in `ap-southeast-2` (Sydney). A non-AU or **unconfirmed** region for real data = ❌. "Available in AU" is not evidence — need the region-specific endpoint/profile confirmed in writing. |
| **Cross-border disclosure (APP 8)** | If any real personal data leaves AU, there is an accountable, documented basis and a dated human decision — not inferred from an adjacent "yes". Synthetic/test calls that still leave the AU network boundary need their **own** dated decision. |
| **New vendor / model** | `new-vendor-and-model-data-sovereignty-check` run; residency confirmed or scoped to synthetic-only + flagged. |
| **AI decision boundary** | No AI output auto-files / approves / declines / screens / concludes a regulated matter. Human + deterministic control in front of anything legally material (`ai-governance-framework`). |
| **Sensitive data** | Voice/biometric/health/children's data: explicit consent + notice, minimised retention, and a documented lawful basis before collection. |
| **Retention** | 7-year retention obligations (AML/CTF, compliance records) identified and separated from ephemeral data. Retaining a *secret* 7 years is a regression, not compliance — the rule increases what you keep a *record* of, not how long you keep a *credential*. |

### 3. Australia — imminent obligations to design for (not optional, dates move — confirm against `caduceus-compliance-watch`)
- **Automated decision-making transparency** (Privacy Act APP 1.7/1.8) — privacy policy must
  disclose ADM that significantly affects individuals. Target ~10 Dec 2026.
- **Statutory tort for serious invasions of privacy** — already in force; surveillance/recording
  features carry real liability.
- **Children's Online Privacy Code** — if under-18s can plausibly use it.
- **Proposed mandatory guardrails for high-risk AI** — if the use case is high-risk (financial
  crime, identity, safety), design to the 10 voluntary guardrails / AS ISO/IEC 42001 / NAIC
  "Guidance for AI Adoption" now so the mandatory version is a formality.
- **AGDIS / Digital ID** private-sector onboarding (from 30 Nov 2026) if doing identity.
- **APRA CPS 230** operational-risk / material-service-provider obligations if selling to a
  regulated financial entity.
- **AML/CTF Tranche 2** (in force 1 Jul 2026) — reliance ≠ outsourcing ≠ agency; a software/
  evidence provider is never a relied-upon party and carries no CDD liability (see
  `caduceus-compliance-watch` for the s 37A/37B/38 mechanics).

### 4. Canada / US / EU — prepare, don't build for (yet)
Record, in one line each, what *would* be required so today's architecture doesn't foreclose it.
Do **not** add controls for these now unless a named opportunity requires it.

- **Canada:** PIPEDA + Quebec Law 25 (ADM transparency, portability); AIDA (Bill C-27) — watch for
  reintroduction; OSFI B-13 if selling to Canadian FRFIs; federal/provincial residency
  expectations for public sector.
- **US:** no federal privacy law — state patchwork (CCPA/CPRA + ~20 states); sectoral GLBA / HIPAA
  / COPPA; Colorado AI Act + NYC LL144 + FTC §5; NIST AI RMF; SOC 2 / FedRAMP for enterprise/gov;
  residency usually contractual not statutory.
- **EU:** GDPR + ePrivacy; **EU AI Act** (extraterritorial — Art 50 transparency live Aug 2026,
  high-risk staged to 2027/2028, GPAI obligations live); international-transfer basis (adequacy /
  SCCs / TIA post-Schrems II); EU Data Act; NIS2 if in scope.

**Architectural implication (do this now, cheaply):** keep the data plane swappable and
region-pinned; keep provider adapters behind a port; keep an explicit `region` / `provider` /
`data_category` field on records; never hard-wire a foreign SaaS into the core. See the HiveCoach
two-planes pattern (`openspec/changes/496-*/CLAUDE_FEEDBACK.md` in the AMLHive repo) as the worked
example.

### 5. Program / grant conflict check
If the opportunity is tied to a grant or accelerator, name the conflict explicitly:
- Does the program reward something that weakens our sovereignty posture (e.g. "show deep use of
  our US voice API" vs "be an Australian approved supplier")?
- Resolve with **componentised delivery** — one codebase, a swappable part per program — never a
  fork. State which component each program sees.

## Output format (paste this back, keep it short)

```
## Data-sovereignty & regulated-market screen — <opportunity> (<date>)

Data: <categories> · whose: <subjects> · actors: <processors/regions/providers>

| Jurisdiction | Obligation | Status | Note |
|---|---|---|---|
| AU | ap-southeast-2 processing | 🟢/🟠/🔴 | ... |
| AU | APP 8 cross-border | ... | ... |
| AU | AI decision boundary | ... | ... |
| AU | sensitive-data consent/retention | ... | ... |
| AU (imminent) | ADM transparency / high-risk AI guardrails | ... | ... |
| CA/US/EU | design-for note | ⚪ prepare | one line each |

**Verdict:** GO / GO WITH CONTROLS (<list>) / NOT YET (<blocking gate + what unblocks it>)
**Human decisions needed:** <named, or "none">
**Architecture note:** <what to keep swappable / region-pinned so this stays portable>
```

## Best practices

- **Ambiguity resolves to the stricter reading.** If you're building an argument for why something
  probably doesn't need a control, you've already established it's ambiguous — apply the control or
  ask.
- **A scoped, access-only enablement is fine in advance** (sandbox key, IAM grant, feature-flagged
  provider defaulting to off). Routing *real or boundary-crossing traffic* is the decision that
  needs a dated human sign-off.
- **This screen decides go/no-go for one opportunity.** Keeping shipped solutions aligned over time
  as regulations change is `au-sovereignty-alignment-audit`. Tracking the live regulatory dates is
  `caduceus-compliance-watch`. Don't merge the three.
- Not legal advice. High-risk / novel data flows still go to a lawyer — this screen tells you
  *when* you need one.
