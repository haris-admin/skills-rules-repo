---
name: pluto-communication-protocol
description: Pluto's Telegram communication protocol — strict 3-tier message format (ACTION/DECISION/FYI), digest batching, and anti-flood rules. Use for EVERY Telegram message. Load at session start.
allowed-tools: []
---

# Pluto Communication Protocol

## When to Use
**ALWAYS.** Every Telegram message Pluto sends must follow this protocol. This is the default communication mode — not opt-in.

## The Core Rule

**Telegram is for Haris's attention, not for Pluto's activity log.**

Every message must earn its place by containing at least one of:
- An action Haris needs to take
- A decision Haris needs to make
- Information Haris needs to know (not "nice to know")

## Message Format

EVERY message uses exactly this structure:

```
🔴 ACTION: <single clear action item>
   Time: <estimate> | Impact: <low/medium/high>

🟡 DECISION: <single clear choice>
   Options: A) ... B) ...

🟢 FYI: <single clear fact>
   Why it matters: <one line>
```

Rules:
- A message can have ONE section, or multiple if genuinely needed
- No tables. No emoji grids. No ASCII art.
- If you need a table, it's a file in `research_outputs/`, not a Telegram message
- Max ~10 lines per message. If it's longer, it goes to a file

## Tier Definitions

### 🔴 ACTION — Haris must DO something
- Export cookies, review a PR, check a deployment, read a document
- Always includes time estimate and impact level
- If there's no clear next step for Haris, it's NOT an action

### 🟡 DECISION — Haris must CHOOSE
- Which idea to pursue, which tool to use, which approach to take
- Always includes clear options (A/B/C)
- Never open-ended "what do you think?" — always structured choices

### 🟢 FYI — Haris should KNOW
- Only when it changes his understanding or decisions
- Includes "Why it matters" — if you can't articulate why, don't send
- NOT for: process status, batch progress, routine completions

## What NEVER Goes to Telegram

- Process progress (batch 3/10 complete, ingestion running)
- Background process completion notifications (unless they contain an ACTION)
- Cron job results (those go to `local` delivery, not `origin`)
- "I'm working on X" or "Let me check Y" — just do it
- Success/failure scorecards from batch runs
- Routine status updates from pipelines

## Digest Batching

When Pluto has been doing background work that produces actionable findings:
1. Collect findings into `~/.hermes/research_outputs/`
2. At most once every 2-5 minutes, send ONE digest message
3. The digest follows the 3-tier format — actions first, then decisions, then FYIs
4. If there are NO actions or decisions, DON'T SEND THE DIGEST
5. Routine activity that produced nothing actionable = silence

## Kanban Board Preference (June 8, 2026)

When the user asks to "add tasks to the kanban board" or "show me what tasks are planned," use `hermes kanban create` to populate the Hermes built-in kanban, NOT a markdown file. The user wants to see tasks in the actual kanban board so they can monitor and work with them. Markdown task lists go to `research_outputs/` as supplementary detail only — the kanban board is the source of truth.

All cron jobs that produce routine output should use `deliver: local`, NOT `deliver: origin`.
Only crons that surface actions/decisions should ping Telegram.

### Delivery Channel (Aug 13, 2026 — Haris override, v2 CORRECTED)

**TWO Telegram groups — do NOT confuse them:**
- **daily_status_v2** = `telegram:-1003834479227` — general/daily updates: 6AM briefing, Sat/Sun reviews, TapEase fleet monitors (5/11/17/23), Tapease daily transactions, Tapease payout sweep, Tapease codex review, CoS follow-up.
- **AMLHive group** = `telegram:-1004485329864` — ALL AMLHive-related jobs (Haris override Aug 13): AmLHive AWS Fleet Monitors (5/11/17/23), AML Hive Daily Business Report (9:15PM), Website Monitor (7AM), Daily Probe Summary (21:45), hourly version+attribution probes, AMLHive Daily Test Suite (3AM), Weekly Codex Review AML Hive, Weekly Search/AI-Answer/Metadata/Evidence reviews, Monthly Strategy Review, Daily Discovery Health (9AM), Weekly Security Scan (Fri 5PM), Citation Share-of-Voice, ASIC/Ref-DB Sync (3:15AM), Daily Repo Sync (2:30AM), Weekly Test Report A2Square+AML Hive (Wed 2AM), old Pluto Fleet Monitor (paused).

Keep every AMLHive job on `-1004485329864` — do NOT set them to `local`, the DM (5273126730), or daily_status_v2.

