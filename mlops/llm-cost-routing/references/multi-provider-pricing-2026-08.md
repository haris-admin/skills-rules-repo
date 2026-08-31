# Multi-Provider Chinese LLM Pricing Snapshot — Aug 9, 2026

Sweep of 11 inference providers for Qwen / DeepSeek / GLM per-1M-token pricing.
All prices USD per 1M tokens, cache-miss input unless noted. Verified by
curl-ing each provider's pricing page (or browser for JS-rendered pages) on
2026-08-09. Treat as a snapshot — re-verify before acting (see SKILL.md
procedure).

## Coverage of the target model list

| Model asked | Where actually found (Aug 2026) |
|---|---|
| Qwen3.8-max | DeepInfra ($1.65/$4.951), Novita "Qwen3.8 Max" ($2/$6, 977K ctx) |
| Qwen3.7-plus | Together only ($0.32/$1.28) |
| Qwen3.7-flash | Not found on any of the 11 (hosted directly via DashScope/Qwen portal instead) |
| Qwen3-coder | Novita "Qwen3 Coder 480B A35B" $0.38/$1.55 256K; DeepInfra Qwen3-Coder-480B-Turbo $0.30/$1.00; Novita "Qwen3 Coder Next" $0.2/$1.5 |
| DeepSeek v4-flash | DeepInfra, Novita, Together ("V4 Flash 0731"), SiliconFlow |
| DeepSeek v4-pro | DeepInfra, Novita, Together, SiliconFlow |
| GLM-5.2 | Novita, Together, SiliconFlow, **DeepInfra** ($0.75/$0.14-cached/$2.40, 1M ctx — verified on its model page; NOT in the DeepInfra pricing-page table) |
| GLM-5 | DeepInfra, Novita, SiliconFlow, Together (fine-tune list) |
| GLM-4.7-flash | DeepInfra, Novita, SiliconFlow(.com has GLM-5.2/5.1/5 only), Cerebras (GLM 4.7, preview, deprecating) |
| GLM-4.7-flashX | Not found on any of the 11 (Z.AI direct only) |

## Per-provider table (input / cached-input / output, per 1M tokens)

### DeepInfra (deepinfra.com — pricing table + per-model pages)
OpenAI-compatible API, open signup. Table is INCOMPLETE — model pages
(deepinfra.com/<org>/<model>) have exact prices + a second "Flex" (batch) tier.

| Model | Input | Cached | Output | Context |
|---|---|---|---|---|
| deepseek-ai/DeepSeek-V4-Flash | $0.09 | $0.018 | $0.18 | 1024k |
| deepseek-ai/DeepSeek-V4-Pro | $1.30 | $0.10 | $2.60 | 1024k |
| Qwen/Qwen3.8-Max | $1.65 | $0.206 | $4.951 | 256k (per page; Novita says 977K) |
| Qwen/Qwen3.7-Max | $2.50 | $0.50 | $7.50 | 250k |
| Qwen3-Coder-480B-A35B-Turbo | $0.30 | $0.10 | $1.00 | 256k |
| zai-org/GLM-5.1 | $1.05 | $0.205 | $3.50 | (batch: $0.84/$0.164/$2.80) |
| zai-org/GLM-5 | $0.60 | $0.12 | $2.08 | (batch: $0.48/$0.096/$1.664) |
| zai-org/GLM-4.7-Flash | $0.06 | $0.01 | $0.40 | (batch: $0.048/$0.008/$0.32) |
| zai-org/GLM-5.2 | $0.75 | $0.14 | $2.40 | 1024k — from its model page (deepinfra.com/zai-org/GLM-5.2); pricing-page table omits it; also supports service tiers (priority 1.5×, flex 0.8×) |

### Novita AI (novita.ai/pricing — server-side, richest table w/ context)
OpenAI-compatible, open signup. No free tier advertised on page.

| Model | Input | Cached | Output | Context |
|---|---|---|---|---|
| Deepseek V4 Flash / Flash 0731 | $0.14 | $0.028 | $0.28 | 1M |
| Deepseek V4 Pro | $1.60 | $0.135 | $3.20 | 1M |
| Qwen3.8 Max | $2.00 | $0.25 | $6.00 | 977K |
| Qwen3.7-Max | $1.25 | $0.25 | $3.75 | 977K |
| Qwen3 Coder 480B A35B Instruct | $0.38 | — | $1.55 | 256K |
| GLM 5.2 | $1.40 | $0.26 | $4.40 | 1M |
| GLM-5.1 | $1.38 | $0.26 | $4.40 | 200K |
| GLM-5 | $1.00 | $0.20 | $3.20 | 198K |
| GLM-4.7-Flash | $0.07 | $0.01 | $0.40 | 195K |
| GLM-4.7 | $0.60 | $0.11 | $2.20 | 200K |

### Together AI (together.ai/pricing — server-side; row format: Input / (cached) / Output)
OpenAI-compatible, open signup. No free tier on page. Context not listed on
pricing page.

| Model | Input | Cached | Output |
|---|---|---|---|
| DeepSeek V4 Pro | $1.74 | $0.20 | $3.48 |
| DeepSeek V4 Flash 0731 | $0.14 | $0.03 | $0.28 |
| Qwen3.7-Max | $1.25 | $0.13 | $3.75 |
| Qwen3.7-Plus | $0.32 | — | $1.28 |
| Qwen3.6-Plus | $0.50 | — | $3.00 |
| Qwen3.5-397B-A17B | $0.60 | $0.35 | $3.60 |
| GLM-5.2 / GLM-5.1 | $1.40 | $0.26 | $4.40 |

