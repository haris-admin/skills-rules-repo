# Morning Briefing v2 — Design Rationale

## Why v2 Exists

On June 8, 2026, Haris told Pluto: "I haven't been wowed by Hermes yet."

The v1 briefing (June 5 example) was 190 lines — a comprehensive research report with equal-weight signals, portfolio impact matrices, LinkedIn posts, blog ideas, timeline tables, and delivery logs. Actions were buried at line 167. Haris, a founder with a full-time day job building fintech products at night, couldn't extract "what matters today" in the 60 seconds he had for morning reading.

## Design Principles (Honcho-Derived)

These principles were NOT invented — they were mined from Haris's observed behavior patterns in Honcho:

| Pattern | Source | Design Response |
|---------|--------|-----------------|
| Uses 🔴/🟡/🟢 color-coded triage in briefings | High-confidence Honcho pattern | Briefing leads with color-coded action checklist |
| Prefers checklists as lead magnets | Observed in product strategy | "Your 3-Minute Checklist" section |
| Uses voice memos as primary medium | Medium-confidence Honcho pattern | Voice overview linked in footer |
| Structured Hook/Angle/CTA for LinkedIn | Medium-confidence pattern | LinkedIn posts moved to separate research output, not brief |
| Time-poor, day job + building | Explicit user preference | 60-second scan target, 73-line max |
| "Overwhelmed by noise" — June 8 | Direct user feedback | No tables, no batch logs, no progress bars |
| Wants to be "surprised" | Direct user request (Option C) | "Didn't Know That" section — one cross-signal insight per briefing |
| Balanced approach over ultra-compact | User preference | ~73 lines, not 40 — enough depth but scannable |

## Section-by-Section Rationale

### Portfolio Pulse (NEW — top of briefing)
**Why:** Haris manages 7 projects simultaneously. He needs to know which ones are HOT before reading any details. A 5-word scan tells him "ExitLens, AML Hive, PayLicence are hot today."

### The ONE Thing Today (NEW)
**Why:** v1 presented 5 equal-weight signals. A founder doesn't have time to triage — the briefing should triage FOR him. The single most important thing goes here, with the project name and deadline.

### 3-Minute Checklist (NEW — top of briefing)
**Why:** Haris gravitates toward checklists (observed in his product strategy — checklists as lead magnets). Giving him a checkbox list he can mentally tick off in 60 seconds respects his time.

### Today's Signals (CONDENSED from v1)
**Why:** v1 had full paragraphs per signal with "For Haris:" callouts, confidence levels, and source lists. v2 condenses to: icon + title → portfolio hit + one-line summary. The full detail is linked as a separate file.

### Didn't Know That (NEW)
**Why:** Haris asked to be "surprised." This section finds one cross-signal connection he wouldn't have made himself — e.g., "4 projects have HOT signals simultaneously for the first time in 20 years."

### Make Tomorrow Better (NEW)
**Why:** The v1 briefing had no feedback loop — it was generated, sent, and forgotten. This section asks one improvement question (rotating through 7 options) that shapes tomorrow's briefing based on Haris's reply.

## What v2 REMOVED from v1

| Section | Why Removed |
|---------|-------------|
| Portfolio Impact Matrix (7×7 table) | Tables violate communication protocol; moved to full report file |
| LinkedIn Posts (4 per briefing) | Moved to separate LinkedIn ideas output — not a morning read |
| Blog Post Ideas (3 per briefing) | Moved to content pipeline, not morning brief |
| Timeline & Actions table | Replaced by "3-Minute Checklist" at top |
| Delivery Log | Operational detail, not actionable for Haris |
| Signal Balance Audit | Academic detail; the briefing itself is the balanced view |
| "For Haris:" callouts | Integrated into checklist items |

## The Self-Improving Loop

Seven improvement questions rotate daily:
1. Actions at the VERY top (line 1)?
2. 3 deeper signals vs 5 surface?
3. Voice-first briefing (90s audio) vs text?
4. One project deep-dive per day vs all 7?
5. Competitor intel section?
6. Surprise section actually surprising?
7. Different weekend format?

Haris replies with a letter (A/B/C). The `briefing_improver.py` engine tracks responses over 30 days and adapts the template. This means the briefing gets better every day without Haris having to explicitly "configure" anything.
