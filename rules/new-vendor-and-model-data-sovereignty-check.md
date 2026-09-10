# Regulated-market & data-sovereignty screen (all agents)

Applies whenever evaluating, integrating, or requesting access to **any new opportunity, market,
external vendor, or AI model**. It is mandatory before an idea is recommended for build and before
any real client data touches a new provider or crosses a jurisdictional boundary.

This is an AU-first screen: Australia is enforced now; Canada, the United States and the European
Union are designed for and monitored, not built for, unless the opportunity actually enters that
market. It is a product/risk screen, not legal advice. Verify the live primary source and obtain
legal/privacy review before relying on a jurisdiction-specific conclusion.

## Mandatory opportunity output

Every opportunity evaluation must include this matrix. `RAG` is the decision posture, not a claim
that the listed law is the only applicable law.

| Jurisdiction | RAG | Current posture | What must be true before real data touches it |
| --- | --- | --- | --- |
| Australia | 🔴 enforce now | Store/process application data, backups and infrastructure in `ap-southeast-2`; apply the Privacy Act/APPs (including APP 8 cross-border disclosure), applicable AML/CTF obligations and security controls. Privacy Act changes include the statutory tort for serious invasions of privacy; the ADM privacy-policy obligation starts 10 Dec 2026 for covered decisions. The Voluntary AI Safety Standard and Guidance for AI Adoption are voluntary, but useful procurement/governance evidence; ISO/IEC 42001 and NAIC guidance are assurance frameworks, not legislation. | Document the data map, residency/subprocessors, purpose/lawful collection, retention, security and human accountability. Treat voice recordings as personal information; treat biometric voice features/templates used to identify or verify a person as sensitive information until privacy review says otherwise. |
| Canada | 🟡 design for / verify on entry | PIPEDA and provincial rules apply depending on activity; Quebec Law 25 has automated-decision transparency/contestability requirements. AIDA remains a proposed regime, not a present compliance claim. Public-sector and financial-sector residency expectations must be checked per customer/province. | Identify the entity, province, sector and transfer route; perform the applicable privacy/impact assessment and obtain customer/legal approval before collection or processing. |
| United States | 🟡 design for / verify on entry | No single national privacy/AI regime: state privacy laws (including California), sectoral laws such as GLBA/HIPAA where applicable, FTC consumer-protection enforcement and evolving state AI rules all need scoped analysis. SOC 2 is a market assurance expectation, not a law. | Identify states, data categories, sector and consumer-facing decision use; confirm notices, contracts, opt-out/rights, security and any AI-disclosure duties before launch. |
| European Union | 🟡 design for / verify on entry | GDPR, cross-border-transfer mechanisms and the EU AI Act's risk-based obligations apply when scope is triggered; AI Act timing differs by obligation. The EU Data Act may also apply to connected-product/data-access models. | Establish lawful basis, controller/processor roles, transfer mechanism, DPIA/AI-risk classification, human oversight, transparency and deletion/rights processes before EU personal data is processed. |

If an idea does not process data or enter a jurisdiction, write `N/A — no data/market trigger` and
state the assumption. Do not omit the row.

## Hard gates

1. **No real data until green for the relevant market.** A new provider, model, region or market is
   `RED` until the matrix says what data moves, where it moves, why it is permitted and who approved
   it. A concept/prototype using no personal or production data may remain an explicitly bounded
   `AMBER` experiment.
2. **Do not collapse residence, transfer and vendor risk into one question.** Hosting in Australia
   does not itself settle model inference, support access, telemetry, subprocessors, training,
   retention or cross-border disclosure.
3. **Voice is a heightened-data use.** Do not assume a voice product is low-risk because it does not
   store a recording. Analyse transcript, derived features, biometric use, provider logs and human
   escalation separately.
4. **Record status, uncertainty and owner.** Mark each claim `confirmed`, `unconfirmed` or
   `proposed/monitor`; link the primary source; name the human owner for any open gate. Never turn a
   proposed law or voluntary framework into a claimed legal duty.

## Why this exists

CLAUDE.md's data-sovereignty rule ("Always store and process all application data ... in
`ap-southeast-2`") is a single paragraph. It has now had to be applied, and re-derived largely
from scratch, three separate times:

