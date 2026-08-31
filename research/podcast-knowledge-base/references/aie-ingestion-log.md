# AI Engineer Podcast Ingestion — Session Log (June 8, 2026)

## Channel
- **Handle:** @aiDotEngineer
- **Channel ID:** UCLKPca3kwwd-B59HNr-_lvA
- **Episodes in 12-month window:** 372 (June 2025–June 2026)
- **Chamber:** aie-podcast (ChromaDB)

## Session Summary

| Run | Command | Offset | Limit | Success | Failed | Notes |
|-----|---------|--------|-------|---------|--------|-------|
| 1 | aie_chamber_ingest.py --limit 5 | 0 | 5 | 5 | 0 | Initial test batch |
| 2 | aie_chamber_ingest.py --limit 10 | 0 | 10 | 9 | 1 | Ep 10 (504PvfXou5Y) failed |
| 3 | aie_chamber_ingest.py --limit 50 (bg) | 0 | 50 | 4 | 0 | Background, killed mid-run |
| 4 | aie_chamber_ingest.py --limit 40 (fg) | 0 | 40 | 0 | 40 | IP blocked entirely |
| 5 | aie_continue.py 11 15 | 11 | 15 | 5 | 6 | Auto-aborted at 5 consecutive fails |
| **Total** | | | | **14 unique** | | **~358 remaining** |

## Key Findings

1. **IP block pattern:** 14-18 successful transcript downloads per session window, then hard block
2. **Auto-abort works:** Correctly stops at 5 consecutive failures — prevents wasted time
3. **Foreground-only execution:** Background processes buffer output silently even with `-u`. Must use foreground with smaller chunks (~40 episodes = ~5-7 min)
4. **Offset continuation works:** `aie_continue.py` correctly skips already-processed episodes
5. **Cookies are the permanent fix:** The IP block game is unwinnable — browser cookies bypass entirely

## Episodes Ingested (newest first)

1. _B4Pv9ttFgY — Building Agent Interfaces: Lessons from Chrome DevTools (MCP) — Michael Hablich, Google
2. pmoDeA3RBZY — Dark Factory: OpenClaw Ships Faster Than You Can Read the Diff — Vincent Koc
3. mFLlVpnGpds — Beyond Transcription: Building Voice AI That Understands — Hervé Bredin
4. r305-aQTaU0 — Text Diffusion — Brendon Dillon, Google DeepMind
5. iNkFlCiij0U — The Art & Science of Benchmarking Agents — Vincent Chen, Snorkel AI
6. wcUJWP6WpGM — SWE-rebench: Lessons from Evaluating Coding Agents — Ibragim Badertdinov, Nebius
7. NmjGfdZLNIs — AI Engineer Melbourne 2026 Keynote Livestream | Day 2
8. hCMrEfPG2Yg — Beyond Components: Designing Generative UI for MCP Apps — Ruben Casas, Postman
9. zKk7sDMGDEQ — Benchmarking semantic code retrieval on Claude Code — Kuba Rogut, Turbopuffer
10. HvZXAOZ3iv8 — What Lies Beneath the API — Benjamin Cowen, Modal
11. YYH0DMQr30A — Task Fidelity Scaling Laws — Kobie Crawdord, Snorkel
12. KA5kPbdkK2E — How Lovable self-improves every hour — Benjamin Verbeek, Lovable
13. hqHC6Z_lXyo — 20 days of compute vs 7 hours — Bertrand Charpentier, Pruna
14. u-rJwPPU3QA — How to talk to statues — Joe Reeve, ElevenLabs

## Failed Episodes (need retry)

- 504PvfXou5Y — BDD, ADR, PRD, WTF: Capturing Decisions
- BM2JX9hqsVQ — What if the network was the sandbox? — Tailscale
- NuePCNMpWGc — Can LLMs generate Enterprise Quality Code? — Sonar
- N7b1PJc7SFc — Engineering voice agents — Together AI
- UQKg0td-Bf4 — Spec-Driven Testing for Agents — SafeIntelligence
- vy7o1g2iHY8 — How I deleted 95% of my agent skills — WorkOS
- phchDt63qAA — How We Built Zeta2 — Zed
