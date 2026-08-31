---
name: llm-provider-evaluation
description: "Pick LLM providers for Hermes: pricing, access, free tiers, hosted inference providers (DeepInfra/SiliconFlow/Novita/Together), Qwen/QAN ecosystem status, DeepSeek hike hedging, provider wiring."
version: 1.0.0
author: Pluto
license: MIT
category: mlops
platforms: [linux, macos, wsl]
metadata:
  hermes:
    tags: [llm, provider, pricing, deepseek, glm, qwen, dashscope, hermes-config, cost-routing]
    related_skills: [hermes-agent, pluto-autonomous-research, reference-data-ingestion]
---

# LLM Provider Evaluation (Hermes Agent Stack)

## When to Use

- User asks "which model/provider should we use?" or "is X still the best option?"
- User asks how to get access to a provider **without OpenRouter** (direct API, OAuth, cloud marketplace)
- A provider announces a **price increase / policy change** and the current choice needs re-validating
- Wiring a new provider into Hermes (`config.yaml`, `.env`, `hermes auth`, Codex `config.toml`)
- Building the cost-routing fallback chain (`or_free.py` 3-phase pattern: free → cheap → paid)

## Core Method (verified 2026-08-08)

1. **Check the provider's OWN pricing page first** (authoritative):
   - DeepSeek: `https://api-docs.deepseek.com/quick_start/pricing` (curl-able, no JS)
   - Z.AI/GLM: `https://docs.z.ai/guides/overview/pricing` (curl-able)
   - Qwen/Alibaba: `https://www.alibabacloud.com/help/en/model-studio/model-pricing` (JS-heavy — use browser or grep the saved snapshot)
2. **OpenRouter `/api/v1/models`** for a cross-provider snapshot (pricing may show $0 during promos — always cross-check with the provider page)
3. **Check free tiers/credits** — many providers give startup/trial credits that change the cost calculus for a small agent fleet
4. **Check Hermes native provider support** before proposing a custom endpoint — the provider may already be built in:
   - `~/.hermes/repo/hermes_cli/auth.py` has the `PROVIDER_REGISTRY` (ProviderConfig with `id`, `inference_base_url`, `api_key_env_vars`)
   - Providers seen: `deepseek`, `zai`/GLM, `alibaba` (DashScope), `alibaba-coding-plan`, `qwen-oauth`, `minimax`, `minimax-cn`, `kimi-coding`, `kimi-coding-cn`, `xai`, `anthropic`, `openrouter`, `bedrock`, `nvidia`, `opencode-zen`, `opencode-go`
   - Config: `hermes config set model.provider <id>`; secrets in `~/.hermes/.env`; OAuth flows via `hermes auth add <provider>`

## Provider Wiring Quick Reference (Hermes)

| Provider | Hermes id | Auth | Env var / flow | Base URL |
|----------|-----------|------|----------------|----------|
| DeepSeek | `deepseek` | API key | `DEEPSEEK_API_KEY` | `https://api.deepseek.com/v1` |
| Z.AI / GLM | `zai` | API key | `GLM_API_KEY` | (see auth.py) |
| Qwen Cloud | `alibaba` | API key | `DASHSCOPE_API_KEY` | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| Alibaba Coding Plan | `alibaba-coding-plan` | API key | `ALIBABA_CODING_PLAN_API_KEY` | `https://coding-intl.dashscope.aliyuncs.com/v1` |
| Qwen Portal | `qwen-oauth` | OAuth | `hermes auth add qwen-oauth` (needs `qwen auth qwen-oauth` CLI login) | `https://portal.qwen.ai/v1` |
| MiniMax | `minimax` | API key | `MINIMAX_API_KEY` | (see auth.py) |

Codex provider blocks live in `~/.codex/config.toml` (`[model_providers.<name>]` with `base_url`, `env_key`, `wire_api`). DeepSeek Responses API base_url is the bare `https://api.deepseek.com` (no `/v1`) — see `references/provider-pricing-2026-08.md`.

## Hosted inference providers (surveyed 2026-08-09)

Beyond first-party APIs (DeepSeek direct, Z.AI, Alibaba/DashScope), third-party
inference hosts serve the same Chinese models — sometimes cheaper than the
vendor's own API. Full table + free-tier survey:
`references/hosted-provider-survey-2026-08.md`. Headlines:

- **DeepInfra = best value for the Hermes agent**: DeepSeek V4-Flash
  **$0.09/$0.18** (35% below direct DeepSeek — the price-hike hedge), GLM-5.2
  1M-ctx **$0.75/$2.40** (half Z.AI list), SOC2/ISO27001, US signup, open.
- **Novita AI** = broadest single-vendor Chinese-model catalog.
- **SiliconFlow intl** = cheapest Qwen open lane ($0.07/$0.28) + official
  Hermes integration guide; $1 free credit.
