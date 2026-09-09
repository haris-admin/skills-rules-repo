---
name: pluto-mempalace-bridge
description: Pluto-Mempalace dual-agent knowledge bridge — ChromaDB feeder, Gumby query interface, and autonomous research pipeline. Use when working with the mempalace, setting up research pipelines, or troubleshooting the bridge.
---

# Pluto-Mempalace Bridge Architecture

> **⚠️ Alexandria mirror check (2026-09-09):** the whole-vault audit
> (`alexandria/vault/_refinery/rationalisation-2026-09-09/`) found the
> `alexandria/vault/mempalace/` mirror **frozen** — weekly-captures stop ~early June 2026, many
> files are "*No signals yet*" shells. The ChromaDB feeder / query pipeline described below still
> runs on cron, but confirm the Windows MemPalace source is live and the mirror is refreshing
> before relying on `vault/mempalace/` content. If the store is retired, the mirror should be
> archived (NEEDS HARIS in the audit).

## Chamber Architecture (v3.2 — Aug 2026: 12 collections)

> **⚠️ UPDATE Aug 16, 2026:** The 27-collection architecture was consolidated to **12 collections** (~2,014 docs) by `mempalace_optimize.py`. The 6 source-topic chambers (`events-sydney`, `accelerators`, `cloud-frontier`, `startup-funding`, `coding-agents`, `ai-frontier`) and 3 emergent chambers (`market-signals`, `quantum-computing`, `space-tech`) were merged into their parent domain chambers or `pluto_research`. **Current live collections (12):** `regulatory-ai`, `fintech-aml`, `agentic-security`, `cloud-infra`, `critical-infra`, `startup-vc`, `payments-npp`, `digital-identity`, `sovereign-ai`, `agent-architecture`, `aie-podcast`, `pluto_research`. The historical 27-collection detail below is retained for reference only.

The mempalace uses a **12-collection ChromaDB architecture** (10 domain + 1 per-source + 1 legacy). Each chamber is a dedicated ChromaDB collection.

**Three types of chambers:**

1. **Domain chambers (16 fixed):** The original taxonomy covering AI regulation, fintech/AML, agent security, etc. These have keyword-based auto-routing via `route_to_chamber()`.

2. **Source-topic chambers (6, new June 7, 2026):** Created to hold information streams that don't fit neatly into domain chambers. Fed from Claude Daily Research and similar multi-topic sources. Queried directly by name. The cross-chamber synthesizer picks them up automatically.
   - `events-sydney` — Sydney conferences, pitch nights, meetups (6 docs)
   - `accelerators` — Startup accelerators, founder programs, pitch events (6 docs)
   - `cloud-frontier` — AWS/GCP/Azure product launches, pricing, multicloud trends (5 docs)
   - `startup-funding` — VC rounds, mega-deals, global funding trends (6 docs)
   - `coding-agents` — AI coding tools: Claude Code, Copilot, Cursor (2 docs)
   - `ai-frontier` — Multi-agent manufacturing, enterprise agent infrastructure (2 docs)

3. **Per-source chambers (ad-hoc):** Created on-the-fly for dedicated single-source knowledge bases. No seed needed. Examples:
   - `aie-podcast` — @aiDotEngineer channel (348 docs)
   - Any future dedicated podcast/book/paper source

4. **Emergent chambers (3, discovered June 20, 2026):** Chambers created outside the documented taxonomy — likely auto-created by the feeder from new information streams. These need investigation to determine if they should be promoted to domain or source-topic status.
   - `market-signals` — 11 docs
   - `quantum-computing` — 1 doc
   - `space-tech` — 1 doc

**Chamber creation philosophy (per Haris, June 7, 2026):** "Let's not try to fit everything into the existing ones. So make logical chambers... so that we can actually have more clarity about information coming in for those chambers separately." **Prefer creating a new chamber over cramming into an existing one when the information stream is a distinct topic or source.** The goal is clarity and retrievability — chambers should make it obvious where to look later.

**Source-topic and per-source chambers don't appear in domain auto-routing.** They're queried directly by name. The cross-chamber synthesizer picks them up automatically.

**Chamber creation is on-the-fly:** The feeder auto-creates a ChromaDB collection when you feed to a new chamber name. No need to run `seed_chambers.py` or pre-create collections. Just:
```bash
python3 pluto_mempalace_feeder.py --input data.json --chamber my-new-chamber
```

### Chamber-Aware CLI (Feeder v2.0)
```bash
# Feed to specific chamber (or auto-route)
python3 pluto_mempalace_feeder.py --input data.json --chamber fintech-aml

# Search specific chamber
python3 pluto_mempalace_feeder.py --query "Tranche 2" --chamber fintech-aml

# Cross-chamber search (default — searches all 16 chambers)
python3 pluto_mempalace_feeder.py --query "AI regulation"

# List all chambers
python3 pluto_mempalace_feeder.py --list-chambers

# Full status with per-chamber breakdown
python3 pluto_mempalace_feeder.py --status
```

### Chamber Taxonomy Overview

**16 Domain Chambers (June 12, 2026 — live counts):**
| Domain | Chamber | Docs |
|--------|---------|------|
| AI Regulation | `regulatory-ai` | 134 |
| FinTech/AML | `fintech-aml` | 82 |
| Agent Security | `agentic-security` | 41 |
| Cloud/Infra | `cloud-infra` | 29 |
| Startup/VC | `startup-vc` | 64 |
| Sovereign AI | `sovereign-ai` | 21 |
| Payments/NPP | `payments-npp` | 10 |
| Digital Identity | `digital-identity` | 3 |
| Data Sovereignty | `data-sovereignty` | 3 |
| RegTech | `regtech-tools` | 6 |
| Agent Architecture | `agent-architecture` | 7 |
| InsurTech | `insurtech` | 3 |
| Agent SRE | `agent-observability` | 5 |
| Critical Infra | `critical-infra` | 18 |
| Legal/Professional | `legal-professional` | 3 |
| Voice/Creative | `voice-creative` | 3 |

