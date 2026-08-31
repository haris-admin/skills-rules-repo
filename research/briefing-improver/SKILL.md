---
name: briefing-improver
description: Pluto's self-improving morning briefing engine — action-first format, portfolio heatmaps, regulatory pulse, checklist generation, and feedback-driven improvement. Use when running or debugging the briefing_improver.py script, adding new data sources to the briefing, or adjusting the improvement algorithm.
allowed-tools: [terminal, read_file, write_file, search_files]
---

# Briefing Improver

## When to Use
- Running the `Pluto Briefing Improver` cron (5:20 AM AEST, `no_agent: true`)
- Debugging briefing format issues or missing signals
- Adding new data sources or portfolio projects to the briefing
- Understanding the self-improvement feedback loop

## Architecture

The briefing improver (`~/.hermes/scripts/briefing_improver.py`) is a **self-improving engine** that reads today's research pipeline outputs and produces an action-first morning briefing for Gumby. It tracks 30-day improvement history and adapts to Haris's feedback.

### Design Principles
1. **Action-first** — Lead with what Haris needs to DO
2. **Regulatory pulse** — Surface legislative timing windows
3. **Portfolio heatmap** — Instant scan of which projects are HOT
4. **"Didn't know that"** — One surprising insight per briefing
5. **Checklist format** — Haris gravitates toward checklists
6. **Self-improving** — Gets better every day based on feedback

### Inputs
- `research_DATE.json` — Today's research findings
- `synthesis_DATE.json` — Cross-chamber synthesis patterns
- `actions_DATE.json` — Action bridge output
- `podcast_insights.md` — Recent podcast themes/frameworks/quotes
- `gumby-action-brief-DATE.md` — Action brief for Gumby

### Outputs
- Briefing markdown (stdout → cron delivery)
- `~/.hermes/research_outputs/.briefing_improvements.json` — 30-day improvement log
- `~/.hermes/research_outputs/.briefing_feedback.json` — User feedback tracking

## Usage

```bash
# Standard run (reads today's outputs, produces briefing)
python3 ~/.hermes/scripts/briefing_improver.py

# Dry run (no state update)
python3 ~/.hermes/scripts/briefing_improver.py --dry-run

# With feedback from Haris
python3 ~/.hermes/scripts/briefing_improver.py --feedback "A"
```

## Cron Integration

**Cron:** `7cc81d64613a` — Pluto Briefing Improver (5:20 AM) — internal  
**Type:** `no_agent: true`, `deliver: local`  
**Schedule:** 20 5 * * * (5:20 AM AEST)  
**Script:** `briefing_improver.py`

Runs after Action Bridge (5:15 AM) and before Morning Briefing (6:00 AM). Produces internal briefing markdown consumed by the 6AM delivery cron.

## 7 Portfolio Projects Monitored

| Project | Pillar | Status |
|---------|--------|--------|
| ExitLens AU | CGT/ESOP | HOT — CGT Senate vote Q3 2026 |
| AML Hive | AML/AUSTRAC | HOT — Tranche 2 enrolment OPEN |
| TokenPilot | Tokenisation | WARM |
| PayLicence | Payments | WARM |
| FinAI | AI/Finance | COOL |
| CloudProof | Cloud/Audit | WARM |
| Tapease | DevOps | WARM |

## Self-Improvement Loop

1. Each day's briefing is logged to `.briefing_improvements.json`
2. When Haris provides feedback (A/B/C choices), tracked in `.briefing_feedback.json`
3. Next day's briefing adapts: adjusts signal counts, format preferences, checklist depth
4. 30-day history enables trend detection (which formats get best engagement)

## Pitfalls

- **Portfolio connection format changed (Jun 26, 2026):** `podcast_insights.json` switched from string connections to dicts with `project`, `rationale`, `episode` fields. `_map_podcast_connections()` was patched to handle both with `isinstance()` checks. Always test with the latest podcast_insights.json format.
- **Signal count is capped at MAX_SIGNALS (7).** More signals = more noise. The script prioritizes regulatory/actionable signals over general market trends.
- **Briefing length is capped at 140 lines.** If too long, signals are truncated. Keep signal descriptions to 2-3 sentences.
- **Feedback file format:** `{"date": "...", "choice": "A/B/C", "applied": true/false}`. Missing `applied` field = feedback received but not yet processed.