1. **C301 (16 Jul 2026)** — Claude Fable 5 has no `au.`-region Bedrock inference profile. Resolved
   with a scoped, IAM-only exemption ("Override and make it available. I don't want to use it
   until necessary. Mark it as an exemption.") that explicitly did **not** route production
   traffic through it.
2. **C403 (12 Aug 2026)** — evaluating Didit (a KYC vendor) as a second identity-verification
   provider alongside Veriff. Didit's own data-residency terms are unconfirmed in this repo.
3. **C404 (12 Aug 2026)** — evaluating NVIDIA Nemotron for AI document extraction. No `au.`-region
   Bedrock path exists for any Nemotron variant, so any live call almost certainly leaves AU.

C403 and C404 both had to reconstruct the reasoning behind C301's exemption from that one
proposal's prose because nothing generalised it. This doc is that generalisation — read it instead
of re-deriving the pattern from C301 each time.

## The checklist

1. **Ask the residency question before writing any integration code, not after.** What region does
   the vendor/model process and store data in? If the answer isn't confirmed in writing (their
   docs, a signed DPA, an AWS/Bedrock region listing), treat it as **UNCONFIRMED** — never assume
   AU-hosted by default, and never assume non-AU vendors are "probably fine" because the call looks
   small or the data looks synthetic.
2. **Real client data — PII, compliance records, uploaded documents — never goes to an
   UNCONFIRMED or confirmed-non-AU endpoint. No exceptions, no "just this once."** This is the
   floor, not a judgement call.
3. **A scoped, access-only enablement is not itself a sovereignty decision and is fine to set up in
   advance.** Provisioning a sandbox API key, granting IAM `bedrock:InvokeModel` for a new model
   ARN, or standing up a feature-flagged provider class that defaults to off — none of that routes
   real traffic anywhere. C301's precedent: "The grant is IAM-only — the app's
   `AI_DEED_EXTRACTION_MODEL`/`AI_OWNERSHIP_EXTRACTION_MODEL` env vars are not set to it."
4. **Routing real production traffic — or even synthetic/test API calls that still leave the AU
   network boundary — through a non-AU or unconfirmed endpoint needs its own separate, explicit,
   dated human decision.** Never infer it from an earlier adjacent "yes" — "go ahead and evaluate
   Didit" is not the same authorization as "send real client PII to Didit," and "start working on
   Nemotron" is not the same authorization as "make live calls to NVIDIA's API." An agent should
   ask for this explicitly rather than assume synthetic data or small scale makes it moot.
5. **Record the decision where the next reader will actually find it**, once the human has actually
   made it in-session: a "Recorded exemption" note in CLAUDE.md's data-sovereignty section
   (mirroring C301's) if it's a standing capability grant, plus the change's own `proposal.md`. Per
   `docs/agent_rules/no-fabricated-human-decisions.md`, never write the decision down before the
   human has actually made it — an open question stays an open question, flagged for the human, not
   quietly resolved by the agent choosing the convenient reading.
6. **Don't let "the account already looks entitled" substitute for the residency question.** C301's
   own investigation found that Bedrock's self-service entitlement signals (`GetUseCaseForModelAccess`,
   `list-foundation-model-agreement-offers`) don't distinguish AU-region availability from
   global-only availability — an account can be fully "authorized" for a model that still has no
   `au.`-prefixed inference profile. Check for the region-specific profile/endpoint explicitly, not
   just for "does this account have access at all."

## Open cases tracked under this pattern

| Change | Vendor/model | Status |
|---|---|---|
| C301 | Claude Fable 5 (Bedrock, `global.anthropic.claude-fable-5`) | Resolved — IAM-only exemption, no production routing |
| C403 | Didit (KYC/identity verification) | Open — residency unconfirmed, sandbox/synthetic-data-only until resolved |
| C404 | NVIDIA Nemotron (AI extraction eval) | Open — no `au.`-region Bedrock path found, live-call authorization not yet requested |
| C411 | CodeRabbit (PR-review SaaS) | Resolved — not adopted. Rejected on marginal-benefit grounds (this repo's own `/code-review`/`/openspec-verify` already know YourApp-specific rules a generic bot doesn't) before the residency question was ever tested against real code; its SaaS tiers have no confirmed AU-residency commitment on record here, so treat as UNCONFIRMED if reconsidered later. |

Add a row here whenever this pattern applies to a new vendor/model so the next reader doesn't have
to grep OpenSpec history to find every prior instance.
