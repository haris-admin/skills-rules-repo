# Chinese AI API Provider Access Map (verified 2026-08-09)

Live-verified snapshot of 7 Chinese labs: flagship + per-1M-token prices, AU signup
without a Chinese phone, OpenAI-compatible endpoint, free tier, AU caveats. Every
number traced to an official page fetched 2026-08-09. Re-verify before acting —
pricing pages change structure often.

## Quick table

| Provider | Intl platform | Flagship | $/1M in / out | AU signup w/o CN phone | OpenAI-compatible base URL |
|---|---|---|---|---|---|
| Moonshot (Kimi) | platform.kimi.ai | kimi-k3 (1M ctx) | 3.00 / 15.00 (0.30 cache-hit) | YES — email code or Google OAuth | https://api.moonshot.ai/v1 |
| MiniMax | platform.minimax.io | MiniMax-M3 | 0.30 / 1.20 (≤512k; permanent 50% promo) | YES — email | https://api.minimax.io/v1 (+ /anthropic) |
| StepFun | platform.stepfun.ai | step-3.7-flash (256K) | 0.20 / 1.15 (0.04 cache-hit) | likely YES — email sign-in | https://api.stepfun.ai/v1 |
| Tencent Hunyuan | none (CN-only) | Hy3 / hunyuan-role-latest | CN ¥ only (see below) | NO — real-name auth; hy.tencent.ai geo-blocked | https://api.hunyuan.cloud.tencent.com/v1 (CN) |
| Xiaomi MiMo | mimo.xiaomi.com | MiMo-V2.5-Pro | not published | — | none found (open weights + JS portal link) |
| Baidu ERNIE | none (intl.cloud.baidu.com is infra-only) | ERNIE 4.5 series (Qianfan) | not published | NO — CN real-name | none international |
| iFlytek Spark | global.xfyun.cn = speech/vision only | Spark (CN platform) | not published | NO — CN phone | WebSocket API, CN only |

## Moonshot AI / Kimi — best AU candidate
- Domains (Aug 2026): intl console+docs = **platform.kimi.ai**; CN = **platform.kimi.com**;
  legacy platform.moonshot.ai still hosts the API. Note: platform.moonshot.cn/docs
  redirects to kimi.com docs.
- Prices (docs/pricing/chat-k3.md, chat-k27-code.md):
  - `kimi-k3`: $0.30 cache-hit / $3.00 cache-miss input, $15.00 output, 1,048,576 ctx.
    Always reasons; `reasoning_effort` (low/high/max, default max).
  - `kimi-k2.7-code`: $0.19 / $0.95 / $4.00, 262K ctx; `-highspeed` = 2x price.
  - `kimi-k2.6`: budget model (cheaper than K3 per docs).
  - Moonshot V1 sunsets 2026-08-31.
- Signup: email verification code OR Sign in with Google — explicitly documented,
  no phone number (docs/guide/account-security-and-sign-in.md).
- Free tier: none. Min top-up **$1** to start; cumulative **$5 → $5 voucher**.
  Rate tiers keyed to cumulative top-up (Tier0 $1: 1 concurrency, 3 RPM, 500K TPM)
  (docs/pricing/limits.md).
- AU caveats: individual top-up docs list WeChat Pay / Alipay QR — international
  card support NOT confirmed in docs for individuals; check checkout or
  platform.kimi.ai/contact-sales. Invoice entity = Beijing Moonshot AI Technology
  Co., Ltd. Docs include an official "Use Kimi K3 in Hermes Agent" guide.

## MiniMax — best AU candidate
- Intl platform.minimax.io (CN twin minimaxi.com). Mintlify docs.
- `MiniMax-M3`: $0.30 in / $1.20 out / $0.06 cache-read for ≤512K input (permanent
  50%-off promo vs list $0.60/$2.40); >512K input $0.60/$2.40. `M2.7` $0.30/$1.20
  (highspeed 2x); M2.5/M2.1/M2 legacy at same $0.30/$1.20.
- Token Plan subscription: Plus $20 / Max $50 / Ultra $120 per month (M3 included);
  Credits 1,000 = $1, packs $5/$25/$100, 365-day validity (docs/guides/pricing-token-plan.md).
- Endpoints: OpenAI-compatible https://api.minimax.io/v1 OR Anthropic-compatible
  https://api.minimax.io/anthropic (Anthropic SDK is their recommended path).
- Signup email-based; real-name verification required for invoices and voice cloning.
- Multimodal: MiniMax-H3 video gen ($0.13/sec 2K), H3-Context-IR $0.90/$3.60 per 1M.

