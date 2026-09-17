# Garry Tan's GBrain Architecture Specification

Technical specification for Garry Tan's **GBrain** (`garrytan/gbrain`), the open-source AI agent memory and "Company Brain" knowledge engine.

---

## 1. The Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ 1. INGESTION LAYER                                          │
│    Markdown notes, Slack transcripts, Gmail, GitHub commits │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. DUAL-INDEX STORAGE (PostgreSQL + pgvector)               │
│    • BM25 Lexical Index (Keywords, names, commit hashes)    │
│    • Vector Embeddings (Semantic concepts, intent)          │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. HYBRID RETRIEVAL (Reciprocal Rank Fusion - RRF)          │
│    Blends keyword precision with semantic breadth           │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. SELF-WIRING KNOWLEDGE GRAPH                              │
│    Automatic entity extraction (People, Projects, Partners) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. THE DREAM CYCLE (Overnight Memory Consolidation)         │
│    Background cron reconciles links, prunes stale memory    │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Reciprocal Rank Fusion (RRF) Formula

GBrain computes hybrid search ranking without relying on arbitrary score weighting:

$$RRF\_Score(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$

Where:
- $M$: Set of ranking algorithms (BM25 and vector cosine similarity).
- $r_m(d)$: Rank of document $d$ in algorithm $m$ (1-indexed).
- $k$: Smoothing constant (standard default is $k = 60$).

---

## 3. Model Context Protocol (MCP) Integration

GBrain exposes standard MCP tools for agents (Claude Code, Hermes, Pluto, Codex):
- `gbrain_search(query, filter_entity, limit)`: Performs hybrid RRF search.
- `gbrain_remember(content, tags, entity)`: Writes new knowledge into the markdown index.
- `gbrain_graph_traverse(entity_id, depth)`: Walks related companies, people, and repos.
