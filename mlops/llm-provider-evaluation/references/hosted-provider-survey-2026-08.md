# Hosted Inference Providers for Chinese Models — Survey (2026-08-09)

Live pricing verified 2026-08-09 by 3 parallel research agents (curl + browser
snapshots of provider pricing pages). All prices per 1M tokens, USD,
cache-miss input unless noted. All OpenAI-compatible unless noted.

## Comparison table

| Provider | DeepSeek V4-Flash | GLM-4.7-Flash | GLM-5.2 | Qwen3.8-Max | Qwen3.7-Plus | Notes |
|----------|-------------------|---------------|---------|-------------|--------------|-------|
| **DeepInfra** | **$0.09/$0.18** ← cheapest | $0.06/$0.40 | **$0.75/$2.40** (1M ctx) | $1.65/$4.95 (256K) | — | SOC2/ISO27001, US signup, open, no free credits, 1M ctx on V4 |
| **Novita AI** | $0.14/$0.28 | $0.07/$0.40 | $1.40/$4.40 | $2.00/$6.00 (977K) | — | Broadest catalog (all 3 families in one endpoint), US company |
| **SiliconFlow intl** | $0.13/$0.28 | — | $1.30/$4.09 | (Qwen3.6 only) | — | $1 free credit, Google/GitHub login, official Hermes Agent guide, no Chinese phone |
| **Together AI** | $0.14/$0.28 | — | $1.40/$4.40 | — | **$0.32/$1.28** ← only host | cheapest V4-Pro ($1.74/$3.48) |
| Groq | — | — | — | — | — | only Qwen3.6-27B preview $0.60/$3.00 |
| Cerebras | — | — | — | — | — | GLM-4.7 preview $2.25/$2.75, **deprecating Aug 17 2026** |
| Fireworks | V3 legacy | — | — | — | — | $1 free credits, Qwen3-8B $0.10 |
| Hyperbolic | — | — | — | — | — | pricing app-only (site moved to hyperbolic.ai); no public per-token prices |
| Lambda / Modal / Baseten | — | — | — | — | — | GPU-rental platforms; no hosted per-token pricing for these models |

## Best value for the Hermes agent (high tool-call volume, cron jobs)

1. **DeepInfra — clear #1.** DeepSeek V4-Flash $0.09/$0.18 is ~35% below the
   direct DeepSeek API price ($0.14/$0.28) — the best hedge against DeepSeek's
   announced hike. GLM-5.2 at $0.75/$2.40 with 1M ctx is half the official
   Z.AI price. SOC 2 + ISO 27001 certified, US payment, open signup, no
   approval. Flex service tier = 0.8× price.
2. **Novita AI — #2.** Broadest single-vendor Chinese-model coverage
   (Qwen3.8/3.7-Max, GLM-5.2, DeepSeek V4 all present), near-direct prices.
3. **SiliconFlow intl — #3.** Cheapest Qwen open lane (Qwen3-14B / Coder-30B
   at $0.07/$0.28), Google/GitHub login, $1 free credit, official Hermes
   integration guide in their docs. Watch: $1 credit is tiny vs a real test
   budget.
4. **Together AI** — pick for Qwen3.7-Plus or cheapest V4-Pro.

**Avoid for this workload:** Groq/Cerebras (preview/legacy only, Cerebras
GLM-4.7 deprecates Aug 17 2026), Hyperbolic/Lambda/Modal/Baseten (no
comparable hosted per-token pricing).

## Free tiers & trial credits (2026-08-09)

| Provider | Free tier |
|----------|-----------|
| Alibaba Model Studio | **70M+ free tokens** + $90 ECS credits (up to 12 months; card required, no PayPal) |
| Z.AI (GLM) | **GLM-4.7-Flash = 100% free** (unlimited free tier model) |
| Qoder (Qwen agent) | Free $0 plan + 2-wk Pro trial (300 credits); Qwen3.8-Max promo 800 free calls (until Sep 3 2026); BYOK allowed |
| Cerebras | $5 free credits; Developer tier from $10 |
| SiliconFlow intl | $1 free credit |
| Fireworks | $1 free credits |
| Modal | $30/month compute credit (not token-based) |
| DeepInfra | ❌ none — needs card/prepay (but cheapest ongoing) |
| Hyperbolic | ~$10 historical, unverified (site moved) |

## Qwen (QAN) ecosystem status — verified Aug 2026

- **Qwen Portal / portal.qwen.ai is DEAD** — discontinued 2026-04-15; every
  path 404s. qwen.ai is consumer-only (Qwen Studio chat at chat.qwen.ai). The
  old `qwen-oauth` Hermes provider path will NOT work.
- **Qwen Code CLI** (`qwen`, then `/auth`) now offers: Alibaba ModelStudio
  (Coding Plan / Token Plan / Standard API key), third-party keys (DeepSeek,
  MiniMax, Z.AI, ModelScope, OpenRouter), or custom provider. Qwen OAuth
  option removed. Headless/CI: use Coding Plan env vars
  (`BAILIAN_CODING_PLAN_API_KEY` + `OPENAI_BASE_URL`) or a plain API key in
  `~/.qwen/settings.json`.
- **Qoder** (qoder.com): credit-based agent platform — Free $0 (2-wk Pro
  trial, 300 credits), Pro $20/mo (2,000 credits), Pro+ $60/mo, Ultra
  $200/mo. Qwen3.8-Max promo Aug 3–Sep 3 2026: 800 free calls; off-peak
  (14:00–00:00 UTC) discounts: Qwen3.8-Max 0.25×, Qwen3.7-Max 0.1×, Qwen3.7-Plus
  0.04×. Agent SDK (TS `@qoder-ai/qoder-agent-sdk`, Python `qoder-agent-sdk`)
  + Cloud Agents API (PAT `pt-` prefix, `api.qoder.com/api/v1/cloud`). No
  published per-token prices.
- **ModelScope** (modelscope.cn): hosted OpenAI-compatible API live
  (`api-inference.modelscope.cn/v1`, 43 models incl 22 Qwen open models),
  China-hosted, English UI via `?lang=en_US`, pricing unpublished
  (console-gated). Qwen Code CLI lists ModelScope as a built-in third-party
  provider.
- **Only live official OpenAI-compatible Qwen endpoints = Alibaba/DashScope**:
  `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` (intl) and
  `https://dashscope.aliyuncs.com/compatible-mode/v1` (Beijing), plus Coding
  Plan endpoints.

## Technique notes

- **SiliconFlow pricing is triple-escaped Next.js flight data** — needs a
  custom JS-string-unescape + RSC key resolution loop; plain regex won't get
  the numbers.
- **DeepInfra has a `__NEXT_DATA__` JSON blob** in its pricing HTML — parse
  that rather than scraping rendered text; individual model pages
  (deepinfra.com/<org>/<Model>) also carry per-model prices.
- **Hyperbolic `.xyz` is dead** (301 → `www.hyperbolic.ai`); pricing is
  app-only, public pages 404.
- **Novita pricing page is client-rendered** — needs a browser pass; exact
  per-model numbers were NOT extracted (marked in table from site copy).
- **OpenRouter `/api/v1/models` shows $0.0000 promos** for these models —
  always cross-check the provider's own page (durable prices only).
