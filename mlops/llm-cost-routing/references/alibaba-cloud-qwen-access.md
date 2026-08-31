# Alibaba Cloud Qwen Access — Account Types, Free Tiers & Entity Strategy (verified Aug 2026)

Research captured 2026-08-09 from live Alibaba Cloud pages (account signup form,
`/free` T&C, Model Studio billing docs, AI Catalyst startup program). All URLs
live-verified; docs restructured Aug 2026 (old `/help/en/account/real-name-verification*`
URLs now 404 — canonical paths below).

## Account types — the ONLY two options

Signup (`https://account.alibabacloud.com/register/intl_register.htm`) asks:
**Enterprise Account or Individual Account**. Both proceed with email+password;
no ABN/ACN at signup.

| Aspect | Individual | Enterprise |
|--------|-----------|------------|
| Official definition | "solo developers, students, startup teams, or personal projects" | "any company or organization" |
| Verification doc (AU) | **Passport OR Driver's Licence only** | Valid business registration doc + company name/reg-no/state/address |
| Review time | ~3 business days, manual | ~3 business days, manual |
| Lock-in | Type locked; **can upgrade to enterprise, never revert** | Type locked |
| Extra rights | Only mainland-China purchases | Online contracts, credit limits, ACPN, cross-country phone binding |

Sources: `alibabacloud.com/help/en/account/what-is-an-alibaba-cloud-account`,
`/help/en/account/account-verification-overview`,
`/help/en/account/verify-your-identity-individual-account/`,
`/help/en/account/verify-your-identity-enterprise-account/`.

**Key nuance: identity verification is OPTIONAL on the international site** for
basic use. Only needed for: mainland-China services, online contracts, credit
limits, ACPN, cross-country phone binding, or going pay-as-you-go past the free
quota.

## Sole-trader ABN (Proprietary) — does it work?

**YES for an Individual account.** harishabib.au-style Proprietary ABNs sign up
as Individual, verify with passport/driver licence, and get the standard free
tier. No company needed.

**Enterprise verification with a sole-trader ABN is LIKELY but UNVERIFIED** —
docs require a "valid business certificate issued by local government"; AU sole
trader ABN acceptance is case-by-case manual review. A Pty Ltd (AMLHive) is the
safe enterprise submission. If the user wants Enterprise tier + startup program,
use the company entity.

## Free tiers (what you actually get)

### 1. Model Studio free quota (per-model, not one big pool)
Source: `alibabacloud.com/help/en/model-studio/new-free-quota` (updated Jun 23 2026)
- Per-model quotas (e.g. 1M tokens for qwen-max; similar per Qwen 3.7/3.8 family)
- "70M+ free AI tokens" headline = across MANY models
- **Singapore region ONLY** (also the AU default: ap-southeast-1) ✅
- Valid **30–90 days** from activation (90 days for new activations since Sep 8 2026)
- Covers real-time inference only — NOT batch, fine-tuning, or deployment
- Account + RAM users share ONE quota
- After quota: service STOPS (`AllocationQuota.FreeTierOnly`) unless you complete
  account info (profile + payment method). Enable "Free Quota Only" to avoid surprise bills.
- No identity verification needed to activate

### 2. Free Trial campaign (`alibabacloud.com/free`)
- Model Studio "70+ Million Tokens Free", ECS $90 credits (3 months), 2,000 free
  images, 1,650 free video seconds, 80+ products up to 12 months
- **Card required to claim** (credit/debit; PayPal NOT supported; $1 pre-auth
  appears as ALIBABACLOUD.COM; no prepaid/virtual cards)
- One-time per product, one account per user/organization (multi-account farming
  = disqualification)
- **Enterprise Free Tier exclusives** require Company Real Name Registration —
  individual free tier users NOT eligible for enterprise free tier

## AI Catalyst startup program (the big prize)
`alibabacloud.com/en/startup/ai`
- Up to **2B free Model Studio tokens**, up to $120K cloud credits, POC coupons,
  1:1 AI expert office hours, 12 months Academy
- **Requires a COMPANY**: unlisted, founded ≤10 yrs, accessible website, solid
  proposal; approval at Alibaba's discretion
- Sole-trader ABN likely does NOT qualify
- Process: survey → review → email in 4–5 business days
- ⚠️ **Firewall note:** T&C grants Alibaba a license to list "your name, website,
  and other general contact information" in a public program directory. If that
  matters, apply as the COMPANY (AMLHive), never the personal brand.
  Program period was Apr 1 2025 – Mar 31 2026 (verify extension).

## Australian gotchas
- Contracting entity: **Alibaba Cloud (Singapore) Private Limited**, billed USD
  → AU card FX fees
