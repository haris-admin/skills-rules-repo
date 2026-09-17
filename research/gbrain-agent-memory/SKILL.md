---
name: gbrain-agent-memory
description: >-
  Query, ingest, and consolidate persistent AI agent memory using Garry Tan's GBrain architecture, hybrid search (BM25 + pgvector + Reciprocal Rank Fusion), self-wiring entity graphs, and overnight Dream Cycle consolidation. Use when equipping AI agents with company memory, retrieving cross-project knowledge, configuring MCP memory servers, or preventing agent amnesia across sessions.
---

# Garry Tan's GBrain Agent Memory Architecture

A persistent, markdown-first AI agent memory system inspired by Garry Tan's **GBrain** (`garrytan/gbrain`), enabling autonomous agents to store, retrieve, and cross-reference company knowledge without amnesia.

## When to Use

- **Agent Memory Across Sessions**: When an AI agent needs persistent recall of past decisions, architecture specifications, and project context.
- **Hybrid Knowledge Retrieval**: When queries require exact keyword precision (commit hashes, company names, code symbols) combined with semantic conceptual recall.
- **Company Brain Engineering**: When organizing company-wide knowledge (Notion, markdown vaults, Slack, emails) so agent fleets can take action safely.
- **Dream Cycle Optimization**: When running overnight background jobs to reconcile links, deduplicate facts, and update knowledge graph edges.

---

## Core Memory Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ 1. INGESTION: Markdown files, meeting notes, project docs   │
├─────────────────────────────────────────────────────────────┤
│ 2. DUAL INDEXING: BM25 Lexical + PostgreSQL pgvector        │
├─────────────────────────────────────────────────────────────┤
│ 3. HYBRID RETRIEVAL: Reciprocal Rank Fusion (RRF, k=60)     │
├─────────────────────────────────────────────────────────────┤
│ 4. ENTITY GRAPH: Auto-linked nodes (Companies, Repos, People│
├─────────────────────────────────────────────────────────────┤
│ 5. DREAM CYCLE: Background overnight memory consolidation   │
└─────────────────────────────────────────────────────────────┘
```

---

## GBrain Hybrid Retrieval CLI

Run the bundled simulator to evaluate hybrid search and Dream Cycle memory states:

```bash
# Perform hybrid search query across venture memory
python3 research/gbrain-agent-memory/scripts/query_gbrain.py \
  --query "dispute resolution and neurodivergent accessibility"

# Inspect overnight Dream Cycle consolidation status
python3 research/gbrain-agent-memory/scripts/query_gbrain.py --dream-cycle

# Output machine-readable JSON for agent tools
python3 research/gbrain-agent-memory/scripts/query_gbrain.py --demo --json
```

See [query_gbrain.py](./scripts/query_gbrain.py) for the underlying RRF ranking algorithm.

---

## Architectural Guardrails

1. **Markdown as Source of Truth**: Never lock agent memories inside proprietary vector databases without human-readable markdown backing. All entities must be inspectable by human engineers.
2. **Hybrid RRF Priority**: Never rely purely on dense vector embeddings. Technical terms, acronyms (e.g. ASIC, AUSTRAC, MID, POS), and proper names fail under pure semantic search; BM25 balances this weakness.
3. **Overnight Consolidation**: Heavy graph restructuring, link inference, and vacuuming should execute during the **Dream Cycle** to avoid degrading interactive agent latency.

For the full system specification, see [GBrain Architecture Spec](./references/gbrain-architecture-spec.md).