### SiliconFlow (siliconflow.com/pricing USD; .cn has RMB ¥)
**TWO separate platforms.** International = `account.siliconflow.com` (login:
"Continue with Google" / "Continue with GitHub" — no Chinese phone), OpenAI-
compatible base URL `https://api.siliconflow.com/v1`, $1 free credit, postpaid
billing, monthly spend limits. China = `account.siliconflow.cn` (RMB ¥).
Prices differ per platform. The .cn pricing page is Next.js RSC flight data —
decode with `scripts/decode_sf_flight.py`; the .com page is Framer (prices in
framerusercontent.com searchIndex-*.json). No Qwen3.7/3.8-Max.

| Model | Input | Cached | Output | Context |
|---|---|---|---|---|
| DeepSeek-V4-Pro | $1.50162 | $0.135 | $3.135 | 1049K |
| DeepSeek-V4-Flash | $0.13 | $0.028 | $0.28 | 1049K |
| GLM-5.2 | $1.302 | $0.26 | $4.092 | 1049K |
| GLM-5.1 | $1.19 | $0.60 | $3.74 | 205K |
| GLM-5 | $0.95 | $0.20 | $2.55 | 205K |
| Qwen3.6-27B | $0.30 | — | $3.20 | 262K |
| Qwen3-Coder-30B-A3B-Instruct | $0.07 | — | $0.28 | — (cheapest verified Qwen lane on .com) |

CN (¥ per 1M): DeepSeek-V4-Pro ¥12/¥24/¥1.00 · V4-Flash ¥1.00/¥2.00/¥0.02.

### Groq (console.groq.com/docs/models — JS, browser)
OpenAI-compatible (api.groq.com/openai/v1), open signup, historically $1 free
credit. Only Chinese model: **Qwen/Qwen3.6-27B (preview)** $0.60 in / $3.00 out,
131,072 ctx, ~500 t/s. Everything else is Llama/GPT-OSS/Whisper/MiniMax M2.7
(contact sales).

### Cerebras (cerebras.ai/pricing — JS, browser)
OpenAI-compatible, **$5 free credits**, Developer tier self-serve from $10.
Only Chinese model: **ZAI GLM 4.7** (preview `**`, deprecation Aug 17, 2026)
$2.25 in / $2.75 out, ~1000 t/s. Others: GPT-OSS-120B $0.35/$0.75, Gemma 4 31B
$0.99/$1.49.

### Fireworks AI (fireworks.ai/pricing)
OpenAI-compatible, $1 free credits. Pricing page is size-bracket serverless
($/1M input: ≤150M $0.008, 150-350M $0.016, Qwen3 8B $0.10) + GPU-hour on-demand
(H100/H200 $7/hr, B200 $10/hr, B300 $12/hr). Per-model prices live in
docs.fireworks.ai/models. Hosts Qwen3 8B / Qwen 3.5 9B / Qwen 3.6 27B (Serverless
Training API: 9B $0.66/$1.995 64k; 27B $1.86/$5.595 128k) — no DeepSeek V4 /
GLM-5.x.

### Hyperbolic — NO hosted per-token pricing
`hyperbolic.xyz/pricing` 404s; site + docs (Mintlify, browser-only) are
GPU-rental (on-demand H100/H200/B200 clusters). OpenAI-compatible API mentioned
generically for self-served models. Nothing comparable for the target list.

### Baseten — BYO-weights serverless
`baseten.ai/pricing` unreachable (HTTP 000). Per-GPU-second billing for your own
deployed weights; docs at docs.baseten.co. No managed Chinese-model catalog.

### Lambda — GPU cloud
`lambda.ai/inference` is JS marketing + "LLM index" benchmarks; no hosted
per-token pricing for these models.

### Modal — compute, not model API
`modal.com/pricing`: per-second GPU (B300 $0.001972/s, B200 $0.001736/s, H200
$0.001261/s, H100 $0.001097/s...), Starter plan $30/month free credit. New
"Shared Endpoints" with token pricing (banner: Kimi K3) — pattern to watch, no
Chinese-model token pricing yet.

## Bottom-line verdicts (Aug 2026)

- **Cheapest flash-tier verified**: DeepInfra DeepSeek-V4-Flash $0.09/$0.18
  (1M ctx) and GLM-4.7-Flash $0.06/$0.40 — DeepInfra is the cost leader of the 11.
- **Broadest Chinese-model catalog**: Novita (Qwen3.8/3.7-Max + GLM-5.2 + V4 all
  in one place), then DeepInfra.
- **DeepSeek V4 Pro cheapest resellers**: SiliconFlow $1.50/$3.14, Novita
  $1.60/$3.20, DeepInfra $1.30/$2.60 (DeepInfra also cheapest for Pro).
- **Direct-vs-reseller spread is large**: DeepSeek's own API for V4 Pro was
  ~$0.44/$0.87 vs $1.30–$1.74/$2.60–$3.48 on resellers — quote the source.
- **Not viable for this workload**: Groq/Cerebras (only legacy/preview Chinese
  models), Hyperbolic/Lambda/Modal/Baseten (no comparable per-token pricing).