- One bank card binds to only ONE Alibaba account
- Only ONE account per person may claim free-tier
- Verification result email can land in spam (docs warn)
- Name/ID must match document EXACTLY (punctuation included)
- Region defaults to Singapore — the only free-quota region
- Same person CAN hold individual + enterprise accounts (6 accounts per phone);
  but free-tier is one-per-person and cards can't be shared

## Token Plan (Team Edition) — the $6/mo flat-rate option
Source: `alibabacloud.com/help/en/model-studio/token-plan-overview` (Jul 01 2026)
- **Monthly Credits-based subscription**; three seat tiers — Standard (from **$6/mo**), Pro, Max
- A **seat = one user quota**; for the Hermes agent one Standard seat is enough (it's one consumer)
- **Credits pool**: all usage draws from one pool — switch models freely within the allowlist
- **Supported models (exact-string allowlist, no version inference):** qwen3.7-max/plus, qwen3.6-plus/flash, qwen-image-2.0(+pro), wan2.7-image(+pro), **deepseek-v4-pro / v4-flash / v3.2**, kimi-k2.7/2.6/2.5, glm-5.2/5.1/5, MiniMax-M2.5
- **Why it matters for the DeepSeek hike:** deepseek-v4-pro + v4-flash are INSIDE the plan — a flat monthly bill makes the pending DeepSeek price increase irrelevant
- **Data security:** "Conversation data is never used for model training" — the secure-use box ticked
- **Broad tool compatibility:** works with popular AI coding tools and agents (Hermes-compatible); dedicated throughput, multi-tenant isolation, no queuing
- **Singapore region ONLY** (fine for AU)
- ⚠️ Exact per-seat token/credit allocation is **not published in docs** — console-gated (purchase page `common-buy-intl.alibabacloud.com/token-plan`); check there before committing
- Related: **AI Savings Plan** (prepaid, up to 47% off pay-as-you-go) once monthly volume is known

## Model access ≠ hosting: Token Plan vs ECS
The Token Plan is **model inference only** — it does NOT host the Hermes agent.
- **ECS** (their EC2) is the hosting layer: small instance (2 vCPU/4GB, e.g. `ecs.g6.large` class) runs Hermes (Python CLI + cron) fine, roughly **$15–30/mo** pay-as-you-go in Singapore (ap-southeast-1); the $90 free ECS credits cover ~3 months of a small box
- **Honest comparison (used 2026-08-09):** Hermes already runs on WSL at **$0/mo**, and AMLHive's stack is on **AWS** — adding Alibaba ECS is a second cloud for marginal benefit. Recommended: keep Hermes on WSL, buy the Token Plan for model access (cloud-agnostic — works from WSL via API key). Revisit ECS only if you want Qwen-native infra or outgrow WSL.
- Free tier mechanics (per-model quota, Singapore-only, 30–90 days) — see below.

## Recommended strategy (used 2026-08-09)
1. **Phase 1:** Sign up Individual (harishabib identity) → activate Model Studio
   Singapore → use 90-day per-model quotas to test qwen3.7-flash/plus via Hermes
   `alibaba` provider. No verification, no company needed to start.
2. **Phase 2 (if Qwen proves out):** Apply AI Catalyst with AMLHive (separate
   enterprise account, separate email/card) for up to 2B tokens.
3. Firewall preserved: Individual and Enterprise accounts are never linked by
   Alibaba.

## Hermes wiring (provider config, from hermes_cli/auth.py)
| Provider | Env var | Base URL |
|----------|---------|----------|
| `alibaba` ("Qwen Cloud") | `DASHSCOPE_API_KEY` | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| `alibaba-coding-plan` | `ALIBABA_CODING_PLAN_API_KEY` (fallback `DASHSCOPE_API_KEY`) | `https://coding-intl.dashscope.aliyuncs.com/v1` |
| `qwen-oauth` | OAuth (Qwen CLI) | `https://portal.qwen.ai/v1` — **DEAD since 2026-04-15**, see below |

Setup: `hermes auth add alibaba` → paste key → `hermes model` → `qwen3.8-max` /
`qwen3.7-plus` / `qwen3.7-flash`.

## ⚠️ Qwen Portal is DEAD (2026-04-15)
- `portal.qwen.ai` all paths 404; qwen.ai is consumer-only (Qwen Studio chat)
- Qwen CLI `/auth` menu: Alibaba ModelStudio (Coding Plan / Token Plan / Standard
  key), third-party keys (DeepSeek, MiniMax, Z.AI, ModelScope), or custom provider
- **Do not recommend qwen-oauth as the primary path** — needs a working Qwen CLI
  login that no longer exists; DashScope API key is the reliable path
