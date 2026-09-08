# Alexandria — tiers, folder layout, frontmatter contract

Detail for the [alexandria-refinery](../SKILL.md) skill. Canonical copies live in the Alexandria
repo itself (`vault/decisions/knowledge-architecture-2026-09-08.md`,
`vault/_refinery/frontmatter.schema.json`) — this is the working summary.

## Target folder layout (`vault/`)

```
vault/
├── 00-maps/               # one MOC per domain + _home.md (hand frame + Dataview blocks)
├── canonical/
│   ├── decisions/         # ADRs — NNNN-slug.md
│   └── reference/         # canonical fleet fact-sheets (e.g. au-regulatory-calendar.md)
├── chambers/              # append-only sector signal-logs (newest at bottom, ### YYYY-MM-DD)
├── refined/<section>/{keep,archive}/   # distilled diamond layer
├── inputs/YYYY/MM/        # Tier 1 raw intake, 90-day TTL
├── reports/
│   ├── _rollups/<job-slug>/YYYY-Www.md   # weekly cron digests (the only report content kept)
│   └── README.md          # pointer — raw runs now in alexandria-ops
├── mempalace/ · openclaw-memory/ · honcho/   # external mirrors, read-only
└── (repo root) _archive/  # cold storage, git-tracked, recoverable, RAG-excluded
```

## Frontmatter contract

Every non-mirror `.md` in `vault/` (outside `mempalace/`, `openclaw-memory/`, `honcho/`,
`_archive/`) carries:

```yaml
---
id: 20260908-amlhive-stone-chalk-au-ai      # YYYYMMDD-kebab-slug, stable, path-independent
title: …
tier: canonical | refined | log | raw | ephemeral
type: signal | intel | research | digest | reference | adr | moc | report
domain: [fintech-payments, regulatory]      # controlled vocab == chamber slugs (+ fleet-ops, meta)
status: seedling | budding | evergreen | archived   # REQUIRED for tier canonical|refined
source: perplexity | claude-daily | cron:<job-id> | agent:<name> | <url> | human
source_url: …                               # REQUIRED when source is external
created: 2026-09-08
updated: 2026-09-08
expires: 2026-12-08                          # REQUIRED for tier raw|ephemeral + time-boxed signals
confidence: high | medium | low             # REQUIRED for type signal|intel|research
canonical: false                            # true = the one source-of-truth doc on a claim
supersedes: []                              # IDs this note replaces
superseded_by: …                            # ID that replaced this note
contradiction: false                        # true = needs human resolution
owner: gumby | pluto | hermes | mercury | haris   # → CODEOWNERS
sha256: …                                   # body hash (frontmatter excluded); set by normalize.py
---
```

Chamber per-entry header standard: `### 2026-09-08 · signal · confidence:high · expires:2026-12-08`.

## Naming

- Dated entries: `YYYY-MM-DD__slug.md`
- Evergreen / reference / MOC: `slug.md`
- ADRs: `NNNN-slug.md`
- Report runs (in alexandria-ops): `<job-slug>/YYYY-MM-DD_HH-MM-SS.md`
- No spaces, colons, emoji, parens, trailing spaces, or variation selectors — anywhere.

## Promotion / demotion rules

| From → To | Trigger |
|---|---|
| ephemeral → (rollup) | weekly `rollup.py` per job; raw run then TTL-pruned |
| raw → refined | weekly distill pass: a claim is durable, sourced, still true |
| refined → canonical | same fact in ≥3 chambers, or a decision is made → one `canonical/reference/` or `canonical/decisions/` doc |
| any → _archive/ | past `expires`, superseded, or source retired — **move, never delete** |

## Automated curation scripts (all delta-scoped)

`normalize.py` (every sync, deterministic) · `rollup.py` (weekly per job) · `prune.py` (daily TTL
sweep) · `dedup.py` (weekly, exact then human-confirmed near-dup) · weekly LLM "refinery/Dreams"
pass (promote / supersede / build canonical) · `audit.py` (weekly, runs the
`knowledge-base-maintenance` blind-spot checks).
