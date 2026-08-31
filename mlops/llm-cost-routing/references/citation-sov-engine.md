# Citation Share-of-Voice (SOV) Engine — who-gets-named monitoring (Aug 2026)

## What it is

Weekly automated check of **which vendors get NAMED** (AMLHive vs competitors)
for a fixed set of commercial-intent queries across search engines + AI-answer
engines. Distinct from the Wed AI-answer review (found/conflated/facts_correct
for AMLHive's own facts) — SOV tracks *citation share* including competitor
mentions. User's baseline framing: "Baseline today is zero" — the point is to
watch the 0 → 1 transition on buying-decision queries.

## Files & wiring

- Engine: `~/.hermes/scripts/pluto_citation_sov.py`
- Output: `~/.hermes/research_outputs/citation_sov/citation_sov_YYYY-MM-DD_HHMM.md` + `.json`
- Cron: `4ff9720d6a8c` — **Friday 04:05 AEST**, deliver `local`
- Briefing: `briefing_improver.py` `load_latest_research()` picks up `files['sov']`
  (latest JSON in the subdir); `format_briefing()` renders a `🏆 Citation Share-of-Voice`
  section ONLY when the file exists (Fridays). First run 2026-08-14.

## Fixed prompt set (contract-controlled)

1. "what software should a small Australian real estate agency use for AUSTRAC Tranche 2 compliance"
2. "compare AML software for Australian real estate agents"
3. "best AUSTRAC reporting compliance software Australia"
4. "real estate agent AML compliance software Australia"

## Vendor watchlist (from frontier_model_assessment.md competitors)

AMLHive, AMLTranche, AgencyAML, easyAML, Flagship AML, AML Partners, FlowAML,
AML Shield, AML Guard, ClearAML, First AML, TrustSoft, lex-aml, WatchEye,
AML Watcher, AMLHub. Tally by name in title + `*.com.au` domain catch.

## Engine mechanics (verified working Aug 2026)

| Layer | Method | Status |
|---|---|---|
| DuckDuckGo | curl `https://html.duckduckgo.com/html/?q=<query+>` → parse `class="result__a"` (real URL in `uddg=` param) | ✅ no login |
| Bing | curl `https://www.bing.com/search?q=...&count=10` → parse `<li class="b_algo"><h2><a href=...>` | ✅ no login |
| Google | curl gets JS/consent shell (h3 count 0); needs CDP browser with logged-in session | 🔜 best-effort |
| Perplexity/ChatGPT/Claude/Gemini | browser best-effort; **record BLOCKED if no session** | 🔜 best-effort |

## ⚠️ Anti-automation lesson (the critical pitfall)

Rapid repeated curl hits to DDG/Bing **trip IP-level anti-automation walls**
(DDG serves an anomaly/challenge page ~14KB with zero `result__a`; Bing serves
a captcha page with zero `b_algo`). First single test parses fine; the 2nd–4th
back-to-back query per engine gets blocked, and the cooldown lasts many minutes.

**Correct behavior (contract: never bypass walls):**
- Shared cookie jar (`curl -c jar -b jar`) so the session looks continuous
- **Polite delay ≥10s between queries** (POLITE_DELAY_S)
- `is_blocked()` markers: `captcha|unusual traffic|challenge|anomaly|access denied|robot check|before you continue` — record `BLOCKED (...)` per prompt, do not retry-hammer
- Weekly cadence (4 prompts × 2 engines, 10s spacing) is well under the wall
  threshold; the 2026-08-09 all-BLOCKED run was purely from manual testing bursts.

## Verified parse+tally output (real HTML, 2026-08-09)

For "compare AML software for Australian real estate agents":
- DDG 10 results: AMLTranche, Flagship AML, AML Partners, FlowAML, AML Shield, AML Guard named
- Bing 10 results: same vendor set
- **AMLHive: 0 across both — baseline confirmed**

## Google/AI-engine wiring (next step — not yet working)

- WSL Playwright `connectOverCDP('http://localhost:9222')` **hangs enumerating
  contexts** when the profile has 18 targets (extension background pages); new-page
  creation also times out. Known-good recipe is Windows-side PowerShell CDP
  (`/mnt/c/Users/habib/n8n-habibi-integration/scripts/test_perplexity_browser.ps1`)
  or attach to an existing page target directly.
- Google via fresh browser hits `/sorry/index` (unusual-traffic) — only a
  logged-in Google session bypasses it.
