# Provider Landscape — Aug 2026 Session Detail (ByteDance verdict + caching economics)

Condensed from the 2026-08-09 provider research session. Live-verified against
official pages/consoles/DNS on that date. Prices per 1M tokens USD unless noted.

## Why this session mattered
User asked: "what other options are out there" → ByteDance infrastructure →
then the sharp question: "what about the caching — we are making massive
savings by using this. Will we get the same via alibaba or this deepinfra?"
The caching answer (below) reframes every future provider recommendation.

## ByteDance / Volcengine — full verdict (NOT usable from AU, verified Aug 2026)

| Check | Result |
|---|---|
| Model family | Doubao Seed 2.1 (pro/turbo) flagship; doubao-seed-evolving (1024K); 2.0 mini/lite/cheap tiers; Seedance (video), Seedream (image), Seed3D |
| Ark pricing (RMB) | 2.1-pro ¥6/¥30 (cache-hit ¥1.2) ≈ $0.84/$4.20; 2.0-mini ¥0.20–0.80 in / ¥2–8 out — cheap IN THEORY |
| Signup | **CN-only** — live form hard-codes +86 mobile, no country selector, no email-only path |
| Payment | RMB only (Alipay/WeChat/CN bank); free quota needs CN real-name verification |
| Domains | volces.com + volcanoengine.com = **NXDOMAIN**; volcengine.com = CN console; doubao.com = consumer chat app |
| API endpoint | `https://ark.cn-beijing.volces.com/api/v3` (OpenAI-compatible, reachable from AU, ~1s TTFB) |
| Singapore region | `ark.ap-southeast-1.volces.com` resolves but **does not answer** from AU (timeout) |
| Verdict | Do not recommend for AU. Only via a third-party aggregator — none verified hosting Doubao. |

## Caching economics — the decision driver
DeepSeek's cache-hit pricing is unmatched: v4-flash $0.0028 (50× cheaper than
miss), v4-pro $0.003625 (120×). Alternatives range 5–10× ratios at
$0.02–$0.30 absolute. For agent workloads (stable system prompts, cron,
delegation) the cache-hit price dominates; rank providers on it.

| Provider | Cache-hit in | Ratio vs miss | Notes |
|---|---|---|---|
| DeepSeek v4-flash | $0.0028 | 50× | current default |
| DeepSeek v4-pro | $0.003625 | 120× | — |
| DeepInfra v4-flash | $0.018 | 5× | same family, best fallback if DS hikes cache |
| Kimi k3 | $0.30 | 10× | 1M ctx, official Hermes guide, AU signup |
| MiniMax M3 | $0.06 | 5× | cheapest alt cache-hit |
| StepFun step-3.7-flash | $0.04 | 5× | — |

Recommended policy: DeepSeek primary while cache-hit stays cheap; DeepInfra as
the swap-ready fallback (already cheaper miss); Kimi/MiniMax only as capability
lanes, not cost lanes.

## Delivery shape signal (user preference)
When asked "what are the options / which is best", deliver a **ranked top-3–5
shortlist with prices + one recommendation immediately**, then offer the deep
dive. The user interrupted mid-research with "So what are the great options?" —
waiting for exhaustive multi-agent research before answering is the wrong
shape. Ship the provisional answer from already-verified data in the first
response; keep the sweep running in the background.

## AU-access reality for the Chinese labs (recap)
- Reachable: Moonshot/Kimi (platform.kimi.ai, email/Google), MiniMax
  (platform.minimax.io), StepFun (platform.stepfun.ai) — all OpenAI-compatible,
  no CN phone.
- CN-only walls: Tencent Hunyuan (real-name auth, hy.tencent.ai geo-blocked),
  Baidu ERNIE (intl cloud has zero ERNIE products), iFlytek Spark (intl = speech
  only), ByteDance Doubao (see above).
- Xiaomi MiMo: no public international API platform (weights on HF only).
