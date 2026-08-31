# Qwen (QAN) Developer Ecosystem Access Map — Aug 2026

Live probe results + official-doc findings for Qwen API access channels that are
NOT OpenRouter and NOT Alibaba Cloud direct. All URLs/statuses verified by curl /
browser on 2026-08-09.

## Endpoint status at a glance (curl-verified)

| Endpoint | Status | Notes |
|---|---|---|
| `https://portal.qwen.ai` (+ `/v1`, `/v1/models`, `/api/v1`, `/keys`, `/home`) | **404 all paths** | Platform dead |
| `https://api.qwen.ai/` | HTTP 200 but Tengine placeholder ("Hello Tengine on TLS"); `/v1/models` → 404 | Not a real API |
| `https://qwen.ai/v1`, `/pricing`, `/docs`, `/keys`, `/portal` | Redirect → `qwen.ai/home` | Consumer-only site |
| `https://chat.qwen.ai` | Live | Qwen Studio consumer chat (free) |
| `https://api.qoder.com/api/v1/cloud` + `/api/v1/forward` | Live (Beta) | Qoder Cloud Agents API, Bearer PAT |
| `https://api-inference.modelscope.cn/v1` | Live, OpenAI-compatible | 43 models, 22 Qwen open models |
| `https://modelscope.com` | Redirect → `modelscope.cn/?lang=en_US` | No separate intl domain |
| `https://coding-intl.dashscope.aliyuncs.com/v1` | Live | Alibaba Coding Plan intl endpoint (Alibaba Cloud, listed for completeness) |

## 1. Qwen Portal (portal.qwen.ai) — DEAD

- What it was: Qwen's official OAuth developer API. OpenAI-compatible base URL
  `https://portal.qwen.ai/v1` (older docs: `/api/v1`). Device-code OAuth login,
  ~2,000 free requests/day, tokens auto-refreshed. Third-party agent tools
  (OpenClaw/claw) consumed it as the `qwen-portal` provider and reused Qwen Code
  CLI creds from `~/.qwen/oauth_creds.json`.
- Death: root + every path 404 as of Aug 2026. Official qwen-code docs:
  *"The Qwen OAuth free tier was discontinued on 2026-04-15. Existing cached
  tokens may continue working briefly, but new requests will be rejected.
  Please switch to Alibaba Cloud Coding Plan, OpenRouter, Fireworks AI, or
  another provider."*
