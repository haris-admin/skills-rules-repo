# Alibaba Cloud Token Plan (Team Edition) — flat-rate lane (verified Aug 2026)

Official doc: https://www.alibabacloud.com/help/en/model-studio/token-plan-overview
(Last updated Jul 01, 2026 — live-verified this session. Purchase/seat-credit
numbers are console-gated; the doc publishes the model allowlist and tier
names but NOT the per-seat token quota.)

## What it is

Monthly AI-model subscription billed in **Credits** (one shared pool across
all models). Covers text + image generation from Qwen, DeepSeek, and others.
Positioned for "popular AI coding tools and agents" — agent use is an
explicit, supported use case. **Singapore region only.**

Key selling points (from the doc):
- Flexible model switching — all usage draws from one Credits pool
- Works with popular AI coding tools and agents
- Team management: assign/reclaim seats, per-member usage tracking
- Predictable costs (monthly or annual subscription)
- **Data security: "Conversation data is never used for model training"** ←
  this is the security-box the user cares about for Qwen
- Dedicated throughput, multi-tenant isolation, no queuing at peak

## Seat tiers

Standard, Pro, Max — a seat is the smallest subscription unit, "a usage quota
for one team member." **One Standard seat (from $6/mo) is enough for the
Hermes agent** — Hermes is effectively one user. Pro/Max = heavier per-seat
quotas. Both Alibaba Cloud accounts and RAM users can subscribe.

⚠️ The doc does NOT publish exact per-seat token/credit numbers — they live on
the purchase page (https://common-buy-intl.alibabacloud.com/token-plan) and in
the console. Verify actual quota before committing.

## Supported models — EXACT allowlist (character-for-character match)

Rules: this is an exact-string allowlist; version/sub-model differences are
NOT supported (e.g. `qwen3-coder-max` → not on list → not supported).

| Brand | Models |
|---|---|
| Qwen | qwen3.7-max (limited-time 50%-off on credits), qwen3.7-plus, qwen3.6-plus, qwen3.6-flash, qwen-image-2.0, qwen-image-2.0-pro |
| Wan | wan2.7-image, wan2.7-image-pro |
| DeepSeek | deepseek-v4-pro, deepseek-v4-flash, deepseek-v3.2 |
| Moonshot AI (Kimi) | kimi-k2.7-code, kimi-k2.6, kimi-k2.5 |
| Zhipu AI (GLM) | glm-5.2, glm-5.1, glm-5 |
| MiniMax | MiniMax-M2.5 |

**Implication for cost strategy:** this single subscription covers BOTH Qwen
AND DeepSeek V4 — so it makes a DeepSeek price hike irrelevant for the
high-volume lane (DeepSeek lives inside the plan). Also includes Kimi/GLM/MiniMax
for experimentation under the same pool.

## Decision fit (from this session)

- **YES for model access:** one Standard seat covers the Hermes agent with
  Qwen + DeepSeek in one flat bill; data-privacy guarantee.
- **NOT for hosting Hermes itself:** Token Plan is inference-only. Hosting the
  Hermes agent runtime is a separate decision (currently WSL at $0/mo; Alibaba
  ECS ~$15–30/mo for a 2vCPU/4GB class; free-trial $90 ECS credits cover ~3 mo).
  Recommendation from session: keep Hermes on WSL; Token Plan is cloud-agnostic
  (works via API key from WSL).
- Use the **free quota first** (per-model 1M tokens, 90 days, Singapore-only)
  to validate before paying — see `references/alibaba-cloud-qwen-access.md`.