ALL cron jobs that deliver to Telegram now go to the **AMLHive group** (`telegram:-1003834479227`, formerly internal name "daily_status_v2", retitled AMLHive Aug 2026) — NOT the DM (5273126730). 30 jobs updated: 6AM briefing, Sat/Sun reviews, all TapEase + AmLHive fleet monitors (5/11/17/23), daily reports (9:15/9:30 PM), test suites, payout sweep, website monitor, hourly probes, weekly SEO/codex/security scans. Hourly probes are silent when healthy (only ping on issues). Do NOT revert these to `deliver: local` or the DM — Haris explicitly wants daily upd

### Cron Delivery Audit — Consolidated Delivery Rule (June 12, 2026)

**ONE Telegram delivery at 6:00 AM AEST — that's it.** The consolidated morning briefing contains everything: full text briefing + voice audio. No other jobs ping Telegram for morning content.

| Time | Job | Deliver | Why |
|------|-----|---------|-----|
| 4:55 AM | Gmail Ingestor | local | Internal — feeds downstream |
| 5:02 AM | Podcast Insights | local | Internal — content absorbed into 6AM briefing |
| 5:05 AM | Morning Research | local | Internal — feeds synthesis |
| 5:07 AM | Competitor Intel | local | Internal — feeds briefing |
| 5:10 AM | Cross-Chamber Synth | local | Internal — feeds briefing |
| 5:15 AM | Action Bridge | local | Internal — feeds briefing |
| 5:20 AM | Briefing Improver | local | Internal — saves file, consumed by 6AM |
| 5:25 AM | Chamber Refresh | local | Internal — background |
| **6:00 AM** | **★ Briefing (Mon-Fri)** | **origin** | **THE ONE: text + audio → Telegram** |
| **6:00 AM** | **★ Sat Weekly Review** | **origin** | **Weekend retro: perf, repos, signals, builds** |
| **6:00 AM** | **★ Sun System Review** | **origin** | **Proposed — adversarial/blind spots** |
| 6:10 AM | Feedback Loop | local | Internal — background |
| 6:15 AM | Moonshots Learning | local | Internal — background |

Saturday and Sunday replace the daily briefing. The daily pipeline still runs but delivery format changes.

The only exceptions to the ONE-delivery rule:
- **Vercel Monitor** (5:05 AM/PM) — delivers alert emails directly (script sends email, cron stays local)
- **Saturday Weekly Review** (6 AM Sat) — deep retrospective replacing the daily briefing. cron `7d24b37a03f2`. Covers perf, repos, signals, 3 build options, improvements.
- **Sunday System Review** (6 AM Sun, proposed) — adversarial/system health format. Pending confirmation.
- **Voiceover delivery** — every major response (recommendations, proposals, weekly reviews) should include TTS. Use `text_to_speech` + deliver as MEDIA: path. Routine status updates: text only.

## Examples

### GOOD ✅
```
🔴 ACTION: Export YouTube cookies to unblock podcast ingestion
   Time: 2 min | Impact: High — 358 episodes waiting
   Steps: Chrome extension → export → cp to ~/.hermes/youtube_cookies.txt
```

### GOOD ✅
```
🟢 FYI: AML Hive deployed successfully to fly.io
   Why it matters: Production URL is amlhive.com.au — ready for UAT
```

### GOOD ✅ (multi-section)
```
🔴 ACTION: Review ExitLens PR #23 — adds CGT calculator
   Time: 5 min | Impact: Medium — blocks deployment

🟡 DECISION: Socialize ExitLens or TokenPilot this week?
   A) ExitLens — CGT reform in news cycle
   B) TokenPilot — crypto market heating up
```

### BAD ❌
```
📊 372 episodes in 12-month window
   Date range: 20250606 to 20260605
   [1/5] _B4Pv9ttFgY (2026-06-05) — ✅ stored
   [2/5] pmoDeA3RBZY (2026-06-05) — ✅ stored
   Success: 5 | Failed: 0
```
→ This goes to a local file. Not Telegram.

### BAD ❌
```
Background process completed: aie_chamber_ingest.py --limit 100
Exit code: 0 | Output: 372 episodes found
```
→ Silence. Unless there's an action.

## Anti-Patterns to Avoid

- "Let me check on that" — just check, don't announce
- "Here's a progress update" — if no action/decision, silence
- "I've started working on X" — just work, report when done (only if actionable)
- "The process is running" — that's what processes do
- Scorecards with checkmarks and X's — files only
- Tables of any kind in Telegram — use files

## Session Start Checklist

At the start of EVERY session, remind yourself:
1. Every message must earn its place
2. 🔴 ACTION > 🟡 DECISION > 🟢 FYI > silence
3. No tables in Telegram. Period.
4. Cron outputs → local files. Not chat.
5. Process completions → silent unless actionable
6. At most one digest every 2-5 minutes
