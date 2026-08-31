# Model Pricing Snapshot — Aug 2026

Captured 2026-08-08 from official pricing pages. **Snapshot only — re-verify
against live pages before acting** (prices move; DeepSeek hike pending).

## ⚠️ DeepSeek price-hike warning (official, on their pricing page)

> "We plan to raise the overall pricing for DeepSeek API services in the near
> future, with a **significant increase** expected. Please plan your usage
> accordingly. The specific pricing plan will be subject to official notice."

No numbers published yet — only the warning. Current rates below.

## DeepSeek (api-docs.deepseek.com/quick_start/pricing)

| Model | Input (cache miss) | Output | Context | Notes |
|-------|-------------------|--------|---------|-------|
| deepseek-v4-flash | $0.14/M | $0.28/M | 1M | Hermes default; Responses API supported |
| deepseek-v4-pro | $0.435/M | $0.87/M | 1M | Responses API NOT yet (early Aug 2026) |
| cache-hit input | $0.0028/M (flash) / $0.003625/M (pro) | — | — | |

Responses API base_url: `https://api.deepseek.com` (bare root).
Chat completions base_url: `https://api.deepseek.com/v1/chat/completions`.

## GLM / Z.AI (docs.z.ai/guides/overview/pricing)

| Model | Input | Cached | Output | Context |
|-------|-------|--------|--------|---------|
| GLM-5.2 (newest) | $1.40 | $0.26 | $4.40 | 1M |
| GLM-5.1 | $1.40 | $0.26 | $4.40 | 200K |
| GLM-5 | $1.00 | $0.20 | $3.20 | 200K |
| GLM-5-Turbo | $1.20 | $0.24 | $4.00 | 200K |
| GLM-4.7 | $0.60 | $0.11 | $2.20 | 200K |
| **GLM-4.7-FlashX** | **$0.07** | **$0.01** | **$0.40** | 200K ← cheap tier |
| **GLM-4.7-Flash** | **FREE** | — | **FREE** | 200K |
| GLM-4.5-Air | $0.20 | $0.03 | $1.10 | — |

Z.AI is "limited-time free" on cached-input storage.

## Qwen / Alibaba (Model Studio)

Flagship **Qwen3.8-Max** ("comprehensive leap in coding and professional work")
just dropped; Qwen3.7-Max / 3.7-Plus / 3.7-Flash are the current tier line
(3.7-Plus: native multimodal, 1M context, agentic coding).

| Model | Input (est.) | Output (est.) | Context | Notes |
|-------|--------------|---------------|---------|-------|
| qwen3.8-max | ~$1–3 | ~$3–10 | 1M | new flagship |
| qwen3.7-plus | ~$0.3–0.6 | ~$1–2 | 1M | |
| **qwen3.7-flash** | **~$0.07** | **~$0.4** | 1M | cheap tier |
| qwen3-coder-flash | ~$0.07 | ~$0.4 | 1M | coding-specialised |

Qwen prices need the browser (JS-rendered tables); curl only returns model IDs/URLs.

## OpenRouter snapshot (2026-08-08)

All three families show **$0.0000 promo** on OpenRouter (`/api/v1/models`):
deepseek-v4-flash/-0731/-pro, qwen3.7-* / qwen3.8-max / qwen3-coder-*, z-ai/glm-4.7
/glm-5/5.1/5.2. **These are free-tier promotions, NOT durable prices** — always
cross-check the provider's own page.

## Decision baseline (from this snapshot)

- DeepSeek flash stays best value **unless** the hike triples+ it.
- If DeepSeek triples flash (~$0.42/$0.84): GLM-4.7-FlashX ($0.07/$0.40) and
  Qwen3.7-Flash (~$0.07/$0.40) are the like-for-like swaps.
- GLM-4.7-Flash free tier = zero-cost batch/experiment lane.
- Flagship tier is NOT the default for high-volume agent/cron work.
