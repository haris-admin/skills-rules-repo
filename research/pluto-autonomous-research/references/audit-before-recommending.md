# Audit Before Recommending — Pitfall Case Studies

Full incident detail behind the Phase 0e "audit before recommending a
tool/service" checklist in `SKILL.md`. Read this when you need the concrete
examples of what happens when the checklist is skipped.

## Pitfall — defaulting to "buy new" when the user already has everything

In July 2026 this user had Gemini Advanced (Veo 3.1 video gen + Imagen 3 images), ChatGPT Plus (Sora video + GPT-5.5 scripting + TTS), ChatGPT Team (more Sora), and ElevenLabs credits (voice). A first-pass recommendation of BytePlus (which would need a new paid subscription, sales call, and China data compliance review) was wrong — the correct answer was "you already have Veo 3.1 in Gemini Advanced, try that first."

## Pitfall — forgetting existing infrastructure

After fixing the tool recommendation, the user also had Cloudflare (DNS, R2, Workers), AWS SES, and Vercel already provisioned. A click tracker that runs on Cloudflare Workers ($0 extra, uses existing infra) is better than any third-party tracking SaaS that needs a new account and billing arrangement.

## Related implementation references

- `references/cloudflare-click-tracker-pattern.md` documents the implementation that resulted from this audit-first protocol — a Cloudflare Worker click tracker with KV logging, UTM enrichment, rate limiting, and a frontend tracking component.
- `references/crm-integration-pattern.md` documents the AU real estate CRM research for AML Hive API integration opportunities — top 10 CRMs, competitive threats (Reapit AML/CTF built-in), and integration priority scoring.