- **Groq/Cerebras avoid** — preview/legacy only; Cerebras GLM-4.7 deprecates
  **Aug 17 2026**.
- **Qwen Portal (portal.qwen.ai) is DEAD** (discontinued 2026-04-15) — the
  `qwen-oauth` Hermes path will not work. Live Qwen API options today:
  DashScope key, Alibaba Coding Plan/Token Plan, Qoder (credit-based), or
  ModelScope (China-hosted, unpublished pricing).

## Doubao / Volcengine Ark (surveyed 2026-08-09)

ByteDance's Doubao/Seed models via Volcengine Ark. **Not directly usable
from Australia**: live console signup hard-codes a +86 Chinese phone (both
tabs), payment is RMB, and free-quota exhaustion requires CN real-name
verification. `volces.com` / `volcanoengine.com` are NXDOMAIN globally —
`volcengine.com` is the only live site and it's CN-only; `doubao.com` is
the consumer chat app, not an API. OpenAI-compatible endpoint (verified
live, 401 without key): `https://ark.cn-beijing.volces.com/api/v3`
(~1.0s TTFB from AU). If Doubao is required, third-party hosts are the
only realistic lane. Full lineup, RMB pricing, free-quota rules, and the
docs-scraping recipe: `references/volcengine-ark-doubao-2026-08.md`.

## Decision Rules (learned 2026-08-08)

- **DeepSeek announced "significant" price increase "in the near future"** (official pricing page). Current rates are flash $0.14/$0.28, pro $0.435/$0.87 per 1M. Treat DeepSeek as non-guaranteed-pricing; have a fallback ready.
- **Even a 2–3x DeepSeek hike likely keeps it cheapest** vs GLM-5/5.2 flagships. Only if flash triples (~$0.42/$0.84) do GLM-4.7-FlashX ($0.07/$0.40) or Qwen3.7-flash (~$0.03–0.20/$0.13–0.80) become meaningfully better for high-volume cron work.
- **Qwen direct access without OpenRouter:** Alibaba Cloud Model Studio (DashScope) API key, Qwen Portal OAuth, or Alibaba Coding Plan. All three are Hermes-native.
- **Alibaba free trial:** 70M+ free Model Studio tokens + $90 ECS credits; Enterprise Free Tier via Company Real Name Registration (good for a registered AU company). PayPal NOT supported — credit/debit card needed.
- **Alibaba Token Plan (Team Edition, ~$6/mo start, Singapore region):** flat-rate Credits pool covering **both Qwen AND DeepSeek models** (qwen3.7-max/plus/flash, deepseek-v4-pro/flash, qwen-image-2.0, wan2.7). Data-privacy guarantee ("conversation data never used for training"). This makes a DeepSeek price hike irrelevant if adopted.
- **Check exact model availability per plan:** Token Plan uses an exact-string allowlist (e.g. `qwen3.7-max`, NOT `qwen3-coder-max`). Verify before assuming a model is included.
- **Qwen3.8-max is the newest flagship** ("comprehensive leap in coding and professional work"), list $2.5/$7.5 per 1M with limited-time 50% off. qwen3.7-plus is the agentic-coding value tier (~$0.4/$1.6 list, 20% off).

## Pitfalls

- **OpenRouter pricing can show $0.0000 during promos** — never conclude "free" from OpenRouter alone; verify on the provider's page.
- **DeepSeek Responses API supports only `deepseek-v4-flash` today** — `deepseek-v4-pro` lands "early August 2026". Streaming has no `data: [DONE]`; ends with `response.completed/incomplete/failed`.
- **`temperature`/`top_p` have no effect in thinking mode** — don't tune them expecting behavior change on thinking models.
- **Alibaba docs pages are JS-heavy** — `curl` returns nav shell; use `browser_navigate` + grep the saved snapshot file for pricing cells.
- **Don't commit to a provider based on list price alone** — always check limited-time discounts (Qwen 50%/20% off), batch-inference discounts (50%), and context-cache discounts (10% hits).
- **Chinese-first platforms (Volcengine Ark, ModelScope) are CN-phone/RMB-gated** — verify the live signup form's country-code field before promising access; free tiers there still require CN real-name verification to keep using.
- **A live-looking API hostname is not proof of an operational service** — `ark.ap-southeast-1.volces.com` resolves (Singapore ALB) but the API times out; probe with a dummy POST (401 JSON = live, timeout = dead). Verify intl brand domains via public DoH before treating them as real (volces.com is NXDOMAIN globally).
- **Hermes model config is at `model.default` / `model.provider` in `~/.hermes/config.yaml`** — provider swaps are config-only, no code change.

## Support Files

- `references/provider-pricing-2026-08.md` — full pricing snapshot (DeepSeek, GLM, Qwen, Alibaba plans) with verification dates