**6 Source-Topic Chambers (🆕 June 7, 2026 — Claude Daily Research):**
| Domain | Chamber | Docs |
|--------|---------|------|
| Sydney Events | `events-sydney` | 6 |
| Accelerators | `accelerators` | 6 |
| Cloud Frontier | `cloud-frontier` | 5 |
| Startup Funding | `startup-funding` | 6 |
| Coding Agents | `coding-agents` | 2 |
| AI Frontier | `ai-frontier` | 2 |

**Per-Source Chambers:**
| Source | Chamber | Docs |
|--------|---------|------|
| AI Engineer Podcast | `aie-podcast` | 348 |

**Emergent Chambers (discovered June 20, 2026):**
| Domain | Chamber | Docs |
|--------|---------|------|
| Market Signals | `market-signals` | 11 |
| Quantum Computing | `quantum-computing` | 1 |
| Space Tech | `space-tech` | 1 |

**Legacy:**
| Collection | Docs |
|------------|------|
| `pluto_research` | 241 |

**Total: 1,675+ docs across 27 collections (June 20, 2026)**

**New as of June 4, 2026:**
- `aie-podcast`: 372 episodes from @aiDotEngineer (AI Engineer by swyx) mapped and ready for transcript ingestion. Covers agents, MCP, LLM ops, evals, coding agents, agent architecture. Blocked by YouTube IP until cookies exported. Ingestion script: `/tmp/aie_chamber_ingest.py`.
- `critical-infra`: 15 Moonshots podcast episodes (AI, geopolitics, consciousness, future-of-work) with frameworks + quiz questions
- `startup-vc`: 11 ranked podcasts (The Pitch) + 10 categorized podcasts (The Investors Podcast) — 21 podcast reviews total
- **Moonshots Daily Learning cron** (`0fb6bf47f704`, 8:15 PM AEST): Picks random topic from these chambers, teaches concept, quizzes Haris
- **Podcast knowledge ingestion at scale:** The `pluto-podcast-knowledge` skill covers multi-source podcast ingestion (30+ shows), Supabase+pgvector vector storage architecture, twice-weekly monitoring crons, and Lenny's Podcast credential integration. See `pluto-podcast-knowledge` skill and `references/supabase-pgvector-schema.md` for the full Supabase pgvector schema (4 tables with hybrid search function). ChromaDB is retained for small-scale knowledge bases (<100 docs); Supabase+pgvector is recommended for 500+ episodes.

## Components

### 0. Research Staging Inbox (`~/.hermes/mempalace-inputs/`) — OPERATIONAL
The **staging inbox** where raw research markdown files land before being auto-processed into ChromaDB. Drop a `.md` file → ≤5 minutes later it's in the knowledge base.

**Current state (May 24, 2026):** Fully wired. Watcher script operational, auto-processing cron active (`5678a363ce3b`). 4/4 files processed, 16 findings fed to ChromaDB (33 total docs across 7 topics). See `references/mempalace-inputs.md` for the complete workflow.

**Input format** (markdown with metadata):
```
# Topic Name
Tags: tag1, tag2

## Finding Title [VERIFIED]
Content paragraph(s)...
Source: https://real-url.com
Type: regulatory|technical|market|opportunity|threat|trend
Confidence: high|medium|low
```

**Flow:**
1. Drop `.md` file in `~/.hermes/mempalace-inputs/`
2. Watcher cron (`5678a363ce3b`, every 5 min) auto-detects new file
3. `mempalace_watcher.py` parses → structures JSON → calls `pluto_mempalace_feeder.py`
4. Findings land in ChromaDB `pluto_research` collection
5. File marked as processed in `mempalace-inputs/.processed/`

**Use cases:**
- Weekend research missions (batch-drop 4 topic files)
- RegRadar Enterprise custom topic requests
- External data ingestion (Gumby drops files via PowerShell bridge)

### 1. ChromaDB Feeder v2.0 (`~/.hermes/scripts/pluto_mempalace_feeder.py`)
Pluto's primary interface to the ChromaDB mempalace at `/mnt/c/Users/habib/.mempalace/palace/`. Now chamber-aware with auto-routing and cross-chamber search.

**Chamber routing:** `route_to_chamber(topic, tags)` maps topics to the correct chamber using keyword scoring + legacy topic map. Falls back to `pluto_research`.

**Collections (27 total — 16 domain + 6 source-topic + 3 per-source/legacy + 3 emergent):**
Domain: `regulatory-ai`, `fintech-aml`, `agentic-security`, `cloud-infra`, `digital-identity`, `data-sovereignty`, `startup-vc`, `sovereign-ai`, `regtech-tools`, `agent-architecture`, `payments-npp`, `insurtech`, `agent-observability`, `critical-infra`, `legal-professional`, `voice-creative`

Source-topic (🆕 June 2026): `events-sydney`, `accelerators`, `cloud-frontier`, `startup-funding`, `coding-agents`, `ai-frontier`

Per-source: `aie-podcast`; Legacy: `pluto_research`

Emergent (🆕 June 20, 2026): `market-signals` (11), `quantum-computing` (1), `space-tech` (1)

