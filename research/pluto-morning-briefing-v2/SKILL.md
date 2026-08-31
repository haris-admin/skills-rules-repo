---
name: pluto-morning-briefing-v2
description: Pluto's redesigned morning briefing — action-first, scannable, self-improving. Uses briefing_improver.py engine. The "Option C" briefing that wows.
allowed-tools: [terminal, file, read_file, write_file]
---

# Pluto Morning Briefing v2 — The "Wow" Briefing

## Design Principles

### 🔈 Voiceover Requirement (June 2026)

Every major response to Haris must include a TTS voiceover alongside the text. This includes:
- Weekly recommendations (Saturday review build options)
- Build proposals (e.g., AgentRed AU)
- Pipeline fixes or changes (e.g., cron fixes, API integrations)
- Any response that would be >3 lines of text

Use `text_to_speech()` and include the resulting `MEDIA:` path in the response. The voice is OpenAI Nova (gpt-4o-mini-tts), female voice. Haris confirmed (June 9): "Voice is our major medium." Voice + text together because "technical terms don't work with voice only."

**Exception:** Brief routine status checks (<3 lines), simple confirmations, or back-and-forth clarifications don't need voiceover. Use judgment — if it's a decision-point or recommendation, voice it.

## Design Principles

Derived from Haris's observed patterns (Honcho, June 2026):

1. **Action-first** — Lead with what he needs to DO today. Not what happened.
2. **Portfolio heatmap** — Instant project scan: HOT / WARM / QUIET
3. **Checklist format** — He gravitates toward checklists as lead magnets
4. **One surprise** — "Didn't Know That" section — a cross-signal insight
5. **Self-improving** — Every briefing asks one question about the briefing itself
6. **60-second scan** — Max 120 lines, no tables, no walls of text
7. **Color-coded triage** — 🔴 Critical / 🟡 Severe / 🟢 Opportunity (already his system)
8. **Voice + text together** — Haris confirmed (June 9): "Voice is our major medium" but "we have lots of technical terms so voice only doesn't work that well." Deliver both simultaneously. TTS: OpenAI Nova voice. See `references/tts-voice-migration.md`.
9. **Three-source mandate (June 16, 2026)** — Every briefing MUST draw from all 3 sources: **Gmail/Perplexity** (email signals), **YouTube/podcast** (worldview), and **Pluto's own web research** (market pulse). No one source should substitute for another. Before delivery, verify all 3 contributed. If one is missing (e.g., Gmail ingestor broken, pipeline skipped), note the gap in the briefing so Haris knows the data provenance.
10. **Data freshness (June 16, 2026)** — Recycled signals from 3+ days ago make the briefing feel stale. If the same topics appear for 3+ consecutive days, either find new angles, deeper analysis, or flag the repetition openly: "Same signal as Tuesday — no new developments."
11. **Cross-validation (June 16, 2026)** — On high-impact findings (competitor moves, regulatory deadlines, credential issues), involve other agents (Gumby/Brainy/Gumby GC) to double-check before surfacing as ACTION items. Briefings should note when a finding was cross-validated and by whom.

## Engine

**Script:** `~/.hermes/scripts/briefing_improver.py`

**Podcast Insights:** `~/.hermes/research_outputs/podcast_insights.json`
**Competitor Intel:** `~/.hermes/scripts/competitor_intel.py`
**Competitor Database:** `~/.hermes/data/competitors.json`

```
briefing_improver.py [--dry-run] [--feedback "A"]
competitor_intel.py [--date YYYY-MM-DD]
```

### What It Does

1. Reads today's research outputs from the morning pipeline (4 sources — see Signal Sources below)
2. Loads podcast insights from `podcast_insights.json` — episodes with AU relevance ≥ 0.15 and portfolio connections become signals with `source: 'podcast'`
3. Loads competitor intel (if available — from competitor_intel.py)
4. Extracts regulatory signals and scores portfolio impact
5. Generates a heatmap showing which projects are HOT/WARM/QUIET
6. Creates an action checklist sorted by priority
7. Generates a dedicated 🎧 Podcast Insights section (reads directly from file, independent of signal cap)
8. Adds competitor watch section for HOT/WARM projects (when intel exists)
9. Generates ONE surprising cross-signal insight
10. Asks one improvement question for tomorrow
11. Saves to `research_outputs/morning-briefing-YYYY-MM-DD.md`
12. Tracks 30-day improvement history

