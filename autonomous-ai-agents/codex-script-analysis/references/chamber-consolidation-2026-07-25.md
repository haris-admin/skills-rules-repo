# Chamber Consolidation — July 25, 2026

## Summary
Reduced ChromaDB chambers from **27 → 12** by deleting 15 tiny chambers (<15 docs each) that were too sparse for effective retrieval. Updated feeder routing to prevent future bloat.

## Why
- 15 chambers had <15 docs — effectively noise, not signal
- `regulatory-ai` had 56% of all content (2,398/4,069 docs) — single-chamber dominance
- Tiny chambers wasted synthesis compute and degraded cross-chamber retrieval

## After (12 chambers)
regulatory-ai (2,398) · aie-podcast (348) · startup-vc (347) · pluto_research (320) · fintech-aml (226) · cloud-infra (128) · critical-infra (99) · agentic-security (96) · payments-npp (53) · sovereign-ai (29) · agent-architecture (14) · digital-identity (11)

## Deleted Chambers (15)
quantum-computing, space-tech, ai-frontier, coding-agents, legal-professional, data-sovereignty, insurtech, accelerators, events-sydney, regtech-tools, cloud-frontier, agent-observability, startup-funding, voice-creative, market-signals

## Feeder Changes
- `pluto_chamber_refresh.py`: `digital-identity` routing changed to `fintech-aml`
- No other feeder changes needed

## Design Principle
Do not create new chambers for topics that will receive <20 docs. Use existing chambers.
