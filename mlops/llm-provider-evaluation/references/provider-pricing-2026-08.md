# LLM Provider Pricing Snapshot — verified 2026-08-08

All prices per 1M tokens (USD), verified on official pricing pages this date.

## DeepSeek (current, pre-hike)

| Model | Input (cache miss) | Input (cache hit) | Output | Context |
|-------|-------------------|-------------------|--------|---------|
| deepseek-v4-flash (DeepSeek-V4-Flash-0731) | $0.14 | $0.0028 | $0.28 | 1M |
| deepseek-v4-pro | $0.435 | $0.003625 | $0.87 | 1M |

**⚠️ Official warning (on pricing page):** *"We plan to raise the overall
pricing for DeepSeek API services in the near future, with a significant
increase expected."* No numbers published as of 2026-08-08.

Responses API (OpenAI format, `base_url=https://api.deepseek.com`): currently
**only deepseek-v4-flash**; v4-pro support "early August 2026". Anthropic
format at `https://api.deepseek.com/anthropic`. Concurrency: flash 2500,
pro 500. Max output 384K.

## Z.AI / GLM

| Model | Input | Cached Input | Output | Context |
|-------|-------|-------------|--------|---------|
| GLM-5.2 (newest) | $1.4 | $0.26 | $4.4 | 1M |
| GLM-5.1 | $1.4 | $0.26 | $4.4 | 200K |
| GLM-5 | $1.0 | $0.2 | $3.2 | 200K |
| GLM-5-Turbo | $1.2 | $0.24 | $4.0 | 200K |
| GLM-4.7 | $0.6 | $0.11 | $2.2 | 200K |
| GLM-4.7-FlashX | $0.07 | $0.01 | $0.4 | ~200K |
| GLM-4.7-Flash | FREE | FREE | FREE | ~200K |
| GLM-4.5-Air | $0.2 | $0.03 | $1.1 | — |

## Qwen / Alibaba Cloud Model Studio (DashScope intl)

| Model | Input /1M | Output /1M | Notes |
|-------|-----------|-----------|-------|
| qwen3.8-max (newest flagship) | $2.5 list (50% off limited) | $7.5 list (50% off) | "Comprehensive leap in coding and professional work", 1M ctx |
| qwen3.7-max | $2.5 list (50% off) | $7.5 list (50% off) | Prior flagship, 1M ctx |
| qwen3.7-plus | $0.4 list (20% off) | $1.6 list (20% off) | Agentic coding, 1M ctx; tiers: ≤256K $0.4/$1.6, 256K–1M $1.2/$4.8 |
| qwen3.7-flash | $0.03 (≤32K) / $0.10 (≤256K) / $0.20 (≤1M) | $0.13 / $0.40 / $0.80 | Tiered by ctx, 1M ctx, 50% batch discount |
| qwen3.6-flash | (similar tiers) | — | Prior flash |

Cache: explicit-cache creation billed 125% of standard input; cache hits 10%.
Batch inference: 50% of real-time price (input+output where supported).

## Alibaba Cloud Free Tier (verified on alibabacloud.com/free)

- **70+ million free Model Studio tokens** (text generation — "LLM startups,
  coding tools, reasoning-heavy apps")
- **$90 ECS credits** (3 months)
- 2,000 free images, 1,650 free video seconds
- 80+ products free, up to **12 months**
- Claim: register → verify phone+email → add credit/debit card (**PayPal NOT
  supported**) → claim free tier. One-time per product, first-use condition.
- **Enterprise Free Tier** via Company Real Name Registration — separate from
  Individual Free Tier (can't have both).

## Alibaba Token Plan (Team Edition) — the flat-rate option

- **~$6/mo starting** (Standard seat); Pro/Max tiers for heavier usage
- **Singapore region only** (as of 2026-08-08)
- Credits-based monthly/annual subscription; switch models freely from one pool
- **Includes BOTH Qwen AND DeepSeek** exact-string allowlist: qwen3.7-max
  (limited-time offer), qwen3.7-plus, qwen3.6-plus, qwen3.6-flash,
  qwen-image-2.0, qwen-image-2.0-pro, wan2.7-image, wan2.7-image-pro,
  **deepseek-v4-pro, deepseek-v4-flash, deepseek-v3.2**
- Data privacy: "Conversation data is never used for model training"
- Dedicated throughput, multi-tenant isolation
- ⚠️ Exact-string allowlist — `qwen3-coder-max` NOT included (not on list);
  verify any model before relying on it

## Hermes wiring notes

- Alibaba/Qwen API key provider: `hermes auth add alibaba` →
  `DASHSCOPE_API_KEY` → `model.provider: alibaba` → pick `qwen3.8-max` /
  `qwen3.7-plus` / etc.
- Qwen Portal OAuth: needs `qwen auth qwen-oauth` CLI login first, then
  `hermes auth add qwen-oauth`; base `https://portal.qwen.ai/v1`.
- Codex: add `[model_providers.deepseek]` with `base_url =
  "https://api.deepseek.com"` (bare root for Responses API), `env_key =
  "DEEPSEEK_API_KEY"`, `wire_api = "responses"` for cheap Codex fallback.
- Hermes provider registry lives in `~/.hermes/repo/hermes_cli/auth.py`
  (PROVIDER_REGISTRY / ProviderConfig) — source of truth for provider ids,
  base URLs, env var names.