### Signal Sources (4 sources — podcast added June 12)

The briefing engine reads from four sources:

| Priority | Source | File Pattern | What It Provides |
|----------|--------|-------------|------------------|
| 1 | Research | `research_YYYY-MM-DD.json` | Primary findings with portfolio_hit/impact fields |
| 2 | Synthesis | `synthesis_YYYY-MM-DD.json` | Cross-domain patterns, chamber stats |
| 3 | Actions | `actions_YYYY-MM-DD.json` | Concrete action items from Action Bridge |
| 4 | Podcast | `podcast_insights.json` | Recent episode insights with AU relevance ≥ 0.15 AND portfolio connections |

Signals are sorted by impact (critical > severe > medium) and capped at **7** (increased from 5 on June 12 to accommodate podcast signals). If Research is sparse, Synthesis, Actions, and Podcast fill the gap. The podcast section is generated directly from the file (not from the truncated signals list), so it always shows the top relevant episodes regardless of the signal cap.

**Project name mapping:** 
- Synthesis: domains (`AI Regulation`, `RegTech`) via `_map_domains_to_projects()`
- Actions: internal names (`RegStack`, `AgentSRE`) via `_map_action_project()`
- **Podcast:** portfolio connection strings (e.g. `FinAI/AI-gov`) via `_map_podcast_connections()` shared helper
- All map to portfolio names (`AML Hive`, `PayLicence AU`, `FinAI File AU`, etc.)

## Briefing Format

```
🌅 Weekday — DD Month YYYY

📡 Portfolio Pulse
🔥 HOT: projects with critical signals
🌤  WARM: projects with medium signals
❄️  QUIET: no signals today

🔴/🟡 TODAY: The single most important thing

✅ Your 3-Minute Checklist
- [ ] 🔴 Project: Action item
- [ ] 🟡 Project: Action item

📡 Today's Signals (condensed, 2 lines each)

🎧 Podcast Insights (NEW June 12 — top 3 episodes with portfolio connections)
- 🎙 Show: Episode Title
  → Project (portfolio mapping)
  _Key theme summary_

👀 Competitor Watch (OPTIONAL — only when competitor moves detected for HOT/WARM projects)
🔥 CompetitorName (PortfolioProject): 💰 🚀
   snippet of what they did...

💡 Didn't Know That (one surprising insight)

🔧 Make Tomorrow Better (one improvement question)
```

### Briefing Configuration (June 12)

- **MAX_SIGNALS** = 7 (was 5 — increased to accommodate podcast + research + synthesis + actions)
- **MAX_BRIEFING_LINES** = 140 (was 120 — increased for podcast section)
- Podcast section reads directly from `podcast_insights.json`, NOT from the truncated signals list — so even if research signals fill all 7 slots, podcast episodes still appear
- Competitor section only appears when intel exists for HOT/WARM projects

## Anti-Patterns (from old format)

- ❌ 190-line walls of text
- ❌ Tables (portfolio impact matrix, timeline, delivery log)
- ❌ Actions buried at line 167
- ❌ 5 equal-weight signals at the top
- ❌ LinkedIn posts + blog ideas in the briefing body
- ❌ No feedback loop — sent and forgotten
- ❌ One-size-fits-all format every day

## Improvement Engine

7 improvement questions rotate daily:

1. Actions at the VERY top (line 1)?
2. 3 deeper signals vs 5 surface?
3. Voice-first briefing?
4. One project deep-dive per day?
5. Competitor intel section?
6. Surprise section actually surprising?
7. [RESOLVED June 13 — Saturday handled by weekly review cron, not format toggle]

