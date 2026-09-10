# Provider seam for a portable external dependency (all agents)

Applies whenever a change adds, or deepens reliance on, an **external third-party service the
product might later swap, bring in-house, or route through a different region** — a
screening/KYC provider, an LLM/inference provider, a voice or media provider, an email provider, a
payments provider. Goal: "bring it home" or switch vendors is a provider swap, never a rewrite.

## Why this exists

This pattern gets applied ad hoc and re-derived each time. Codify it once:

- A screening integration behind a `ScreeningClient` interface so a provider switch is minimal
  code change (an explicit risk-register mitigation in more than one project).
- AI model choice as configuration (`AI_*_MODEL` env vars) with region resolution separate, so the
  model or route changes without touching extraction logic.
- A `VoiceSessionProvider` port with a "two planes, one seam" design so a foreign voice data plane
  can be replaced by a self-hosted in-region stack later without disturbing the control plane,
  scoring, audit or scenarios.

The data-sovereignty screen (`new-vendor-and-model-data-sovereignty-check.md`) says "keep it
portable by construction" in one line; this is that line as a checklist.

## The rules

1. **The application core never imports the vendor SDK.** Core services, models, routers, workers,
   seeds and UI depend on a local `Protocol`/interface and a provider-neutral result schema. The
   vendor SDK is imported only inside its one adapter module.
2. **Provider is selected by server configuration, not a code branch.** A single config value
   picks the adapter. Adding a provider is a new adapter class + a config value, not edits across
   call sites.
3. **A scoped, access-only enablement of a new provider may be built in advance** — a
   feature-flagged adapter that defaults to off, a sandbox key, an IAM grant. Routing real or
   boundary-crossing traffic is the separate dated decision (see the data-sovereignty rule).
4. **Your IP stays in your database, not the vendor's dashboard.** Prompts, scenarios, rubrics,
   routing rules, question sets, scoring logic — versioned in your datastore and pushed to the
   vendor at call time. If it lives only in the vendor console, you cannot migrate it and you do
   not own it.
5. **Split the control plane from the data plane.** The control plane (lifecycle, tenant
   isolation, cost ceiling, audit, retention, scoring/decision logic) is always yours and always
   in your approved region. The data plane (the vendor's actual processing) is what the adapter
   wraps and what a later change may relocate.
6. **Record provider provenance on every affected row** — `provider`, the external reference, and
   the specific vendor/model/region used — so a later cutover is provable and a mixed-provider
   history is auditable.
7. **Normalise the vendor's inbound shape immediately.** Webhooks, callbacks and responses are
   converted to a provider-neutral internal schema at the adapter boundary. Nothing downstream
   sees a raw vendor payload; nothing raw is persisted beyond what a contract requires.
8. **The adapter is the only place vendor-specific error handling lives** — status-code mapping,
   retry/timeout policy, expected-operational-error classification. The core sees bounded, typed
   failures.

## When this does NOT apply

A genuinely single-vendor, commodity, unlikely-to-move dependency where an abstraction is pure
ceremony (the cloud provider's own SDK, the database driver). Judgement call — but "we'll never
switch" is wrong often enough that the default for a compliance-data or AI provider is: build the
seam.

## Related

- `new-vendor-and-model-data-sovereignty-check.md` — the AU-first jurisdiction screen that runs
  before a provider is chosen; this rule is how you build it once chosen.
- `external-api-integration-contract` skill — schema validation, pre-flight checks, audit logging
  and Sentry-noise registration for the adapter itself.
- `data-sovereignty-market-screen` skill — its "architectural implication" step points here.