**Usage:**
```bash
# Feed research (auto-routes to best-fit chamber)
python3 ~/.hermes/scripts/pluto_mempalace_feeder.py --input findings.json --topic "AUSTRAC Tranche 2"

# Feed to specific chamber
python3 ~/.hermes/scripts/pluto_mempalace_feeder.py --input findings.json --chamber fintech-aml

# Cross-chamber search (default: all chambers)
python3 ~/.hermes/scripts/pluto_mempalace_feeder.py --query "sovereign AI"

# Chamber-specific search
python3 ~/.hermes/scripts/pluto_mempalace_feeder.py --query "AML" --chamber fintech-aml

# Status with per-chamber breakdown
python3 ~/.hermes/scripts/pluto_mempalace_feeder.py --status

# List all chambers
python3 ~/.hermes/scripts/pluto_mempalace_feeder.py --list-chambers
```

### 2. Gumby Query Interface (`~/.hermes/scripts/gumby_mempalace_query.py`)
Allows Gumby (OpenClaw on Windows) to search Pluto's mempalace.

**WSL call:**
```bash
python3 ~/.hermes/scripts/gumby_mempalace_query.py "AUSTRAC" --n 5
```

**PowerShell wrapper (from Windows):**
```powershell
.\query_mempalace.ps1 "AUSTRAC compliance"
.\query_mempalace.ps1 -Status
.\query_mempalace.ps1 -Daily "2026-05-22"
```

### 3. Research Pipeline
Defined in `pluto-autonomous-research` skill:
1. Web search → 2. Synthesize findings → 3. Write JSON → 4. Feed ChromaDB → 5. Report

### 4. Cross-Chamber Synthesizer (`~/.hermes/scripts/pluto_cross_chamber_synthesizer.py`) — NEW May 27
Queries ALL 16 ChromaDB chambers, detects cross-domain patterns and contradictions, and surfaces recurring signals with frequency counts. This is the SYNTHESIZE layer of the pipeline — it bridges individual research findings into strategic intelligence.

**Usage:**
```bash
# Full synthesis across all chambers (default: last 3 days)
python3 ~/.hermes/scripts/pluto_cross_chamber_synthesizer.py

# Narrower window
python3 ~/.hermes/scripts/pluto_cross_chamber_synthesizer.py --days 1

# Contradiction-focused analysis
python3 ~/.hermes/scripts/pluto_cross_chamber_synthesizer.py --contradictions

# JSON output
python3 ~/.hermes/scripts/pluto_cross_chamber_synthesizer.py --output json
```

**Outputs:** `synthesis_YYYY-MM-DD.json` (structured) + `synthesis_YYYY-MM-DD.md` (human-readable). The MD summary includes cross-domain themes ranked by concept count, contradictions detected, top recurring signals with frequency counts, and per-chamber status breakdowns.

**Cross-domain pairs:** 16 predefined chamber pairs (e.g., `regulatory-ai × fintech-aml`, `agentic-security × agent-architecture`) that are semantically analyzed for shared concepts. First run (May 27): 108 docs → 9 patterns + 2 contradictions across 16 chambers. See `references/synthesis-example-2026-05-27.md` for the full output from the inaugural run.

### 5. Action Bridge (`~/.hermes/scripts/pluto_action_bridge.py`) — NEW May 27
Converts synthesis output into concrete, prioritized, project-mapped actions. The ACT layer of the pipeline.

**Priority rules** (built-in):
- `deadline`, `mandatory`, `penalty`, `fine` → 🔴 CRITICAL
- `enforcement`, `AUSTRAC`, `compliance`, `breach` → 🟠 HIGH
- `opportunity`, `trend` → 🟡 MEDIUM
- `insight` → 🟢 LOW

**Project mapping** (built-in):
- `regulatory-ai`, `fintech-aml`, `regtech-tools`, `sovereign-ai`, `data-sovereignty`, `digital-identity`, `legal-professional` → **RegStack**
- `agentic-security`, `agent-architecture`, `agent-observability` → **AgentSRE**
- `cloud-infra`, `payments-npp`, `critical-infra` → **Tapease**
- `startup-vc`, `insurtech` → **Portfolio**
- `voice-creative` → **Pluto**

**Usage:**
```bash
python3 ~/.hermes/scripts/pluto_action_bridge.py                      # From latest synthesis
python3 ~/.hermes/scripts/pluto_action_bridge.py --json-input FILE    # From specific synthesis
```