Each question has A/B/C choices. Haris replies with a letter — the engine adapts.

### Question #7 — RESOLVED (June 13, 2026)

Question #7 (weekend format) was answered: Saturdays now get a deep weekly review via `7d24b37a03f2` instead of a different briefing format. The question is removed from the active rotation but the code remains for reference. See "Weekend Variant" section above for the resolution.

## Wiring into Pipeline

The morning briefing is generated by a dedicated cron job (`7cc81d64613a`, 5:20 AM AEST) that runs `briefing_improver.py` independently of upstream job success. It consumes all available pipeline outputs and produces the final formatted briefing.

### Pipeline (all times AEST — June 13, 2026: All internal except 6:00 AM consolidated briefing + Sat 6AM weekly review)

```
4:55 AM Gmail Ingestor        → mempalace-inputs/gmail-briefing-*.md        local
5:02 AM Podcast Insights      → research_outputs/podcast_insights.json       local
5:05 AM Morning Research      → research_outputs/research_YYYY-MM-DD.json    local
5:05 AM Vercel Monitor        → alert via email                              local
5:07 AM Competitor Intel      → research_outputs/competitor_intel_*.json     local
5:10 AM Cross-Chamber Synth   → research_outputs/synthesis_YYYY-MM-DD.json   local
5:15 AM Action Bridge         → research_outputs/actions_YYYY-MM-DD.json     local
5:20 AM Briefing Improver     → research_outputs/morning-briefing-*.md       local (saves file)
5:25 AM Chamber Refresh       → feeds ChromaDB chambers                      local
6:00 AM ★ Briefing (Mon-Fri) → text briefing + voice audio                  origin (THE ONE)
5:30 AM Honcho Signal Bridge  → Honcho signals                              local
6:10 AM Feedback Loop         → research_outputs/feedback/                   local
6:15 AM Moonshots Learning    → podcast-teach concept                        local
6:45 AM LinkedIn Ideas        → content generation                           local
```

**Friday SOV slot (Aug 2026):** `4ff9720d6a8c` runs `pluto_citation_sov.py` at **04:05 Friday** → writes `research_outputs/citation_sov/citation_sov_*.md` + `.json`. The 5:20 Briefing Improver loads the latest SOV JSON (`files['sov']`) and renders a **🏆 Citation Share-of-Voice** section (AMLHive named YES/NO per engine + top other vendors named). Only appears on Fridays when the SOV file exists.

**Cron details:**
- `7cc81d64613a` — Pluto Briefing Improver (5:20 AM AEST), `no_agent: true`, script: `briefing_improver.py`, `deliver: local`
- `c527fed4a1da` — ★ Pluto Morning Briefing (6:00 AM **Mon-Fri**), `deliver: origin`. Reads the briefing file + podcast insights, generates voice audio, delivers ALL content + audio in one message. This is the only Telegram delivery in the morning on weekdays.
- `7d24b37a03f2` — ★ Pluto Saturday Weekly Review (6:00 AM **Sat only**), `deliver: origin`. Deep weekly retrospective covering performance, repo health, signals, 3 build options, and improvements. Replaces the daily briefing on Saturdays. Loads `pluto-portfolio-ideation` + `fleet-intelligence` skills.

## Saturday Weekly Review (supersedes Weekend Variant)

### Running the improver

```bash
cd ~/.hermes
python3 scripts/briefing_improver.py
```

For dry-run (preview without saving):
```bash
python3 scripts/briefing_improver.py --dry-run
```

## Feedback Processing

The `--feedback` flag is now implemented:
```bash
python3 scripts/briefing_improver.py --feedback "A"
```
- Accepts A, B, or C
- A or B = applied as improvement
- C = noted but no change (Other)
- Tracks streak in `.briefing_improvements.json`
- Records all responses in `.briefing_feedback.json`

## Portfolio Mapping

Research findings need `portfolio_hit` and `impact` fields for the briefing engine. The autonomous research pipeline produces findings with `type` (threat/opportunity/trend) — these must be mapped to portfolio projects before the briefing improver runs. The enriched file is saved as `.research_enriched_latest.json`.