- qwen.ai homepage still shows an "API Platform" card ("Qwen API, OpenAI-API
  compatible") — its Use Now button opens `chat.qwen.ai` (consumer app), i.e.
  the card is stale/broken. Do not route new work here.

## 2. Qwen Code CLI (qwen-code) — auth flow today

- Install: `curl -fsSL https://qwen-code-assets.oss-cn-hangzhou.aliyuncs.com/installation/install-qwen-standalone.sh | bash`
  (Windows: `irm ...install-qwen-standalone.ps1 | iex`; or `npm i -g @qwen-code/qwen-code`, `brew install qwen-code`). Run `qwen`, then `/auth`.
- **Qwen OAuth is no longer a selectable option** (removed with the free tier).
  Current `/auth` menu:
  1. **Alibaba ModelStudio** (official recommended): Coding Plan (individuals,
     fixed monthly fee, weekly quota, dedicated endpoint), Token Plan (teams,
     usage-based, dedicated endpoint), or standard API key.
  2. **Third-party providers** (API key): DeepSeek, MiniMax, Z.AI, Idealab,
     ModelScope, OpenRouter, Requesty.
  3. **Custom provider**: any OpenAI/Anthropic/Gemini/Qwen-compatible endpoint.
- Headless/CI cannot complete the OAuth browser flow. Use instead:
  `export BAILIAN_CODING_PLAN_API_KEY=...` +
  `export OPENAI_BASE_URL=https://coding-intl.dashscope.aliyuncs.com/v1` +
  `export OPENAI_MODEL=qwen3-coder-plus`, or write `~/.qwen/settings.json`
  (`modelProviders.openai[].baseUrl` + `env.BAILIAN_CODING_PLAN_API_KEY`).
- The `qwen auth` CLI subcommand was removed.
- Coding Plan model roster (from docs): qwen3.5-plus, qwen3.6-plus, qwen3.7-plus,
  qwen3-coder-plus, qwen3-coder-next, qwen3-max-2026-01-23, plus third-party
  models (glm-5, glm-4.7, kimi-k2.5, MiniMax-M2.5).

## 3. Qoder (qoder.com) — Qwen's agentic coding platform

Operator: Bright Zenith Private Limited (footer on qoder.com); China site
qoder.com.cn. Qwen3.8-Max (2.4T params) launched there Aug 3, 2026. Served 5M+
users at first anniversary.

- **Plans (Individual)**: Free $0 — 2-week Pro trial with 300 credits, limited
  completions/next-edits, BYOK allowed. Pro $20/mo = 2,000 credits/mo. Pro+
  $60/mo = 6,000. Ultra $200/mo = 20,000. Add-on credit pack $20 / 1,500 credits
  (valid 1 month). Credits reset monthly; when exhausted, falls back to
  "basic models" with limited messages. Teams/Enterprise: SSO, role/group mgmt,
  cost centers, richer APIs.
- **Credit consumption guidance** (median): Editor Ask ~3–4/request, Editor
  Agent ~7–12, Quest Agent ~50, Quest Experts ~75, Repo Wiki ~50/repo. Failed
  calls don't deduct.
- **API access — two programmatic surfaces** (no per-token prices published):
  - **Agent SDK**: `npm i @qoder-ai/qoder-agent-sdk` / `pip install qoder-agent-sdk`.
    Auth: PAT (`pt-...`) from `qoder.com/account/integrations` (shown once) or
    org Service Account key; env `QODER_PERSONAL_ACCESS_TOKEN`. Fixed or dynamic
    model selection; BYOK per-request supported; multi-turn, streaming, MCP,
    subagents, permissions, hooks.
  - **Cloud Agents API** (Beta, REST): `https://api.qoder.com/api/v1/cloud`
    (managed) and `/api/v1/forward` (IM-channel forward mode). Header
    `Authorization: Bearer pt-...`. Agents/environments/sessions/SSE
    events/files/vaults/skills/memory/deployments/schedules. Body limit 4 MB.
    Billing: model calls → credits; sandbox runtime metered per-second from
    2026-08-10; storage currently free.
- **Promos (Aug–Sep 2026)**: 800 free Qwen3.8-Max calls for new/paid users
  (claim in-app, one per user; +2,000 if ordering during event Aug 3–Sep 3).
  Off-peak (14:00–00:00 UTC) credit multiplier: Qwen3.8-Max 0.25x (50% off),
  Qwen3.7-Max 0.1x (80% off), Qwen3.7-Plus 0.04x.
- Docs: `docs.qoder.com` — `https://docs.qoder.com/llms.txt` is a full clean
  index; every page has a `.md` twin (`.../cli/sdk/quick-start.md`).

## 4. ModelScope (modelscope.cn) — hosted inference

- **Hosted OpenAI-compatible inference API is live**: `https://api-inference.modelscope.cn/v1`
  (GET `/v1/models` returns the served catalog). 43 models, including **22 Qwen
  open-source models**: Qwen3-4B/8B/14B, Qwen3-30B-A3B(+Thinking), Qwen3-235B-A22B
  (+Instruct/Thinking-2507), Qwen3-Next-80B-A3B(+Thinking), Qwen3-Coder-30B-A3B,
  Qwen3.5-27B/35B-A3B/122B-A10B/397B-A17B, Qwen3-VL-8B/235B, Qwen-Image-Edit, etc.
  NOT the flagship proprietary qwen3.8-max.
- International: `modelscope.com` → redirects to `modelscope.cn/?lang=en_US`
  (English UI, China-hosted, Alibaba infra). No separate global domain.
- Signup: free registration (phone/Alibaba login); free cloud Notebooks (CPU/GPU)
  and free online demos for registered users.
- **Pricing: no public per-1M-token list found.** Model Service docs cover
  SwingDeploy (deploy any model as OpenAI-API-compatible cloud service, one-click
  or local). Docs are JS-rendered SPA; `modelscope.cn/docs/...*.md` URLs return
  the HTML shell too. Treat as "registration required; prices in console".
- Also exposed as a built-in third-party provider inside qwen-code CLI `/auth`.

## Techniques that worked (repeatable)

- **Docs discovery**: fetch `https://<vendor>.com/docs/llms.txt` with
  `curl --compressed` (gzipped) — Mintlify/Nextra-style sites (Qoder) return a
  full page index; per-page `.md` twins render clean markdown. Custom SPAs
  (ModelScope) return shells — browser needed.
- **Resolving JS-only buttons**: hook `window.open` from the browser console,
  click, read the capture — resolved qwen.ai's "API Platform" card → chat.qwen.ai.
- **Search for "is X still alive"**: `lite.duckduckgo.com/lite/?q="portal.qwen.ai"`
  via curl returned history (OpenClaw provider docs, Medium guides) proving the
  platform's former shape; Bing HTML as fallback; both intermittently captcha.
- **Endpoint triage**: `curl -sL -o /dev/null -w "HTTP %{http_code} | %{url_effective}"`
  over candidate URLs distinguishes live endpoints from redirects and dead hosts
  in one pass (found `api.qwen.ai` placeholder vs real 404s).

## Unresolved / needs signup to verify

- ModelScope per-token prices and free quotas (console-only).
- Qoder per-token equivalents (credit model only; no $/1M published).
- Whether Qoder Cloud Agents API works outside Qoder apps / standalone agents
  (Beta; PAT-based, so likely yes).
