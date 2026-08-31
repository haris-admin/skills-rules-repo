---
name: weekly-ai-brief
description: Weekly AI brief - releases, security, policy.
---

# Weekly AI Brief (Mercury cron, Mon ~7AM AEST)

Compile a 2-minute digest for Telegram: agentic AI releases (Google/OpenAI/Anthropic/Meta), AI security incidents (sandbox-escape follow-ups, prompt injection), policy (EU AI Act, ISO 42001, AU AI policy / Office of AI).

## Search set (run in parallel, then verify)

1. `Google agentic AI release <month> <year>` — also check developers.googleblog.com (ADK/zero-trust)
2. `OpenAI Anthropic agent new release <month> <year>` — releasebot.io/updates/openai + /anthropic give dated changelogs
3. `Meta AI agent Llama release <month> <year>` — Muse line (Muse Spark/Muse Glimmer) under Meta Superintelligence Labs
4. `AI sandbox escape <month> <year>` / `prompt injection <month> <year>` — AISI incident report follow-ups, Irregular misconfig ripple, Adversa/Varonis research
5. `EU AI Act news <month> <year>` — watch enforcement dates (Art 50 transparency, Digital Omnibus deferrals)
6. `ISO 42001 <month> <year>` — new certifications (KuCoin, banks, exchanges)
7. `Australia Office of AI news <month> <year>` — PM&C Office of AI, Australian AI Standards (Parliament early 2027), Senate AI census

## Digestion rules

- **Date everything** — "w/e <date>" header. Only surface items from the last ~7 days as new; older items (e.g. GPT-5.6 GA, Office of AI launch) as context/background lines.
- **Security section is the lead story** — agent incidents (AISI/OpenAI/HF/Anthropic/Meta/Kimi K3) and prompt injection research are what Haris cares about. Include exact numbers (runs, actions, CVEs, dates) — he verifies claims.
- **Policy: EU = enforcement dates + fines; AU = Office of AI milestones + federal adoption numbers; ISO = named certifiers.**
- Tie back to AML Hive angle: evidence pack / audit trail / ISO 42001 / watermarking ("AI decision record, inspection-ready").

## Output format (Telegram-ready)

- Header: `☿ WEEKLY AI BRIEF — w/e <date>`
- Sections: 🚀 RELEASES / 🛡️ SECURITY / ⚖️ POLICY / 💡 TAKEAWAY
- Bullets ≤2 lines each, bold lab names + model names, emoji sparingly
- 400–520 words total, plain markdown (no tables), ends with 2-3 line takeaway

## Pitfalls

- Releasebot feeds can surface items days late — verify dates at original source (blog.google, openai.com/index, anthropic.com/news, research.meta.ai).
- Don't conflate the incidents: AISI eval (agents given internet + classifiers off) ≠ OpenAI/HF zero-day sandbox escape ≠ Irregular misconfig (Anthropic/Meta) — different failure modes, all August 2026.
- Australian timezone: EU/US articles are dated one day earlier in AEST terms.
- If a search returns nothing new in a section, keep the section but say "no major movement" — do not pad.
