---
name: llm-cost-routing
description: "Pick cost-effective LLM fallbacks across providers."
version: 1.0.0
author: Pluto
license: MIT
category: mlops
platforms: [linux, macos, wsl]
metadata:
  hermes:
    tags: [llm, pricing, deepseek, glm, qwen, openrouter, cost-routing, or_free]
    related_skills: [pluto-autonomous-research, genspark-agent-orchestration]
---

# LLM Cost Routing

## When to Use

- User asks "is <provider> still the best deal?" or "should we switch models?"
- A provider announces a price change (e.g. DeepSeek's planned hike)
- Choosing fallback models for `or_free.py`, Hermes default, or Codex providers
- Comparing DeepSeek / GLM / Qwen flash-tier economics for high-volume cron/agent work
- Any model-selection decision where per-1M-token price is the deciding factor

## The 3-Phase Routing Pattern (or_free.py)

`~/.hermes/scripts/or_free.py` implements the canonical cost ladder — keep this
shape when adjusting models:

1. **Phase 1 — free OpenRouter models** (try first, zero cost)
2. **Phase 2 — cheap coding models via OpenRouter** (`CHEAP_CODING` list)
3. **Phase 3 — our paid DeepSeek API** (reliable, `api.deepseek.com/v1/chat/completions`,
   key `DEEPSEEK_API_KEY` from Windows `.env`)

Each phase falls through to the next on failure. Adding a new fallback = add the
model id to the correct phase list (or a new phase), never a code rewrite.

## Qwen access paths for Hermes (no OpenRouter needed)

Qwen/QAN is a first-class Hermes provider, verified from `hermes_cli/auth.py`
+ live endpoint probes (Aug 2026). The user prefers these over OpenRouter
routing. ⚠️ The old **Qwen Portal OAuth** path is DEAD since 2026-04-15 — see
pitfalls below.

| Path | Hermes provider id | Key env var | Base URL | Best for |
|------|-------------------|-------------|----------|----------|
| **DashScope API key** (recommended, simplest) | `alibaba` ("Qwen Cloud") | `DASHSCOPE_API_KEY` | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` | Pay-as-you-go; works for Hermes + cron + delegation |
| **Alibaba Coding Plan** | `alibaba-coding-plan` | `ALIBABA_CODING_PLAN_API_KEY` (falls back to `DASHSCOPE_API_KEY`) | `https://coding-intl.dashscope.aliyuncs.com/v1` (intl) / `https://coding.dashscope.aliyuncs.com/v1` (Beijing) | Flat-rate subscription for heavy agent use |
| ~~Qwen Portal OAuth~~ **GONE** | ~~`qwen-oauth`~~ | — | `https://portal.qwen.ai/v1` → 404 everywhere | Dead 2026-04-15; migrate to Coding Plan / DashScope / third-party |

Other non-OpenRouter Qwen channels worth knowing (neither is a Hermes provider
id; details + pricing in `references/qwen-ecosystem-access-2026-08.md`):

- **Qoder** (qoder.com, Qwen's coding agent, op. Bright Zenith Pte Ltd) —
  credit-based plans (Free 2-wk trial 300 cr / Pro $20 / Pro+ $60 / Ultra
  $200/mo, top-up $20/1500 cr), BYOK supported, **Agent SDK** (Python/TS,
  auth via PAT `pt-...` from qoder.com/account/integrations) and **Cloud
  Agents API** (Beta, `https://api.qoder.com/api/v1/cloud` + `/forward`).
  No per-token prices published; credits ≈1–3 simple ask … 50–75 Quest/Experts.
- **ModelScope hosted inference** (modelscope.cn, Alibaba's model hub) —
  OpenAI-compatible `https://api-inference.modelscope.cn/v1`; serves 22 open
  Qwen models (Qwen3/Qwen3.5/VL/Image/Coder — NOT flagship qwen3.8-max).
  China-hosted (modelscope.com just redirects to modelscope.cn?lang=en_US);
  free registration, no public per-token price list. Also a built-in
  third-party provider in qwen-code CLI `/auth`.

Setup procedure:
1. DashScope: create Alibaba Cloud intl account → Model Studio → API key, then
   `hermes auth add alibaba` → `hermes model` → pick `qwen3.8-max`.
2. **Do NOT use qwen-oauth** — the Qwen Portal OAuth free tier was discontinued
   2026-04-15 (portal.qwen.ai is dead); DashScope API key or the Coding Plan are
   the reliable paths.
3. Coding Plan / Token Plan: `ALIBABA_CODING_PLAN_API_KEY` → provider
   `alibaba-coding-plan`; or Token Plan (Team Edition) Standard seat from $6/mo
   for flat-rate Qwen + DeepSeek access (see `references/alibaba-cloud-qwen-access.md`).

Models confirmed on the intl platform (Aug 2026): `qwen3.8-max` (newest
flagship, coding-leap), `qwen3.7-max`, `qwen3.7-plus`, `qwen3.7-flash` (1M ctx),
`qwen3-coder`/`qwen3-coder-plus`. All three paths are general LLM APIs — no
restriction on autonomous-agent use (unlike some consumer plans). DashScope
terms permit agent workflows; Coding Plan is explicitly positioned for
developer/agent tooling.

**Pitfall — pricing page is JS-heavy:** Alibaba model/billing pages render
prices client-side; curl gets model IDs but not numbers (see "How to Check
Current Pricing" below). Use the browser for actual Qwen prices, or OpenRouter
`/api/v1/models` JSON as a quick cross-check (but treat $0.0000 as promo, not
durable).

## Hermes native provider registry — check BEFORE recommending (verified Aug 2026)

Before recommending any provider, check whether Hermes ships it natively
(`hermes_cli/providers.py` — HermesOverlay entries). Native = zero config
beyond the API key; non-native = custom provider block (base_url + env key).

Chinese-model-relevant NATIVE providers (provider id → key env var):

| Provider id | Models | Key env var | Notes |
|---|---|---|---|
| `deepseek` | DeepSeek V4 flash/pro | `DEEPSEEK_BASE_URL` | current default |
| `zai` | GLM-5.2/5.1/5, GLM-4.7-Flash | `GLM_API_KEY` / `ZAI_API_KEY` | probe-zai logic in auth.py |
| `alibaba` | Qwen3.8/3.7-max, qwen3.7-plus/flash | `DASHSCOPE_BASE_URL` | intl base `dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| `alibaba-coding-plan` | Qwen + DeepSeek (Coding Plan) | `ALIBABA_CODING_PLAN_BASE_URL` | |
| `kimi-for-coding` | Kimi K2.x (Moonshot) | `KIMI_BASE_URL` | native — often forgotten |
| `stepfun` | Step-3.x | `STEPFUN_API_KEY` | |
| `minimax` / `minimax-oauth` / `minimax-cn` | MiniMax-M2.x | `MINIMAX_BASE_URL` | anthropic_messages transport |
| `tencent-tokenhub` | Hunyuan (Tencent) | `TOKENHUB_BASE_URL` | |
| `xiaomi` | MiMo | `XIAOMI_BASE_URL` | |
| `novita` | Qwen/DeepSeek/GLM catalog | `NOVITA_BASE_URL` | |
| `fireworks` | Qwen, DeepSeek V3 | `FIREWORKS_API_KEY` | |
| `nvidia` | NIM-hosted open models | `NVIDIA_BASE_URL` | |

**NOT native — needs a custom provider block:** ByteDance / Volcengine
(Doubao models) — no `volcengine`/`doubao` key in providers.py (verified Aug
2026). Volcengine Ark IS OpenAI-compatible so a 4-line custom provider would
work in principle; **BUT ByteDance is effectively DEAD for AU users (verified
Aug 2026) — see ByteDance verdict below.** Same custom-provider treatment
applies to DeepInfra and any non-native host.

### ByteDance / Volcengine Doubao — AU verdict: NOT usable (verified Aug 2026)

Live-verified from volcengine.com + console + DNS probes:
- **Signup is CN-only.** The live signup form (`console.volcengine.com/auth/signup`)
  is hard-coded to **+86 Chinese mobile** (no country selector, no email-only
  path); payment is RMB (Alipay/WeChat/CN bank); free-quota exhaustion requires
  CN 实名认证 real-name verification.
- **No international domain resolves.** `volces.com` and `volcanoengine.com` are
  NXDOMAIN (verified via Cloudflare + Google DoH). `volcengine.com` is the only
  live site and it is CN-only. `doubao.com` is the consumer chat app, not an API
  platform.
- **The Singapore Ark endpoint is a mirage.** `ark.ap-southeast-1.volces.com`
  resolves to a Singapore ALB but does not answer from AU (connection timeout);
  only `ark.cn-beijing.volces.com/api/v3` works, adding ~1s TTFB per call from AU
  (DeepSeek api.deepseek.com is ~0.21s from the same host).
- Models (for reference if a partner channel ever appears): Doubao Seed 2.1
  (¥6/¥30 per 1M, ¥1.2 cache-hit ≈ $0.84/$4.20), doubao-seed-evolving (1024K
  ctx), 2.0-mini cheapest (¥0.20–0.80 in).
- **Verdict: do not recommend ByteDance for AU.** Only via a third-party
  aggregator would Doubao be reachable, and no AU-usable one was verified.
  Kimi/MiniMax/StepFun are the reachable Chinese labs (see Direct Chinese API
  Platforms).

**Pitfall — native provider ≠ user's preference.** The user explicitly does
NOT want OpenRouter routing for Qwen; native Alibaba/DashScope is preferred.
Check the user's stated preference before recommending a provider, even one
that's technically native.

## Deliverable shape — ranked shortlist FIRST (user signal, Aug 2026)

When the user asks "what are the options / which is best", deliver a **ranked
top-3-to-5 shortlist with prices and a single recommendation immediately**,
then offer the deep-dive. The user interrupted mid-research with "So what are
the great options?" — waiting for exhaustive multi-agent research before
answering is the wrong shape. Keep the sweep running, but ship the provisional
answer from already-verified data in the first response.

## How to Check Current Pricing (procedure)

| Provider | Official page | Method |
|----------|--------------|--------|
| DeepSeek | `https://api-docs.deepseek.com/quick_start/pricing` | curl + strip HTML tags |
| GLM / Z.AI | `https://docs.z.ai/guides/overview/pricing` | curl + strip HTML tags (renders fine) |
| Qwen (Alibaba) | `https://www.alibabacloud.com/help/en/model-studio/model-pricing` | ⚠️ JS-heavy — use browser_navigate, prices are in a table near the bottom |
| OpenRouter aggregate | `https://openrouter.ai/api/v1/models` | curl JSON, filter by id |

### Multi-provider sweep (workflow, verified Aug 2026)

When asked to compare the SAME model family across many inference providers
(e.g. "Qwen/DeepSeek/GLM prices on Together, Groq, Fireworks, Novita,
DeepInfra, SiliconFlow, Cerebras, ..."), do NOT fetch pages one at a time —
that burns tool iterations. Sweep instead:

1. **One curl loop, all providers**: `for u in ...; do curl -sL -A "<browser UA>" "$u" -o "$(echo $u|md5sum|cut -c1-8).html" -w "HTTP %{http_code} size %{size_download}\n"; done` — the HTTP code + size line tells you instantly which pages 404'd or failed (HTTP 000 = unreachable).
2. **One python pass to textify ALL files**: strip `<script>/<style>`, replace tags with newlines, unescape entities, drop blank lines → `t_<name>.txt` per provider.
3. **One grep per question across all files** with a per-file header (`=== $f ===`) — first for model names, then for `\$[0-9]` price lines.
4. **Browser only for JS-rendered pages** (Groq, Cerebras, Lambda, Fireworks docs) — curl gets the shell, browser_navigate gets the table.

Provider URL map + gotchas (all hit in Aug 2026):

| Provider | Best URL(s) | Rendering | Gotcha |
|---|---|---|---|
| Together | `together.ai/pricing` | server-side ✅ | Table rows are Model / Input / **(cached)** / Output — the number next to "(cached)" IS the cached-input price, last number is output |
| Novita | `novita.ai/pricing` | server-side ✅ | Richest table: includes context length per model; has Qwen3.7/3.8-Max, GLM-5.2/5.1/5, GLM-4.7-Flash, DeepSeek V4 |
| DeepInfra | `deepinfra.com/pricing` + per-model pages `deepinfra.com/<org>/<model>` | server-side ✅ | Pricing page table is INCOMPLETE (misses Qwen3.8-Max, GLM-5.x) — fetch the individual model pages for exact Input/Output/Cached; each also shows a second "Flex" (batch) tier block |
| SiliconFlow | `siliconflow.com/pricing` (USD) AND `siliconflow.cn` (RMB ¥) | ⚠️ NOT plain server-side — see pitfall below | .com is a Framer site (prices in `framerusercontent.com` searchIndex JSON); .cn embeds prices in triple-escaped Next.js RSC flight data — run `scripts/decode_sf_flight.py` on the curl'd HTML; .com prices like $1.50162 are real (not typos) |
| Groq | `groq.com/pricing` ❌ redirects to homepage | JS — browser | Real model+price list is `console.groq.com/docs/models` (production/preview tables with $/1M input+output, context, max completion) |
| Cerebras | `cerebras.ai/pricing` | JS — browser | Table has Model/Speed/Input/Output; preview models carry `**` + deprecation dates (e.g. GLM 4.7 deprecates Aug 17, 2026) — don't build on deprecating previews |
| Fireworks | `fireworks.ai/pricing` (bracketed tiers) + `docs.fireworks.ai/models` (per-model) | mixed | Pricing page = size-bracket ($/1M by param count) + GPU-hour; per-model numbers live in docs |
| Hyperbolic | `hyperbolic.xyz/pricing` → **404** | — | Pivoted to GPU-rental cloud; no hosted per-token model pricing anywhere on site/docs |
| Baseten | `baseten.ai/pricing` → HTTP 000 | — | BYO-weights serverless, per-GPU-second billing, not comparable per-token; docs at `docs.baseten.co` |
| Lambda | `lambda.ai/inference` | JS — marketing | No token prices; GPU cloud + "LLM index" benchmarks only |
| Modal | `modal.com/pricing` | server-side ✅ | Per-second GPU/compute (not per-token) — but they now offer token-based "Shared Endpoints" for some models (e.g. Kimi K3) |

**Pitfall — a provider not hosting the target models is a real finding**: report
"not hosted" per provider rather than leaving the cell blank or guessing.
Sweep verdicts from Aug 2026: cheapest verified flash-tier across the 11 =
DeepInfra DeepSeek-V4-Flash $0.09/$0.18 (1M ctx) and GLM-4.7-Flash $0.06/$0.40;
DeepInfra + Novita have the broadest Chinese-model catalogs.

**Pitfall — third-party inference prices ≠ vendor's own API price**: DeepSeek
V4 Pro was ~$0.44/$0.87 direct from DeepSeek but $1.30–$1.74/$2.60–$3.48 on
inference providers (Novita $1.60/$3.20, SiliconFlow $1.50/$3.14, Together
$1.74/$3.48). Always label which price source you're quoting.

**Pitfall — probe docs-platform endpoints before reaching for the browser**:
try `llms.txt` and per-page `.md` variants first — they work on some platforms
(Qoder's `docs.qoder.com/llms.txt` is a full 66KB clean-markdown index and every
page has a `.md` twin; fetch with `curl --compressed`, it's gzipped). Mintlify
sites (`docs.hyperbolic.xyz` etc.) serve only an HTML shell, and custom SPAs
(e.g. `modelscope.cn/docs/...`, even `*.md` URLs) do too — those need the
browser. A one-line probe loop (`curl -sL -o /dev/null -w "%{http_code}"`)
over the candidates sorts this out in a single pass.

**Pitfall — OpenRouter shows $0.0000 promo prices** for many models (free-tier
promotions). That is NOT the durable price. Always confirm the real rate on the
provider's own pricing page before recommending a switch.

**Pitfall — Alibaba's model page requires JS** (help.aliyun.com + alibabacloud.com
render pricing tables client-side). `curl` gets model IDs/URLs but not prices;
use the browser for actual numbers.

**Pitfall — SiliconFlow has TWO separate platforms with different accounts &
prices.** `.cn` = China domestic (RMB ¥, `account.siliconflow.cn`); `.com` =
international (USD, `account.siliconflow.com`, signup via **Continue with
Google / GitHub — NO Chinese phone needed**, $1 free credit, OpenAI-compatible
base URL `https://api.siliconflow.com/v1`). Prices differ per platform (e.g.
DeepSeek-V4-Flash: ¥1/¥2 on .cn vs $0.13/$0.28 on .com). Both `/v1/models`
endpoints return 401 without a key — that's normal, it's an OpenAI-style API.
International docs: `docs.siliconflow.com` (Mintlify — has `llms.txt` +
`llms-full.txt`; docs even include an official Hermes Agent integration guide).

**Pitfall — siliconflow.cn pricing page is Next.js RSC flight data, not
server-rendered HTML.** Prices live in triple-escaped `self.__next_f.push([1,"..."]);`
chunks: `\\n`/`\\\"` in the raw file, chunk terminator is `"])</script>` (no
semicolon — a naive `"]);` regex finds nothing). Use `scripts/decode_sf_flight.py`
(does JS-string unescape + RSC `$ref` resolution; ~60 models with in/out). The
`.com` Framer page has no flight data — its model prices are in
`framerusercontent.com/sites/.../searchIndex-*.json` (blocks shaped
`"Input Price","$","0.13","/ M Tokens",[,"Cache Read","0.028",],"Output Price","0.28"`).

**Pitfall — DeepInfra `cents_per_input_token` is CENTS per token.** $/M =
value × 1e6 / 100 (e.g. 9e-06 → $0.09/M). On DeepInfra model pages, the first
price-bearing NEXT_DATA match may belong to a DIFFERENT (related) model — grep
for the model's own `full_name`, or just render the page in the browser
(verified: DeepInfra DOES host GLM-5.2 at $0.75/$0.14-cached/$2.40, 1M ctx —
cheaper than SiliconFlow intl $1.30/$4.09).

## Hosted Inference Providers — Chinese Models (verified Aug 2026)

Full landscape surveyed by 3 research agents (2026-08-09). Prices = per 1M tokens, cache-miss input. All are OpenAI-compatible unless noted.

| Provider | DeepSeek V4-Flash | GLM-4.7-Flash | GLM-5.2 | Qwen3.8-Max | Qwen3.7-Plus | Notes |
|----------|-------------------|---------------|---------|-------------|--------------|-------|
| **DeepInfra** | **$0.09/$0.18** ← cheapest | $0.06/$0.40 | **$0.75/$2.40** (1M ctx) | $1.65/$4.95 (256K) | — | SOC2/ISO27001, US signup, no free credits, 1M ctx on V4 |
| **Novita AI** | $0.14/$0.28 | $0.07/$0.40 | $1.40/$4.40 | $2.00/$6.00 | — | Broadest catalog (all 3 families), 977K ctx, US co |
| **SiliconFlow intl** | $0.13/$0.28 | — | $1.30/$4.09 | (Qwen3.6 only) | — | $1 free credit, Google/GitHub login, official Hermes guide, CN .cn platform separate |
| **Together AI** | $0.14/$0.28 | — | $1.40/$4.40 | — | **$0.32/$1.28** ← only host | cheapest V4-Pro ($1.74/$3.48) |
| Groq | — | — | — | — | — | only Qwen3.6-27B preview $0.60/$3.00 |
| Cerebras | — | — | — | — | — | GLM-4.7 preview $2.25/$2.75, **deprecating Aug 17 2026** |
| Fireworks | V3 legacy | — | — | — | — | $1 free credits, Qwen3-8B $0.10 |

**Best value for Hermes agent (high tool-call volume, cron jobs):**
1. **DeepInfra** — cheapest verified V4-Flash ($0.09/$0.18, ~35% below direct DeepSeek) + GLM-5.2 1M-ctx at $0.75/$2.40; SOC2-certified, US payment, open signup. Best single value.
2. **Novita AI** — near-Direct prices + broadest Chinese-model coverage in one endpoint.
3. **SiliconFlow intl** — cheapest Qwen open lane (Qwen3-14B/Coder-30B $0.07/$0.28), Google login, $1 credit, official Hermes integration guide.
4. **Together AI** — pick for Qwen3.7-Plus or cheapest V4-Pro.

**Avoid for this workload:** Groq/Cerebras (preview/legacy only, Cerebras GLM-4.7 deprecates Aug 17 2026), Hyperbolic (pricing app-only, now hyperbolic.ai), Lambda/Modal/Baseten (GPU-rental, no hosted per-token pricing).

### Qwen official ecosystem status (verified Aug 2026)
- **Qwen Portal / portal.qwen.ai — DEAD** (discontinued 2026-04-15, all paths 404). qwen.ai is consumer-only (Qwen Studio chat).
- **Qwen Code CLI** `/auth` now offers: Alibaba ModelStudio (Coding Plan / Token Plan / Standard API key), third-party keys (DeepSeek, MiniMax, Z.AI, ModelScope, OpenRouter), or custom provider. Qwen OAuth option removed.
- **Qoder** (qoder.com): credit-based agent platform — Free (2-wk Pro trial 300 credits), Pro $20/mo, Pro+ $60/mo, Ultra $200/mo. Qwen3.8-Max promo Aug 3–Sep 3 2026: 800 free calls. Agent SDK + Cloud Agents API (PAT auth, `pt-` prefix). No published per-token prices.
- **ModelScope** (modelscope.cn): hosted OpenAI-compatible API live (api-inference.modelscope.cn, 43 models incl 22 Qwen), China-hosted, English UI via ?lang=en_US, pricing unpublished (console-gated).

## Direct Chinese API Platforms (Kimi / MiniMax / StepFun) — verified Aug 2026

For the big Chinese labs' OWN APIs (not third-party inference), access changed a
lot in 2026. Full snapshot + AU signup details in
`references/chinese-provider-access-2026-08.md`. Quick facts:

| Platform | Flagship | $/1M in / out | AU signup w/o CN phone | OpenAI-compatible base URL |
|---|---|---|---|---|
| Moonshot Kimi (intl) | kimi-k3 (1M ctx) | 3.00 / 15.00 (0.30 cache-hit) | ✅ email code or Google (platform.kimi.ai) | https://api.moonshot.ai/v1 |
| MiniMax (intl) | MiniMax-M3 | 0.30 / 1.20 (≤512k, permanent 50% promo) | ✅ email (platform.minimax.io) | https://api.minimax.io/v1 (+ /anthropic) |
| StepFun (intl) | step-3.7-flash (256K) | 0.20 / 1.15 (0.04 cache-hit) | likely ✅ (platform.stepfun.ai) | https://api.stepfun.ai/v1 |
| Tencent Hunyuan | Hy3 / hunyuan-role-latest | CN ¥ only | ❌ real-name auth; hy.tencent.ai geo-blocked | https://api.hunyuan.cloud.tencent.com/v1 (CN) |

**Mintlify trick:** all three intl platforms serve `llms.txt` + `.md` page twins
(platform.kimi.ai/docs/llms.txt, platform.minimax.io/docs/llms.txt,
platform.stepfun.ai/docs/llms.txt) — curl the pricing `.md` directly instead of
fighting JS sites. Xiaomi MiMo, Baidu ERNIE and iFlytek Spark have no
AU-usable international LLM API (open weights / CN real-name walls / speech-only
intl platform respectively) — don't burn time on their JS pricing pages.

## Caching is the DECISION DRIVER for agent workloads (Aug 2026) 🔥

For an agent like Hermes (long stable system prompts, repeated cron prompts,
delegation fan-outs sharing base context), **cache-hit input price dominates
the bill** — cache-miss and output are a small fraction of tokens. The user's
own framing: *"we are making massive savings by using this [caching]"* — any
provider recommendation that ignores cache-hit pricing is wrong.

| Provider | Model | Cache-Miss in | **Cache-Hit in** | Ratio | Output |
|---|---|---|---|---|---|
| **DeepSeek** | v4-flash | $0.14 | **$0.0028** | **50×** | $0.28 |
| **DeepSeek** | v4-pro | $0.435 | **$0.003625** | **120×** | $0.87 |
| DeepInfra | v4-flash | $0.09 | $0.018 | 5× | $0.18 |
| Kimi (Moonshot) | k3 | $3.00 | $0.30 | 10× | $15.00 |
| MiniMax | M3 | $0.30 | $0.06 | 5× | $1.20 |
| StepFun | step-3.7-flash | $0.20 | $0.04 | 5× | $1.15 |
| Alibaba | qwen3.7-max | ~$1.25 (promo) | implicit cache (~50% off) | 2× | ~$3.75 |

**Consequences (the honest answer when the user asks "is X cheaper?"):**
1. **DeepSeek stays primary even after a "significant" hike** — as long as the
   cache-hit price survives, our bill barely moves (miss/output are minor).
2. **No alternative matches DeepSeek's cache-hit** ($0.0028–0.003625 vs
   $0.02–0.30). DeepInfra's $0.018 cache-hit is still 6× DeepSeek's.
3. The **real DeepSeek-hike risk** is the cache-hit price itself. If DeepSeek
   hikes cache-hit ~5×+, DeepInfra (same V4-Flash family, already cheaper
   miss + cache, 5-min swap) becomes the fallback. Kimi K3 is the capability
   alternative (1M ctx, official Hermes guide, AU signup); MiniMax M3 the
   cheapest cache-hit among alternatives ($0.06).
4. **Rule: quote cache-hit, cache-miss AND output whenever comparing** — a
   provider with a slightly higher miss price but 2× better cache-hit wins for
   agent work. Never rank on cache-miss alone.

## Decision Framework (as of Aug 2026)

Order of preference for high-volume agent/cron work (input/output per 1M tokens):

1. **DeepSeek v4-flash** (~$0.14/$0.28) — current default; 1M ctx. ⚠️ DeepSeek
   officially warns of a "significant increase" coming. Until the new price is
   published, keep it.
2. **GLM-4.7-FlashX** (~$0.07/$0.40, 200K ctx) — the strongest cheap-tier
   fallback if DeepSeek triples flash. Needs Z.AI API key.
3. **Qwen3.7-Flash** (~$0.07/$0.40, 1M ctx) — same price class as FlashX; usable
   via OpenRouter with existing key.
4. **GLM-4.7-Flash** — FREE tier; good for zero-cost batch/experimental work.
5. Flagship tier (GLM-5.2 $1.4/$4.4, Qwen3.8-Max, DeepSeek v4-pro $0.435/$0.87) —
   only for tasks that genuinely need the stronger model; NOT the default.

Rule of thumb: **if DeepSeek flash doubles → keep. If it triples+ → switch the
high-volume lane to GLM-4.7-FlashX / Qwen3.7-Flash.**

**Flat-rate override (Aug 2026):** the Alibaba **Token Plan (Team Edition)
Standard seat from $6/mo** changes the math — it puts DeepSeek V4
(pro/flash/v3.2) AND Qwen AND GLM-5.x AND Kimi AND MiniMax-M2.5 under ONE
credits pool with a data-privacy guarantee. If the user is willing to pay
"not a lot" for predictability, this is the strongest hedge against the
DeepSeek hike (see `references/alibaba-token-plan-2026-08.md`). Keep DeepSeek
as primary while cheap; Token Plan as the flat-rate fallback; GLM-4.7-Flash
free tier for zero-cost experiments.

## Recommended Practice on Price-Hike Warnings

When a provider announces a hike but hasn't published numbers:
1. **Don't switch yet** — compare the announced price, not the warning.
2. **Pre-stage the fallbacks** so the swap is 5 minutes: add FlashX/Qwen-flash
   to `or_free.py` Phase 3 candidates (zero risk — only used if DeepSeek fails).
3. **Set a pricing-check cron** (monthly) that fetches the provider pricing page
   and alerts when the number changes — catches the hike the moment it lands
   instead of after a surprise bill.

## Pitfalls

- **OpenRouter promo $0 prices are not durable** — verify on the provider page.
- **DeepSeek Responses API ≠ chat completions** — `deepseek-v4-flash` supports
  Responses API today; `deepseek-v4-pro` NOT until "early August 2026". The
  Responses API base_url is `https://api.deepseek.com` (bare root); chat
  completions use `.../v1/chat/completions`. Don't point a Responses-API provider
  at the /v1 path or vice versa.
- **Pricing pages change structure** — treat any single fetch as a snapshot;
  re-verify before acting on a number.
- **Context length differs per tier** — GLM FlashX is 200K, DeepSeek/Qwen flash
  are 1M. For 1M-context workloads Qwen-flash is the like-for-like fallback; for
  short-context volume FlashX wins on output price.
- **Qwen Portal is dead (verified Aug 2026)** — `portal.qwen.ai` 404s on every
  path (`/`, `/v1`, `/v1/models`, `/keys`, `/home`); `api.qwen.ai` is a Tengine
  placeholder; `qwen.ai/v1` redirects to the consumer homepage; `qwen.ai/pricing`
  and `/docs` redirect to `/home`. Official Qwen Code docs: Qwen OAuth free tier
  discontinued **2026-04-15**; the `qwen auth` CLI command was removed and OAuth
  is no longer in the `/auth` dialog. qwen.ai's "API Platform" card button opens
  `chat.qwen.ai` (consumer app) — no developer API console remains on qwen.ai.
- **qwen-code CLI `/auth` today** — Alibaba ModelStudio (Coding Plan / Token
  Plan / standard API key) → third-party API keys (DeepSeek, MiniMax, Z.AI,
  Idealab, ModelScope, OpenRouter, Requesty) → custom OpenAI/Anthropic/Gemini
  endpoint. Headless/CI can't complete the OAuth browser flow: use env vars
  (`BAILIAN_CODING_PLAN_API_KEY` + `OPENAI_BASE_URL=...`) or `~/.qwen/settings.json`.
- **Finding where JS-only buttons go** — React SPA buttons have no href; hook
  `window.open` from the browser console
  (`window.__c=[]; window.open=(u,...a)=>{window.__c.push(u);return null;}`
  then click and read `window.__c`) to resolve the target URL instead of guessing.
- **Search-engine fallback ladder** — `lite.duckduckgo.com/lite/?q=...` via curl
  (plain HTML) usually works for "is X still alive" checks; Bing HTML
  (`bing.com/search?q=`) next; both intermittently captcha curl — retry with a
  browser UA or switch engines. Good for confirming a provider/platform's
  current status before trusting stale docs.
- **read_file binary false-positive on Chinese docs** — textified CN-language
  pages (e.g. Tencent Cloud docs, mixed UTF-8 bytes) can be flagged "Binary file
  - cannot display" by read_file; re-decode + filter via python (execute_code)
  instead of fighting the detector.
- **Tencent Cloud CN docs server-render, intl is a SPA** — `cloud.tencent.com/
  document/...` is curl-friendly (use `--compressed`); `www.tencentcloud.com/...`
  returns the same ~29KB shell for EVERY path (check content, not HTTP 200).
- **CN-only real-name walls are the norm for the enterprise labs** — Tencent
  Hunyuan, Baidu Qianfan/ERNIE and iFlytek Spark LLM all require Chinese
  identity/phone; Baidu's intl cloud (`intl.cloud.baidu.com`) has zero ERNIE
  products; iFlytek's intl platform (`global.xfyun.cn`) is speech-only; Tencent's
  intl portal `hy.tencent.ai` geo-blocks ("Access Restricted"). Don't burn time
  on their JS pricing pages when the answer for AU users is already "no".
  The startups (Moonshot, MiniMax, StepFun) run proper intl platforms instead.

## Reference Files

- `references/model-pricing-2026-08.md` — the Aug 2026 pricing snapshot (DeepSeek
  hike warning, GLM/Z.AI table, Qwen tiers) used for the last decision. Load when
  answering "which model is cheapest" to see the baseline; always re-verify
  against the live pages above before acting.
- `references/multi-provider-pricing-2026-08.md` — full 11-provider sweep snapshot:
  which Chinese models each hosts (Qwen3.7/3.8-Max, DeepSeek V4 Flash/Pro,
  GLM-5.2/5.1/5, GLM-4.7-Flash), exact in/out/cached prices, context, OpenAI-compat,
  free credits, signup model. Load when a provider-level comparison is needed.
- `scripts/decode_sf_flight.py` — decodes SiliconFlow .cn pricing page (Next.js
  RSC flight data) into a model→in/out table; also documents the .com Framer
  searchIndex JSON format and the DeepInfra cents-per-token unit trap.
- `references/qwen-ecosystem-access-2026-08.md` — the non-OpenRouter /
  non-Alibaba-Cloud Qwen access map (Aug 2026): portal.qwen.ai dead, qwen-code
  CLI auth paths, Qoder plans / SDK / Cloud-Agents API, ModelScope inference
  API + model list, live endpoint probe results. Load when asked "how do we
  get Qwen API access without OpenRouter or Alibaba Cloud".
- `references/alibaba-cloud-qwen-access.md` — Alibaba Cloud account types
  (Individual vs Enterprise), sole-trader ABN eligibility, free-tier mechanics
  (per-model quota, Singapore-only, 30–90 days), AI Catalyst startup program
  (2B tokens, company required, public-listing clause), Australian gotchas,
  and Hermes provider wiring. Load when the user asks which entity/account to
  sign up with for Qwen or how to claim the free tier.
- `references/alibaba-token-plan-2026-08.md` — Alibaba Token Plan (Team
  Edition): $6/mo Standard seat, one credits pool, EXACT model allowlist
  (Qwen 3.6/3.7, DeepSeek V4 pro/flash/v3.2, Kimi K2.x, GLM-5.x, MiniMax-M2.5),
  data-privacy guarantee, seat tiers, Singapore-only. Load when asked "will
  $6/mo cover the Hermes agent" or considering the flat-rate lane.
- `references/chinese-provider-access-2026-08.md` — direct-access map for 7
  Chinese labs (Moonshot/Kimi, MiniMax, StepFun, Tencent Hunyuan, Xiaomi MiMo,
  Baidu ERNIE, iFlytek Spark): flagship + per-1M prices, AU signup without a
  Chinese phone, OpenAI-compatible endpoints, free tiers, AU caveats, and the
  Mintlify llms.txt/.md discovery pattern. Load when asked "can I use <Chinese
  lab> from Australia" or comparing the labs' own APIs.
- `references/bytedance-caching-2026-08.md` — ByteDance/Volcengine AU verdict
  (CN-only signup, NXDOMAIN intl domains, non-functional Singapore endpoint —
  do NOT recommend for AU) + the cache-hit decision framework (DeepSeek
  50–120× cache ratio is the cost driver for agent workloads; alternatives
  5–10×). Load when asked "what about caching" or "what about ByteDance".
- `references/citation-sov-engine.md` — the weekly citation share-of-voice
  engine (who-gets-named tracking across DDG/Bing + AI engines): fixed prompt
  set, vendor watchlist, curl parse patterns for DDG (`result__a`) and Bing
  (`li.b_algo`), the **anti-automation rate-limit lesson** (cookie jar + ≥10s
  polite delay + BLOCKED detection), Friday 04:05 cron + briefing wiring, and
  the not-yet-working Google/CDP path. Load when running or extending
  `pluto_citation_sov.py` or asked "who is naming us / our competitors".