## StepFun — solid third
- Intl **platform.stepfun.ai** (English docs; CN twin platform.stepfun.com;
  stepfun.ai redirects to consumer chat.stepfun.com). CN site shows a banner
  pointing intl users to platform.stepfun.ai.
- `step-3.7-flash` (flagship multimodal reasoning, 198B/11B MoE, 256K ctx):
  $0.20 miss / $0.04 cache-hit / $1.15 out (docs/en/guides/pricing/details).
  `step-3.5-flash` / `step-3.5-flash-2603`: $0.10 / $0.02 / $0.30.
- Free tier: docs say usage draws "free credit first, then paid balance; free
  credit can expire" — amount unpublished. V0 tier at $0 top-up = 5 concurrency,
  10 RPM, 5M TPM (usable without paying).
- Step Plan subscription: Flash Mini $6.99 → Flash Max $99/mo; ~$1 ≈ 7M credits
  (docs/en/step-plan/overview).
- Endpoint https://api.stepfun.ai/v1. Official Hermes Agent integration page in docs.

## Tencent Hunyuan — NOT AU-friendly
- CN platform requires Tencent Cloud real-name auth (personal = Chinese ID).
  Intl tencentcloud.com product-1729 docs = 404 (no intl Hunyuan product).
  Official intl portal **hy.tencent.ai returned "Access Restricted"** (geo-block
  observed from non-CN IP, 2026-08-09).
- CN list prices (cloud.tencent.com/document/product/1729/97731, ¥/1M tokens):
  Hunyuan-a13b ¥0.5/¥2; `hunyuan-role-latest` ¥2.4/¥9.6; hunyuan-translation
  ¥1.2/¥3.6 (+lite ¥1/¥3); vision models (turbos-vision, t1-vision, video) ¥3/¥9;
  hunyuan-embedding ¥0.7/¥0.7. Free 1M tokens on first activation.
- New flagship **Hy3** released 2026-07-06; services migrating to **TokenHub**
  (console.cloud.tencent.com/tokenhub) — old platform stops new model purchases.
- OpenAI-compatible endpoint (CN): https://api.hunyuan.cloud.tencent.com/v1 —
  models hunyuan-turbos / t1 / lite / vision / functioncall / embedding
  (doc product/1729/111007).

## Xiaomi MiMo — no API pricing
- mimo.xiaomi.com: MiMo-V2.5-Pro (1T-param class per blog), MiMo-V2.5, TTS/ASR
  series. Site has an "API Access → developer portal" link (JS-rendered; target
  not resolved). Open weights on HuggingFace. No published per-token pricing.

## Baidu ERNIE — NOT AU-friendly
- intl.cloud.baidu.com = infrastructure products only (BCC/BOS/VPC/CSN etc.),
  zero ERNIE/Qianfan/LLM products. qianfan.baidubce.com = 404.
- Qianfan pricing pages (qianfan.cloud.baidu.com) are JS-rendered; no numbers
  extractable via curl. Mainland Qianfan requires CN real-name verification.

## iFlytek Spark — LLM is CN-only
- Spark LLM lives on xfyun.cn (CN phone signup; WebSocket/HTTP API docs at
  xfyun.cn/doc/spark/Web.html). Pricing page xinghuo.xfyun.cn/sparkapi?scr=price
  is a 2KB JS shell — no numbers extractable.
- Intl platform **global.xfyun.cn is speech/vision only** (TTS, ASR, OCR,
  translation, virtual broadcast) with email signup + free trial packages —
  no Spark LLM offered internationally.

## Method notes (verified working Aug 2026)
- **Mintlify llms.txt trick**: Kimi, MiniMax and StepFun all serve
  `docs/llms.txt` + `.md` page twins → curl pricing directly, no browser:
  platform.kimi.ai/docs/llms.txt, platform.minimax.io/docs/llms.txt,
  platform.stepfun.ai/docs/llms.txt. Price tables are `<DocTable>` components in
  the .md — grep for `rows={` / `"$"` values.
- Tencent CN docs server-render — curl with `--compressed` works. Intl
  tencentcloud.com is a JS SPA returning the same ~29KB shell for every path
  (check content, not HTTP 200).
- Chinese-encoded textified files can trip read_file's binary detection —
  re-decode/filter via python instead.
- JS-only: stepfun.ai (redirects), platform.stepfun.com, xinghuo price page,
  qianfan pricing → browser needed.