## Weekend Briefing Format (June 13, 2026)

The daily briefing runs **Mon-Fri only** (`c527fed4a1da`, `0 6 * * 1-5`). Weekends get dedicated formats via separate crons:

### Saturday 6:00 AM — ★ Weekly Review

**Cron:** `7d24b37a03f2` | **Model:** deepseek-v4-pro | **Skills:** pluto-portfolio-ideation, fleet-intelligence

The Saturday Weekly Review is a **deep retrospective** — not a lighter briefing. It replaces the daily briefing on Saturdays entirely.

**Data sources:**
| Source | Location | What It Provides |
|--------|----------|------------------|
| Performance Tracker | `~/.hermes/research_outputs/.performance_tracker/{week_id}.json` | Daily cron health snapshots, error counts, output volumes |
| Cron State DB | `~/.hermes/cron/state.db` | Job statuses, last run times |
| Research Outputs | `~/.hermes/research_outputs/synthesis_*.md` | Weekly signals, cross-domain patterns |
| Actions | `~/.hermes/research_outputs/actions_*.json` | Action items generated |
| Repo Audit | `/mnt/c/Code/gitlab/` | Git repo health, dirty status, recent commits |
| Errors Log | `~/.hermes/logs/errors.log` | Broken pipe, 401, stale stream patterns |

**Sections produced:**
1. **📊 Week in Review** — performance summary from tracker data
2. **🔍 Repo Health** — system repository audit (all git repos)
3. **💡 Signals This Week** — emerging themes from synthesis + competitor intel + research
4. **🚀 Three Build Options** — scored using Gumby 1000-point assessment + Ideas→Development pipeline
5. **🔧 Improvements** — ranked priorities for the next week

**Format principle:** Comprehensive but scannable. ~30-50 lines on Telegram. "Same format as daily, deeper content."

### Sunday 6:00 AM — Adversarial + Portfolio Pulse (LIVE June 14)

**Cron:** `f8756a2b8403` | **Model:** deepseek-v4-pro | **Skills:** fleet-intelligence | **Deliver:** origin (Telegram)

A forward-looking format with two halves:

**Part A — Adversarial Blind Spots:** Challenges the dominant narrative of the week. Blind spot scan (what's overrepresented vs missing), counter-narrative (best case for the opposing view), one non-obvious take.

**Part B — Portfolio Pulse:** Deep-dive on one project (rotates weekly: AML Hive → ExitLens → TokenPilot → PayLicence → FinAI File → CloudProof). Project health check from Vercel/error data, signal-to-project impact map, and one recommendation (pivot/pause/accelerate/kill).

The user confirmed this format on June 13: "A + C combined."

## Pitfalls

- **Research files must exist before running.** The improver reads from `research_outputs/` — if no research ran, the briefing will be sparse (which is correct — quiet days should produce short briefings).
- **Synthesis file naming mismatch (fixed June 9).** `load_latest_research()` previously globbed for `cross_chamber_synthesis_*.json` but the Cross-Chamber Synth cron produces `synthesis_YYYY-MM-DD.json`. Both patterns are now matched. **If you edit the synths cron, keep the filename convention in sync.**
- **Signal extraction was research-only (fixed June 9).** `extract_regulatory_signals()` originally only read from `research_YYYY-MM-DD.json`. It now reads from four sources: research (primary), podcast (enrichment), synthesis (cross-domain patterns), and actions (concrete action items). **If you add new pipeline outputs, wire them into `load_latest_research()` AND `extract_regulatory_signals()`.**
- **Podcast signals compete for the 7-slot cap.** Research signals (all 'critical') usually fill the cap first, pushing podcast signals ('severe'/'medium') out of Today's Signals. The dedicated 🎧 Podcast Insights section reads directly from the file and always shows top episodes. **If you change MAX_SIGNALS, verify the Podcast Insights section still renders** (it reads from the file, not from the signals list, so it's independently robust).\n- **Podcast section requires `files_available` parameter.** `format_briefing()` accepts an 8th parameter `files_available` (the dict from `load_latest_research()`). The Podcast Insights section reads podcast_insights.json FROM this dict. If you call `format_briefing()` without `files_available`, the podcast section silently disappears. Always pass `files=load_latest_research()` as the 8th argument.
- **Podcast portfolio mapping is keyword-based and format-aware.** The `_map_podcast_connections()` helper handles both legacy string format (`"FinAI/AI-gov - description"`) and new dict format (`{"project": "FinAI / AI-Gov", "rationale": "...", "episode": "..."}`) via isinstance() checks. The podcast insight extractor (cron 67319a9b2606) switched to dict format circa June 2026. If the extractor changes format again, update both the inline code in `extract_regulatory_signals()` AND the shared `_map_podcast_connections()` helper. They should always agree on the expected format — if they diverge, the Podcast Insights section and the signal path will disagree on which projects are hit.
- **Competitor snippets can be raw JSON (fixed June 9).** Competitor intel's `snippet` field sometimes contains podcast metadata JSON instead of human-readable news text. The `generate_competitor_section()` now detects JSON (starts with `{` or `[`) and falls back to displaying signal type names instead. Long-term fix: improve `competitor_intel.py` snippet extraction.
- **Action Bridge project names differ from portfolio names.** The Action Bridge uses internal names like `RegStack`, `AgentSRE` while the briefing engine maps to `AML Hive`/`PayLicence AU`/`FinAI File AU` etc. The `_map_action_project()` helper handles this. If new project names appear in action bridge output, update the mapping.
- **Recovery path when Morning Research fails:** If `research_YYYY-MM-DD.json` is missing, the podcast + synthesis + competitor intel + action bridge outputs provide enough signal for a useful briefing. Run `briefing_improver.py --dry-run` first to preview, then without `--dry-run` to save and deliver. The briefing will note the lighter signal day. See `references/recovery-procedure.md`.
- **Cron delivery requires briefing in stdout (fixed June 9).** `briefing_improver.py` now prints the full briefing after saving, not just a status line. The `no_agent` script cron delivers stdout. If you modify main(), keep the `print(briefing)` at the end.
- **Voice overview is text-to-speech.** Uses OpenAI TTS Nova voice. See `references/tts-voice-migration.md` for voice config, cost, and alternatives. TTS is generated inline during the 6:00 AM morning briefing (`c527fed4a1da`) — delivers both the MP3 and a 1-sentence summary via Telegram.
- **The improvement question is the feedback mechanism.** Haris replies with a letter. Pluto processes it and adjusts tomorrow's briefing. Don't skip this.
- **Checklist items are generated from signals.** If no signals hit Haris's projects, the checklist section won't appear — that's intentional. "Nothing to do today" is a valid briefing.
- **The engine tracks history.** `~/.hermes/research_outputs/.briefing_improvements.json` contains the 30-day log. Don't delete it.
- **Competitor section is conditional.** The 👀 Competitor Watch section only appears when `competitor_intel.py` finds relevant competitor moves for HOT or WARM projects. Empty competitor intel → no section. Cold-project-only intel → no section. This prevents noise.
- **⚠️ Competitor intel has a known false-positive problem.** Single-word name tokens ("aml", "financial", "change", "intelligence") in `competitor_intel.py` trigger hits on generic content, and funding/acquisition/launch regex patterns fire on the same text. If a competitor shows all three signals (💰🏢🚀) simultaneously, verify before treating as real. See `fleet-intelligence` skill → `references/competitor-signal-verification.md` for the full verification procedure and signal confidence tiers.

## Podcast Data Flow (Added June 12)

### Flow

