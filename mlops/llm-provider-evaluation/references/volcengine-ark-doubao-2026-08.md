# Volcengine Ark / Doubao — verified profile (2026-08-09, from AU)

ByteDance's Doubao/Seed model API = Volcengine Ark (火山方舟). All findings
verified live this date. **Bottom line: not directly usable from Australia
— CN-only signup/payment/verification. Third-party hosts are the only
realistic lane for Doubao outside China.**

## Domain / site situation (the answer to "which domain?")

| Domain | Status (verified) | What it is |
|---|---|---|
| `volcengine.com` | LIVE (HTTP 200) | The only working site; CN-market console + docs. Signup is CN-only (see below) |
| `volces.com` | **NXDOMAIN globally** (Cloudflare + Google DoH, bare & www) | Former intl cloud brand — gone as a site |
| `volcanoengine.com` | **NXDOMAIN globally** | Never resolves |
| `doubao.com` | LIVE | Consumer Doubao chat app, NOT an API platform |
| `ark.cn-beijing.volces.com` | Resolves, **API responds** (401 w/o key) | Real OpenAI-compatible endpoint |
| `ark.ap-southeast-1.volces.com` | Resolves (Singapore ALB) but **API times out from AU** | No operational intl endpoint found |

Verification commands used:
```bash
# DoH when local DNS fails (NXDOMAIN from 2 resolvers = domain dead, not geo-block)
curl -s "https://dns.google/resolve?name=volces.com&type=A" -H "accept: application/dns-json"
# Endpoint liveness: 401 JSON = live service; timeout/000 = dead
curl -s -X POST "https://ark.cn-beijing.volces.com/api/v3/chat/completions" \
  -H "Content-Type: application/json" -d '{"model":"x","messages":[]}' -w " %{http_code}"
```

## OpenAI-compatible base URL (official, doc updated 2026-06-23)

- **Data plane (Chat + Responses API): `https://ark.cn-beijing.volces.com/api/v3`**
  — works with OpenAI SDK; Bearer API key or AK/SK signing. Doc: `https://docs.volcengine.com/docs/82379/1298459`
- Control plane (endpoints/keys mgmt): `https://ark.cn-beijing.volcengineapi.com/`
- SDK: `volcengine-python-sdk[ark]` (`Ark(base_url=..., api_key=os.getenv('ARK_API_KEY'))`); or plain OpenAI SDK pointed at the base URL.
- Coding Plan subscribers have a DIFFERENT base URL (doc 1928261) — using the wrong one incurs extra cost.

## Model lineup (verified on official 模型列表 doc 1330310)

Current/recommended:
- `doubao-seed-2-1-pro-260628` — flagship "Agent 通用模型", 256k ctx (256k in/out, 256k CoT), deep thinking + text + multimodal + tools + json_schema
- `doubao-seed-2-1-turbo-260628` — cheaper fast sibling, same 256k envelope
- `doubao-seed-evolving` — weekly-iterated coding/agent model, **1024k ctx**, RPM 500 / TPM 1M (all 2.1 models: RPM 500 / TPM 1M)
- 2.0 line: `doubao-seed-2-0-pro/lite/mini/code-preview-260215`, `2-0-lite/mini-260428` — 256k ctx (224k in / 128k out); lite/mini have audio-input pricing
- `doubao-seed-character-260628` — roleplay, 128k ctx
- Media: `doubao-seedance-2.5/2.0` (video), `doubao-seedream-5.0(-pro)` (image), `doubao-seed3d-2.0`, `doubao-embedding-vision`
- Legacy 1.5/1.6/1.8 + 1-5 lines are all marked 即将下线 (sunsetting) — don't build on them
- Platform also hosts third-party: glm-5-2-260617, deepseek-v4-pro/flash(-ga) etc.

## Pricing — regular online inference, RMB per 1M tokens (doc 1544106; USD ≈ ÷7.15)

| Model | Input | Output | Cache-hit |
|---|---|---|---|
| doubao-seed-2.1-pro | ¥6.00 (~$0.84) | ¥30.00 (~$4.20) | ¥1.20 |
| doubao-seed-evolving | ¥6.00 | ¥30.00 | ¥1.20 |
| doubao-seed-2.1-turbo | ¥3.00 | ¥15.00 | ¥0.60 |
| doubao-seed-2.0-pro / 2.0-code | ¥3.20–9.60 (by input len) | ¥16–48 | ¥0.64–1.92 |
| doubao-seed-2.0-lite | ¥0.60–1.80 | ¥3.60–10.80 | ¥0.12–0.36 |
| **doubao-seed-2.0-mini (cheapest)** | **¥0.20–0.80** | **¥2.00–8.00** | ¥0.04–0.16 |

Cache storage ¥0.017/M tokens/hour. Separate tables: 低延迟 (low-latency) ≈2–3×; 批量 (batch) ≈0.5×. All billing RMB — no USD/AUD billing lane found.

## Signup requirements (verified on live form, console.volcengine.com/auth/signup)

- Both tabs (手机号注册 / 账号注册) hard-code **+86 Chinese mobile** — no country-code selector, no email-only path.
- Payment RMB (Alipay/WeChat/CN bank). Free-quota exhaustion → requires **实名认证 (CN real-name verification)** + manual model activation.
- Conclusion: a non-China user cannot self-service sign up or pay. No bypass verified.

## Free tier / trial

- Official 免费推理额度 (doc 1399514): new accounts get per-model token grants (e.g. seed3d 2M tokens); shared across master account; offsets only pay-per-token online inference (NOT plugins, KB, batch, or cache-storage fees).
- Gated behind the CN-only registration → effectively unavailable to AU users.

## AU latency (measured from AU host, 3 runs each)

- `ark.cn-beijing.volces.com`: TCP ~0.34–0.44s, TLS ~0.66–0.78s, **TTFB ~0.98–1.11s** (~1s added per API round-trip)
- `api.deepseek.com` (reference): TTFB ~0.21s
- No official AU/Singapore latency docs; no working non-CN endpoint observed.

## Volcengine docs scraping recipe (reusable)

`docs.volcengine.com` is a JS SPA but **some pages embed full content server-side**:
1. `curl -sL "https://docs.volcengine.com/docs/82379/<DOCID>?lang=zh"` → if page contains `window._ROUTER_DATA = {...}` (page size 10KB–1MB), everything is in that JSON:
   - Article body = `loaderData["docs/(libid)/(docid$)/page"]["curDoc"]["Content"]` — a JSON **string** `{"version":"0.4.16","data":{"0":{"ops":[Quill ops]}}}` → `json.loads` twice, join `op["insert"]` strings.
   - Nav tree / doc discovery = `loaderData["docs/(libid)/layout"]["docListMap"]` — `docID -> {value:{Title}}`, lets you find sibling docs (e.g. 模型价格=1544106, 免费推理额度=1399514) and the `"747"` root gives the tree.
2. Pages returning the **9819-byte shell with no `_ROUTER_DATA`** are client-rendered → use `browser_navigate`, then extract tables with
   `browser_console` JS: `[...document.querySelectorAll('table')].map(t => [...t.querySelectorAll('tr')].map(r => [...r.querySelectorAll('td,th')].map(c => c.innerText)))`.
3. Key doc IDs (library 82379, Ark): 模型列表 1330310 · 模型价格 1544106 · Base URL及鉴权 1298459 · 快速入门 1399008 · 模型服务计费说明 1544681 · 免费推理额度 1399514 · 订阅(Agent/Coding Plan) 1928261
