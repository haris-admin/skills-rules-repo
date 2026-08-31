# MemPalace 16-Chamber Architecture

**Built:** May 25, 2026
**Status:** Operational (16/16 chambers populated, 87 chamber docs + 219 legacy)

## Chamber Taxonomy

| # | Chamber | Docs | Description |
|---|---------|------|-------------|
| 1 | `regulatory-ai` | 13 | AI Regulation & Compliance — EU AI Act, AU guardrails, global governance |
| 2 | `fintech-aml` | 4 | FinTech & AML/CTF — AUSTRAC, Tranche 2, KYC, CDD, BNPL |
| 3 | `agentic-security` | 9 | Agentic AI Security — red-teaming, OWASP LLM, A2A protocol |
| 4 | `cloud-infra` | 4 | Cloud & Infrastructure — repatriation, AWS/GCP/Azure, colo |
| 5 | `digital-identity` | 3 | Digital Identity — AGDIS, CDR, TDIF, verifiable credentials |
| 6 | `data-sovereignty` | 3 | Data Sovereignty & Privacy — CPS 234, SOCI Act, Privacy Act |
| 7 | `startup-vc` | 3 | Startup & VC Ecosystem — AU startups, funding, exits |
| 8 | `sovereign-ai` | 20 | Sovereign AI & Government — local AI, AUKUS, procurement |
| 9 | `regtech-tools` | 3 | RegTech Platforms — compliance workflow, RegStack |
| 10 | `agent-architecture` | 7 | Agent Architecture & Skills — patterns, SKILL.md, tools |
| 11 | `payments-npp` | 3 | Payments & NPP — PayTo, BNPL, merchant acquiring |
| 12 | `insurtech` | 3 | InsurTech & Insurance — distribution reforms, CPS 230 |
| 13 | `agent-observability` | 3 | Agent Observability & SRE — monitoring, AgentSRE |
| 14 | `critical-infra` | 3 | Critical Infrastructure & OT — mining, energy, SOCI |
| 15 | `legal-professional` | 3 | Legal & Professional Services — LegalTech, accounting |
| 16 | `voice-creative` | 3 | Voice, Audio & Creative AI — TTS, AI music, creative tools |

## Per-Source Chambers (Ad-Hoc)

Beyond the 16 domain chambers, **per-source chambers** can be created on-the-fly for dedicated single-source knowledge bases. These auto-create when feeding to a new `--chamber` name — no `seed_chambers.py` needed.

| Chamber | Source | Docs | Description |
|---------|--------|------|-------------|
| `aie-podcast` | @aiDotEngineer | 1 (seed) | AI Engineer podcast — 372 episodes in 12-month window, ~1 ep/day, covers agents/MCP/evals/coding agents |

**Creation pattern:**
```bash
# Auto-creates the chamber on first feed — no pre-creation step needed
python3 pluto_mempalace_feeder.py --input seed.json --chamber aie-podcast
```

Per-source chambers don't participate in domain keyword auto-routing. They're queried directly by name and picked up automatically by the cross-chamber synthesizer.

## How It Was Built

### Phase 1: Collection Creation
```bash
# All 16 chambers created as ChromaDB collections with metadata and descriptions
python3 ~/.hermes/scripts/seed_chambers.py  # creates collections + seeds
```

### Phase 2: Migration from Legacy
Existing docs in `pluto_research` (53 docs across 9 topics) were redistributed:
- `AI Regulation & Compliance 2026` + `EU AI Act` → `regulatory-ai`
- `Agentic AI Security 2026` + `A2A Protocol` → `agentic-security`
- `Cloud Repatriation & AU FinTech 2026` → `cloud-infra` (primary) + `fintech-aml` (dual-mapped copy)
- `Skills Ecosystem` + `Zero Language Progress` → `agent-architecture`
- `Opportunity #3: LocalStack` → `sovereign-ai`

### Phase 3: Seeding Empty Chambers
10 empty chambers received 3 seed documents each (30 total), populated from:
- Portfolio review analysis (VerifyLink → digital-identity, PitGuard → critical-infra)
- GenSparks report (RegStack → regtech-tools, AgentSRE → agent-observability)
- Fleet infrastructure knowledge (voice overviews → voice-creative)

## Feeder v2.0 — Chamber-Aware Operations

### Auto-Routing
```python
route_to_chamber(topic, tags) → chamber_name
```
Uses keyword matching against chamber keywords + legacy topic map. Fallback: `pluto_research`.

### New CLI Flags
```bash
# Feed to specific chamber
python3 pluto_mempalace_feeder.py --input data.json --chamber fintech-aml

# Search specific chamber
python3 pluto_mempalace_feeder.py --query "AML" --chamber fintech-aml

# Cross-chamber search (default)
python3 pluto_mempalace_feeder.py --query "sovereign AI"

# List all chambers
python3 pluto_mempalace_feeder.py --list-chambers

# Full status with per-chamber breakdown
python3 pluto_mempalace_feeder.py --status
```

## Related Scripts
- `~/.hermes/scripts/pluto_mempalace_feeder.py` — v2.0 feeder with chamber support
- `~/.hermes/scripts/seed_chambers.py` — reproducible chamber seeding (30 seed docs)

## Data Flow (Updated)

```
Research Request → mempalace-inputs/*.md → mempalace_watcher.py (cron: */5m)
    ↓
route_to_chamber(topic, tags) → target chamber collection
    ↓
ChromaDB: regulatory-ai | fintech-aml | agentic-security | ... (16 chambers)
    ↓
search_mempalace(query, chamber=None) → cross-chamber semantic search
    ↑
Gumby (PS) → WSL → gumby_mempalace_query.py (needs --chamber support update)
```