```
podcast_insights.json (9-15 episodes, scored by au_relevance)
        ↓
briefing_improver.py
  ├── extract_regulatory_signals() → podcast signals (source='podcast')
  │     Uses _map_podcast_connections() helper shared with format_briefing
  │     Episodes with score ≥ 0.15 AND portfolio connections become signals
  │     Impact: 'severe' (score ≥ 0.45) or 'medium' (score 0.15–0.44)
  │     NOTE: These compete with research signals for the 7-slot cap
  │
  └── format_briefing()
        → 🎧 Podcast Insights section (reads podcast file DIRECTLY, bypasses signal cap)
        → Always shows top 3 episodes with portfolio mapping + key theme + YouTube link

Portfolio mapping logic (_map_podcast_connections):
  Connections can be in TWO formats (function handles both via isinstance() checks):
  - NEW (June 2026): dicts with 'project', 'rationale', 'episode' keys
    e.g. {"project": "FinAI / AI-Gov", "rationale": "Policy reform...", "episode": "..."}
  - LEGACY: connection strings like "FinAI/AI-gov - description"
  Mapping via keyword matching on project field/string: FinAI→FinAI File AU, ExitLens→ExitLens AU, etc.
  See source in briefing_improver.py `_map_podcast_connections()` function.
  ⚠️ The podcast insight extractor (cron 67319a9b2606) switched from string to dict format for
  portfolio_connections circa June 2026. The briefing improver was patched June 26 to handle both.
```

### Why Two Paths?

1. **Signal path** — podcast episodes appear in Today's Signals when research is sparse (they're in the capped list)
2. **Dedicated section** — always visible regardless of signal cap, so podcast insights are never lost

This means on heavy research days, podcast episodes may not make the 7-signal cut (all slots filled by critical research findings), but they'll ALWAYS appear in the 🎧 Podcast Insights section.

### Data Flow

```
competitors.json (21 competitors, 7 categories)
        ↓
competitor_intel.py (regex-based signal extraction)
        ↓
competitor_intel_YYYY-MM-DD.json
        ↓
briefing_improver.py (filters to HOT/WARM projects)
        ↓
👀 Competitor Watch section (briefing)
```

### Competitor Database

`~/.hermes/data/competitors.json` tracks 21 competitors across 7 project categories:
- **ExitLens AU:** Cake Equity, Orchestra, Pulley
- **AML Hive:** Arctic Intelligence, First AML, Napier AI, ComplyAdvantage
- **PayLicence AU:** FrankieOne, Change Financial, mx51
- **TokenPilot AU:** Chainalysis, Notabene
- **FinAI File AU:** Credo AI, Holistic AI, Monitaur
- **CloudProof AU:** Vanta, Drata, Secureframe
- **Tapease:** Square (Block), Tyro, Till Payments

### Signal Types Detected

| Signal | Icon | Examples |
|--------|------|----------|
| funding | 💰 | Capital raise, Series A-D, valuation |
| product_launch | 🚀 | New product, platform, feature |
| partnership | 🤝 | Strategic alliance, integration |
| regulatory | 📋 | AUSTRAC/ASIC/APRA approval, licence |
| acquisition | 🏢 | Merger, acquisition, takeover |
| expansion | 🌏 | AU/NZ market entry, office opening |
| earnings | 📊 | Quarterly/annual revenue reports |
| asx_announcement | 📈 | ASX-listed company filings |

### Maintenance

- **Adding competitors:** Edit `competitors.json`, add entry under matching category
- **Removing false positives:** If a competitor name matches common words (e.g., "Orchestra" matching "orchestration"), add to a blocklist in `competitor_intel.py`
- **The engine tracks history.** `~/.hermes/research_outputs/.briefing_improvements.json` contains the 30-day log. Don't delete it.
- **Competitor section is conditional.** The 👀 Competitor Watch section only appears when `competitor_intel.py` finds relevant competitor moves for HOT or WARM projects. Empty competitor intel → no section. Cold-project-only intel → no section. This prevents noise.
- **⚠️ Competitor intel has a known false-positive problem.**

When the morning briefing wasn't generated by the pipeline: see `references/recovery-procedure.md` for step-by-step recovery. In short: check what pipeline outputs exist, dry-run the improver, generate, deliver. Synthesis + competitor intel alone produce a useful (if lighter) briefing.