**Outputs:** `actions_YYYY-MM-DD.json` (structured actions) + `gumby-action-brief-YYYY-MM-DD.md` (formatted for Gumby's morning brief). First run (May 27): 19 actions generated from 9 synthesis patterns — 8 CRITICAL, 5 HIGH, 5 MEDIUM, 1 enrichment.

### 6. Feedback Processor (`~/.hermes/scripts/pluto_feedback_processor.py`) — NEW May 27
Reads Gumby's morning brief to track which Pluto research findings were actually used. Closes the signal quality loop.

**How it works:**
1. Parses Gumby's brief output for Pluto signal references
2. Tracks per-topic utilization scores (e.g., AUSTRAC: 100%, others: 0%)
3. Accumulates `feedback/signal_scores.json` over time
4. Generates utilization reports and priority adjustment recommendations
5. Produces `pluto-feedback-to-gumby.md` requesting USED:/SKIPPED: markers for future briefs

**Usage:**
```bash
python3 ~/.hermes/scripts/pluto_feedback_processor.py                     # Auto-detect latest
python3 ~/.hermes/scripts/pluto_feedback_processor.py --brief FILE        # From specific brief
python3 ~/.hermes/scripts/pluto_feedback_processor.py --list-pending      # List unprocessed
```

**Signal scores** accumulate at `~/.hermes/research_outputs/feedback/signal_scores.json` with fields: topic_scores, source_scores (RSS feed reliability), confidence_calibration, and per-finding usage tracking. First run (May 27): 17% utilization rate (only AUSTRAC used by Gumby).

**Feedback protocol:** Pluto requests Gumby annotate morning briefs with `USED: finding #N` / `SKIPPED: finding #N` markers. This enables automatic signal quality tracking without manual intervention.

### 7. MemPalace Nightly Cleanup (`~/.hermes/scripts/mempalace_cleanup.py`) — NEW June 5, 2026
Runs at 11:55 PM AEST (cron `0fc5019948be`). Archives old research files, checks ChromaDB health, and generates a daily activity summary.

**What it does:**
1. **Archive old files** — moves `synthesis_*`, `actions_*`, `research_*`, `briefing_*`, `podcast_insights_*` files older than 7 days to `~/.hermes/archive/research/YYYY/MM/`
2. **ChromaDB health check** — reports total storage size, flags if compaction needed
3. **Daily activity summary** — counts files generated today by type
4. **State tracking** — writes `~/.hermes/research_outputs/.cleanup_state.json` with last_cleanup timestamp and total_archived count

**Why nightly:** Prevents `research_outputs/` from accumulating hundreds of stale files (already 139 files / 1.3MB as of June 2026). The 7-day retention keeps the working set lean while the archive preserves history.

### 7. Cron Jobs (Updated June 5, 2026)
- `Podcast KB Ingestion (4:00 AM AEST)` — `d4d77c41f6c0`, daily at 04:00, ingests YouTube transcripts via YouTube API v3 (max 3/show, 5s delays, auto-abort on IP block)
- `Git Repo Sync (1:00 AM AEST)` — `c23dc3f73e2d`, daily at 01:00, pulls all GitLab (hhsiddiqui + hhsiddiqui-group) and GitHub repos
- `Gmail Briefing Ingestor (4:55 AM AEST)` — `e5675447ed37`, daily at 04:55, pulls Perplexity + Claude Daily Research briefings via Python imaplib → `mempalace-inputs/`. `no_agent: true`, `deliver: local`. Script: `gmail_ingestor_imaplib.py`. **⚠️ Claude format fix applied 20 Aug 2026** — see `references/claude-daily-research-ingestion.md` for the silent-skip root cause + detection rule.
- `Podcast Insight Extractor (5:02 AM AEST)` — `67319a9b2606`, daily at 05:02, extracts themes/frameworks/quotes from recent podcast episodes → `~/.hermes/research_outputs/podcast_insights.md`
- `Pluto Morning Research (5:05 AM AEST)` — `b0de180cec84`, daily at 05:05, research pipeline → gumby-brief-input.md
- `Pluto Cross-Chamber Synthesis` — `ddceef1f9e5b`, daily at 05:10, runs `pluto_cross_chamber_synthesizer.py` (picks up podcast insights automatically)
- `Pluto Action Bridge` — `38c1aa80a5b8`, daily at 05:15, converts synthesis to actions
- `Pluto Honcho Signal Bridge (5:30 AM)` — `pluto_honcho_bridge_daily`, pushes Pluto signals to Honcho
- `Pluto Feedback Processor` — `59f18c4d557c`, daily at 06:10, tracks Gumby's signal utilization
- `Moonshots Daily Learning (6:15 AM AEST)` — `0fb6bf47f704`, random podcast episode → teach concept + quiz
- `Pluto LinkedIn Ideas (6:45 AM AEST)` — `ee4e48300826`, generates LinkedIn/blog post ideas
- `Pluto Skill Extractor` — `2d33c8f9a89c`, daily at 11:00 AM AEST, scans sessions + scripts for reusable patterns
- `Pluto Morning Briefing (6:00 AM Mon-Fri)` — `c527fed4a1da`, delivers briefing text + voice via Telegram (voice generated inline)
- `Pluto Chamber Refresh (5:25 AM AEST)` — `0959371eec17`, daily at 05:25. `script: pluto_chamber_refresh.py`, `no_agent: true`, `deliver: local`. Feeds Gmail/Perplexity + podcast transcripts + research findings into chambers, then triggers synthesis.
- `Vercel Monitor — AML Hive (5:05 AM/PM AEST)` — `745ec76c6bf9`, twice daily at 05:05 and 17:05, runs `vercel_monitor.py` to check deployment health and send email alerts (hhsiddiqui@gmail.com + shoaib@amlhive.com.au)
- `Pluto Weekly Review (Fri 11:05 PM AEST)` — `cc5ca5690d05`, every Friday, reviews the week: what worked, what didn't, what to improve. Saves to `~/.hermes/reviews/weekly/weekly-review-{DATE}.md`
- `Pluto Weekly Improvements (Sat 12:00 AM AEST)` — `159702fe072c`, every Saturday midnight, implements the review's action items across 5 phases: 🧹 Stale data cleanup (pgvector), 🧠 MemPalace updates, 🔧 Skill rewriting, 🔗 Connection rewiring, 🌙 Dreaming (speculative improvements)
- `Mempalace Inbox Watcher` — `5678a363ce3b`, every 5 minutes, auto-processes `mempalace-inputs/`
- `MemPalace Nightly Cleanup (11:55 PM AEST)` — `0fc5019948be`, archives old research files, compacts ChromaDB

### 8. Gumby Handoff Bridge (v3.0 — Dual-Channel, May 2026)
After each morning research run, Pluto delivers findings to Gumby via **two complementary channels**:

**Channel A — File Pull (primary, long-form):** Pluto writes `~/.hermes/research_outputs/gumby-brief-input.md` — a markdown summary with actionable signals formatted for Gumby's 6AM morning brief. Gumby reads it from Windows via `wsl cat`. The 55-minute buffer (5:05 → 6:00 AM AEST) ensures the file is always fresh.

**Channel B — Honcho Push (complementary, signal cards):** The `pluto_honcho_bridge.py` script pushes structured `[pluto]` signal cards to Honcho's message stream. Gumby's message pull pipeline picks these up as scannable, bite-sized action items alongside the full brief. First operational cycle (May 29, 2026): 8/11 signals delivered via Honcho. State tracked in `.honcho_bridge_state.json` to prevent duplicate pushes. Full architecture in `fleet-intelligence` → `references/honcho-signal-bridge.md`.

**Enhanced by the full pipeline (May 27+):**
- **Research brief** (`gumby-brief-input.md`): Top signals with For-Haris hooks, confidence levels, and source URLs
- **Action brief** (`gumby-action-brief-YYYY-MM-DD.md`): Prioritized, project-mapped actions from cross-chamber synthesis — includes CRITICAL/HIGH/MEDIUM triage with specific project assignments (RegStack, AgentSRE, Tapease, Portfolio)
- **Honcho signal cards** (`[pluto]` messages via `pluto_honcho_bridge.py`): Structured signal summaries pushed to Honcho for Gumby's message pull pipeline — scannable bite-sized action items alongside the long-form briefs
- **Feedback request** (`pluto-feedback-to-gumby.md`): Pluto requests Gumby annotate briefs with USED:/SKIPPED: markers to close the signal quality loop

For deep-dive queries beyond the top-line signals, Gumby can still use the `gumby_mempalace_query.py` CLI.

## Dependencies
- ChromaDB with ONNX embedding (DefaultEmbeddingFunction)
- SQLite accessible at `/mnt/c/Users/habib/.mempalace/palace/chroma.sqlite3`
- Python packages: chromadb, onnxruntime
- **Honcho memory provider:** Configured 2026-05-23. See `references/honcho-setup.md` in the `fleet-intelligence` skill or load `fleet-intelligence` with `file_path='references/honcho-setup.md'`.

## Reference Files
- `references/mempalace-inputs.md` — Staging inbox workflow and wiring plan
- `references/16-chamber-architecture.md` — Full chamber taxonomy, migration history, seeding procedure, and data flow (May 2026 upgrade)
- `references/watcher-cron-fix.md` — Corrected watcher cron prompt and DEEPSEEK_API_KEY expiry investigation pattern
- `references/honcho-setup.md` — Cross-referenced from `fleet-intelligence` skill
- `references/synthesis-example-2026-05-27.md` — Known-good output from the inaugural cross-chamber synthesis + action bridge + feedback loop run (May 27, 2026). Includes full pattern map, action breakdown, and feedback results.
- `references/pipeline-stability-validation-2026-05-31.md` — 4-cycle stability validation (May 27–30, 2026): zero script changes, 100% feedback utilization, skill deduplication map showing which "pending" skills are already covered by existing umbrellas.
- `references/claude-daily-research-ingestion.md` — 🆕 Claude Daily Research ingestion pattern: email format, parsing, chamber routing, watcher format requirements, and user preferences for Sydney events/accelerators (June 7, 2026).

## Data Flow (v3.0 — Full Pipeline, May 2026)

```
Research Request → mempalace-inputs/*.md → mempalace_watcher.py (cron: */5m)
    ↓
route_to_chamber(topic, tags) → target chamber collection
    ↓
ChromaDB: regulatory-ai | fintech-aml | agentic-security | ... (16 chambers)
    ↓                                              ↓
search_mempalace(query)              pluto_cross_chamber_synthesizer.py (cron: ddceef1f9e5b)
    ↑                                              ↓
Gumby (PowerShell)                    synthesis_*.json/md — cross-domain patterns
    ↑                                              ↓
gumby_mempalace_query.py        pluto_action_bridge.py — prioritized actions
    ↑                                              ↓
[Gumby's 6AM brief]          gumby-action-brief-*.md → Gumby's morning brief
    ↑         ↑                    ↓
    │         │   pluto_honcho_bridge.py → Honcho [pluto] signals → Gumby's message pull
    │         └─────────────────────────────────────────────────────────────┘
    └── pluto_feedback_processor.py (cron: 59f18c4d557c)
                                                              ↓
                                              signal_scores.json → priority adjustment
                                                              ↓
                                              pluto-feedback-to-gumby.md (USED:/SKIPPED: protocol)
                                                              ↓
                                                    Next research cycle (adjusted)
```

**Full pipeline stages (all wired as of June 5, 2026):**
1. **Podcast Ingestion** — `podcast_ingestor.py` (cron: `d4d77c41f6c0`, 4:00 AM) ingests YouTube transcripts into Supabase pgvector (max 3/show, 5s delays, auto-abort on IP block)
2. **Git Repo Sync** — `git_sync.py` (cron: `c23dc3f73e2d`, 1:00 AM) pulls all GitLab (hhsiddiqui + hhsiddiqui-group) and GitHub repos to `/mnt/c/Code/gitlab/`
3. **Gmail Ingestor** — Pulls Perplexity and other briefings from email (cron: `e5675447ed37`, 4:55 AM)
4. **Podcast Insight Extractor** — Queries Supabase for recent episodes, extracts themes/frameworks/quotes → `research_outputs/podcast_insights.md` (cron: `67319a9b2606`, 5:02 AM)
5. **mempalace-inputs/** — Raw markdown staging. Files dropped here auto-processed within 5 minutes.
6. **mempalace_watcher.py** — `5678a363ce3b` polls every 5 min, parses `.md` files, structures as JSON.
7. **Chamber routing** — `route_to_chamber()` maps topic+tags to the correct chamber collection.
8. **Feeder v2.0** — Validates JSON → embeds → stores in the target chamber collection.
9. **Cross-chamber search** — `search_mempalace()` queries all 16 chambers by default.
10. **Research Pipeline** — Autonomous deep research (cron: `b0de180cec84`, 5:05 AM).
11. **Cross-Chamber Synthesis** — `pluto_cross_chamber_synthesizer.py` (cron: `ddceef1f9e5b`, 5:10 AM) — picks up podcast insights automatically from `research_outputs/`.
12. **Action Bridge** — `pluto_action_bridge.py` (cron: `38c1aa80a5b8`, 5:15 AM).
13. **Feedback Loop** — `pluto_feedback_processor.py` (cron: `59f18c4d557c`, 6:10 AM).
14. **Daily Learning** — Random podcast episode → teach concept + quiz (cron: `0fb6bf47f704`, 6:15 AM).
15. **Morning Briefing** — Text + voice MP3 delivered via Telegram (cron: `c527fed4a1da`, 6:00 AM Mon-Fri).
22. **Chamber Refresh** — `pluto_chamber_refresh.py` (cron: `0959371eec17`, 5:25 AM). Cross-source feed: Gmail briefings + podcast transcripts + research findings → ChromaDB chambers → synthesis.
17. **Nightly MemPalace Cleanup** — `mempalace_cleanup.py` (cron: `0fc5019948be`, 11:55 PM) archives old research files, checks ChromaDB health.
18. **Vercel Monitor (AM/PM)** — `vercel_monitor.py` (cron: `745ec76c6bf9`, 5:05 AM & 5:05 PM) checks AML Hive deployment health, catches BLOCKED/ERROR states, sends email alerts.
19. **Weekly Review** — (cron: `cc5ca5690d05`, Fri 11:05 PM) reviews the week's operations, identifies what worked/failed, proposes improvements.
20. **Weekly Improvements** — (cron: `159702fe072c`, Sat 12:00 AM) implements review action items: stale data cleanup (pgvector), MemPalace updates, skill rewriting, connection rewiring, speculative dreaming.

## Feeding Interactive/Ad-Hoc Research into the Mempalace

Interactive Telegram sessions (asking Pluto to research a topic in real-time) produce files in `research_outputs/` but neither the mempalace watcher (which monitors `mempalace-inputs/`) nor the Honcho bridge (which only pushes pipeline-standard files `research_*.json`, `synthesis_*.json`, `actions_*.json`, `gumby-action-brief-*.md`, `feedback/*`) picks them up. **Knowledge from interactive sessions is absent from ChromaDB unless manually ingested.**

### Procedure: Manually Feed Interactive Research to ChromaDB

After any interactive research session that produced useful knowledge:

```bash
# Option A: Drop file into mempalace-inputs for the watcher to pick up
cp /home/habib/.hermes/research_outputs/YYYY-MM-DD-topic.md /home/habib/.hermes/mempalace-inputs/

# Option B: Feed directly to a specific chamber (skips watcher queue)
# First convert the research into feeder JSON format
python3 -c "
import json
# Build a minimal findings array from the research
data = {
    'topic': 'RFC 10008 HTTP Query Method',
    'findings': [
        {'title': 'Finding title', 'content': 'Content...', 'source': 'URL', 'type': 'technical', 'confidence': 'high'}
    ],
    'tags': ['rfc', 'http', 'api-design']
}
print(json.dumps(data))
" > /tmp/mempalace_feed.json && \
python3 ~/.hermes/scripts/pluto_mempalace_feeder.py --input /tmp/mempalace_feed.json --chamber agentic-security

# Option C: For complex multi-topic files, create separate input files per chamber
# The playbook format (AML-Hive-Internal-Plan) covers multiple domains —
# split findings by chamber and feed each separately
```

### Common Sources of Interactive Research Files

Files saved during interactive sessions that need manual ingestion:

| File Pattern | Typical Content | Suggested Chamber |
|-------------|----------------|-------------------|
| `*-playbook-query.md` / `*-plan-playbook-*.md` | RFC analysis, startup credits, business plans | Varies — split by subtopic |
| `*-deep-dive-*.md` | Single-topic deep research | Auto-route or domain chamber |
| `*-analysis-*.md` | Competitive/market analysis | `startup-vc` or `regtech-tools` |
| `*-audit-*.md` / `*-review-*.md` | Infrastructure/code audits | Chamber based on audited domain |

### Checking the mempalace-inputs Backlog

The watcher cron (`5678a363ce3b`, every 5 min) processes `mempalace-inputs/` but files can accumulate if the watcher's agent is in an error state:

```bash
# Check how many files are pending in the inbox
ls ~/.hermes/mempalace-inputs/*.md 2>/dev/null | wc -l

# Check what's already processed
ls ~/.hermes/mempalace-inputs/.processed/*.done 2>/dev/null | wc -l

# Dry-run any unprocessed files
python3 ~/.hermes/scripts/mempalace_watcher.py --status

# Force-process all pending
python3 ~/.hermes/scripts/mempalace_watcher.py
```

If files from days/weeks ago are still sitting unprocessed, the watcher cron needs investigation — run it manually first, then check `cronjob list` for the cron's `last_status`.

## Pitfalls

- **Interactive/ad-hoc research is invisible to both ingestion pipelines.** Files saved to `research_outputs/` during interactive Telegram sessions (e.g., `2026-06-18-aml-hive-internal-plan-playbook-query.md`) are NOT picked up by: (a) the mempalace watcher (only monitors `mempalace-inputs/`), or (b) the Honcho bridge (only pushes pipeline-standard `research_*.json`, `synthesis_*.json`, etc.). After any interactive research session, manually copy the file to `mempalace-inputs/` or feed directly via the feeder script. See the "Feeding Interactive/Ad-Hoc Research" section above for step-by-step.
- **Python buffering in cron/background processes: always use `python3 -u`.** When Python stdout is piped (cron jobs, `background=true`, delegate_task), it switches to 4KB block buffering. A script can run for minutes with zero visible output — psql queries complete, yt-dlp downloads finish, but the log shows nothing. Always use `python3 -u script.py` in cron prompts, background terminal commands, and subprocess calls. This applies to ALL Pluto scripts: podcast_ingestor.py, mempalace_cleanup.py, git_sync.py, etc.

- **`/tmp/` is wiped on reboot.** Any venv or cache placed in `/tmp/` (e.g., `/tmp/podcast_venv/`) will be gone after a system restart. Scripts that hardcode `/tmp/venv/bin/python3` will fail with "No such file or directory." Document the rebuild command in any skill that depends on a `/tmp/` venv, and consider placing persistent venvs under `~/.hermes/venvs/` for long-lived dependencies.
- **🔴 chromadb import fails with opentelemetry version drift (fixed Aug 15, 2026).** `import chromadb` fails with `ModuleNotFoundError: No module named 'opentelemetry.exporter.otlp.proto.common._exporter_metrics'`. Root cause: mixed opentelemetry package versions in `~/.hermes/repo/venv` (grpc 1.44.0 vs common/api/sdk 1.39.1). When this happens, the Chamber Refresh cron silently feeds 0 items — every feed shows `Traceback ... pluto_mempalace_feeder.py` and the footer reads `Fed 0 new item(s)`. **Fix (align all opentelemetry to one version):**
  ```bash
  pip install -U 'opentelemetry-api==1.44.0' 'opentelemetry-sdk==1.44.0' 'opentelemetry-exporter-otlp-proto-common==1.44.0' 'opentelemetry-exporter-otlp-proto-http==1.44.0' 'opentelemetry-exporter-otlp-proto-grpc==1.44.0' 'opentelemetry-proto==1.44.0'
  ```
  **Verify:** `python3 -c "import chromadb; print(chromadb.__version__)"` → prints `1.5.9 IMPORT OK`. **Detection:** Chamber Refresh cron `last_status` stays `ok` (script exits 0 despite failed feeds) while output shows `❌ ... feed failed` — a silent-failure false negative that the cron health check misses. Check the actual feed footer, not just `last_status`.
  **🔴 RECURRED Aug 22, 2026:** The exact same drift re-appeared (`opentelemetry-exporter-otlp-proto-grpc` at 1.44.0 while api/proto/sdk/common/http pinned at 1.39.1), silently breaking the Chamber Refresh for 4 days (Aug 18–21 all showed `Fed 0 new item(s)` with a feeder Traceback, masked by `last_status: ok`). Root cause: `hermes update` (Mon/Fri 4AM) reinstalls core deps and re-introduces the version mismatch. **Durable fix needed:** pin the six opentelemetry packages in a constraints file and re-apply after every `hermes update`, or add an import smoke-test to `pluto_chamber_refresh.py` that alerts (not silently skips) when `import chromadb` fails.
- First ChromaDB use downloads ONNX model (~80MB) — slow initial run
- ChromaDB SQLite must be accessible from WSL path (`/mnt/c/...`)
- Embedding function must match between feeder and query (DefaultEmbeddingFunction)
- Research outputs stored at `~/.hermes/research_outputs/`
- **Gumby's memory DB may be empty:** When using the bridge to query Gumby's state, always check `/mnt/c/Users/habib/.openclaw/memory/main.sqlite` first with `SELECT name FROM sqlite_master`. The DB can be reset/reinitialized (0MB, no tables) — don't assume it's populated. Fall back to reading Gumby's AGENTS.md, logs, and reports directly.
- **Watcher cron active:** Job `5678a363ce3b` auto-processes mempalace-inputs every 5 minutes. Files land, findings feed. The watcher script is at `~/.hermes/scripts/mempalace_watcher.py`. Run manually with `--status`, `--file`, or `--dry-run`.
- **Windows .env vs WSL .env:** Haris may place API keys in `C:\\Users\\habib\\.hermes\\.env` (Windows side) rather than `~/.hermes/.env` (WSL side). Always check both. From WSL, the Windows path is `/mnt/c/Users/habib/.hermes/.env`. This is common for Honcho and other cross-platform configurations.
- **16-chamber upgrade (May 2026):** The old 3-collection model (`pluto_research`, `pluto_skills`, `pluto_daily_summaries`) has been replaced by the 16-chamber architecture. New research should route to chambers, not `pluto_research`. The original `pluto_research` collection is retained as legacy. See `references/16-chamber-architecture.md` for full taxonomy, migration history, and seeding procedure.
- **Chamber creation is on-the-fly:** The feeder auto-creates a ChromaDB collection when you feed to a new `--chamber` name. No need to run `seed_chambers.py` for new chambers — that script is only for bulk-seeding empty domain chambers after a ChromaDB reset. For per-source chambers (e.g., a new podcast), just start feeding: `--chamber my-new-chamber`.\n- **⚠️ Dual ChromaDB locations — don't query the wrong one.** There are TWO ChromaDB databases: the real one at `/mnt/c/Users/habib/.mempalace/palace/` (Windows side, 27 collections, 1,675+ docs as of June 20, 2026) and an empty WSL-side one at `~/.hermes/mempalace/chromadb/` (0 collections). The feeder script uses the Windows path. If you check `chromadb.list_collections()` on the WSL path, you'll get 0 results and think the chambers are empty. Always use the Windows path: `chromadb.PersistentClient(path='/mnt/c/Users/habib/.mempalace/palace')`.\n\n- **Gmail ingestor dedup — check existing files not just state.** `gmail_ingestor_imaplib.py` was patched (June 12) to check both the state file AND filesystem for existing `gmail-briefing-{msg_id}-*.md` files before fetching. This prevents re-processing after state file resets. If duplicates appear, check the `processed_ids` list in `~/.hermes/research_outputs/.gmail_ingestor_state.json` and the file glob `~/.hermes/mempalace-inputs/gmail-briefing-$ID-*.md`.\n\n- **Chamber refresh script (`pluto_chamber_refresh.py`) expects the feeder to receive JSON input — NOT markdown.** The feeder's `--input` flag reads `json.load()`. To feed a markdown file or raw text, convert to feeder JSON format first (see source in `pluto_chamber_refresh.py` for the expected `topic`/`findings`/`tags`/`source` structure). The refresh script builds temp JSON files in `mempalace-inputs/` and cleans up after.\n- **Watcher cron agent may search wrong paths:** The Mempalace Inbox Watcher cron agent (job `5678a363ce3b`) can get confused and search non-existent paths like `/home/habib/.hermes/mempalace/inputs/`, `/home/habib/.hermes/data/mempalace-inputs/`, or `/home/habib/.hermes/inputs/` instead of the correct path `/home/habib/.hermes/mempalace-inputs/`. This wastes tokens every 5 minutes. Fix: update the cron job prompt with the explicit correct path and instruct the agent to NOT search variations. Run `mempalace_watcher.py --status` to verify the directory is accessible.
- **API key expiry cascades to all cron jobs:** When the DEEPSEEK_API_KEY becomes invalid (HTTP 401), ALL cron jobs using DeepSeek will fail silently with `last_status: error`. The Mempalace Inbox Watcher (every 5 min) will rack up hundreds of failures over 48+ hours. After fixing the key, check ALL cron jobs — those with `error` status from the outage window will self-heal on their next scheduled run. Investigation pattern: `cronjob list` → check `errors.log` for `401.*invalid` → trace timestamps → fix key → verify with `--status` on the watcher.
- **Low signal utilization breaks the feedback loop:** First feedback run (May 27) showed 17% utilization — only AUSTRAC signals were used by Gumby. If utilization stays below 30%, (a) Pluto should make signals more actionable with explicit "For Haris:" hooks, (b) shorten signal descriptions to 2-3 sentences max, (c) Gumby should annotate briefs with USED:/SKIPPED: markers so the feedback processor can identify which topics resonate. Without the markers, signal quality tracking is blind.
- **Cross-chamber synthesis needs populated chambers:** The synthesizer queries all 16 chambers. If chambers are empty or sparsely populated (e.g., 3 docs each), cross-domain patterns will be thin. Run `seed_chambers.py` after a ChromaDB reset, then accumulate at least 5+ docs per chamber before expecting meaningful synthesis output.
- **Synthesis → Action → Feedback pipeline is sequential:** The 5-minute gap between Research (19:05), Synthesis (19:10), and Feedback (20:10) allows each stage to complete and write output files before the next stage reads them. If a stage runs long (>5 min), the next stage may read incomplete or stale files. Check file timestamps if outputs are missing.

- **`--status` only shows domain chambers — use direct ChromaDB query for full picture:** The feeder's `--status` command only enumerates the 16 domain chambers + legacy collections. Source-topic chambers (`events-sydney`, `accelerators`, etc.), per-source chambers (`aie-podcast`), and emergent chambers (`market-signals`, `quantum-computing`, `space-tech`) are NOT listed. To see all 27 chambers: `python3 -c "import chromadb; c = chromadb.PersistentClient(path='/mnt/c/Users/habib/.mempalace/palace'); [print(f'{x.name}: {x.count()}') for x in sorted(c.list_collections(), key=lambda x: x.name)]"`.

- **`mempalace_cleanup.py` may skip `feedback/` subdirectory.** The nightly cleanup script (cron `0fc5019948be`, 11:55 PM AEST) archives files older than 7 days from `research_outputs/` but may not recurse into `research_outputs/feedback/`. As of June 13, 2026, 11 feedback files from May 27–June 5 were found in `feedback/` despite being 8–17 days old — the cleanup script either skips the subdirectory or its glob patterns don't include `feedback/*.md`. Check `mempalace_cleanup.py` and add `feedback/*.md` to the archive patterns if missing.

- **Claude Daily Research email format requires `\\r\\n` normalization:** The forwarded Claude emails use `\\r\\n` line endings from the originating Anthropic system. Before parsing, normalize: `text.replace('\\r\\n', '\\n').replace('\\r', '\\n')`. Additionally, the `*N. Title* — *Source, Date*` format often wraps across lines in email — try joining with the next line if the regex doesn't match on the first pass.

- **Claude Daily Research has multiple section formats:** The main content sections (Global Fintech, AI & Agentic) use `*N. Title* — *Source, Date*` with separate source attribution. The Events and Accelerators sections use `*N. Event Name — Date | Location*` without a separate source field — the entire line is the finding. Use different parsers for each.

- **Watcher only catches `##` headers, not `###`:** When writing `.md` files for the mempalace watcher to parse, each finding must use a `##` header. Using `## Section > ### Title` nesting causes the watcher to treat section names as findings and miss the actual items. For Claude Daily Research, use `## [Section Name] Finding Title` format — section context in the title, one `##` per finding.

- **Prefer new chambers over cramming (per Haris, June 7, 2026):** "Let's not try to fit everything into the existing ones. So make logical chambers... so that we can actually have more clarity." When a new information stream represents a distinct topic or source, create a dedicated chamber. The feeder auto-creates on first use with `--chamber new-name`. This keeps chambers clean and makes cross-chamber synthesis more meaningful.
