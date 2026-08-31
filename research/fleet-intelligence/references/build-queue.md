# Pluto Build Queue

## Location
`~/.hermes/mempalace-inputs/.build-queue/BUILD_QUEUE.md`

## Structure
```
.build-queue/
├── BUILD_QUEUE.md    ← Master registry (this reference describes it)
├── active/           ← Projects currently being built (max 2 at once)
├── staged/           ← Ready to build, scored and prioritized
├── completed/        ← Shipped and live
└── archived/         ← Frozen — revisit Q3 2026+
```

## How to Read the Queue

Each project entry tracks:
- **Score:** Gumby 1000-point or GenSparks composite score
- **Domain:** Which sector/industry
- **Status:** Active / Staged / Queued / Frozen
- **Hook:** Why now — the timing signal that makes this urgent

## Current Active Projects (June 2026)

| # | Project | Status |
|---|---------|--------|
| 1 | AML Hive (amlhive.com.au) | 🔨 Building |
| 2 | ExitLens AU (esop.harishabib.au) | ✅ LIVE |
| 3 | TokenPilot AU | 🔨 Active |

## Moving Projects Between States

To move a project from staged → active:
1. Verify the BUILD_QUEUE.md shows it in staged
2. Research any new signals that strengthen/weaken the case
3. Create go-to-market collateral (one-pager, landing page, pitch)
4. Move the entry to active in BUILD_QUEUE.md
5. Create the project repo if not already present

## Portfolio Decision Rules

- **Max 2 active builds** — AML Hive is always slot 1. Queue picks slot 2.
- **Content-first for new entries** — $250 MVP, validate demand before SaaS.
- **Portfolio synergy wins** — projects that feed each other (RegIntel → AML Hive, TokenPilot → RegStack) get priority.
- **Timing window is everything** — July 1 Tranche 2 deadline, July 2 CGT Senate inquiry, Neo-X AFSL validation period.
