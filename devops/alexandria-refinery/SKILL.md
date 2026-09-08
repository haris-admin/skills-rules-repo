---
name: alexandria-refinery
description: >-
  Operating procedure for the Alexandria knowledge-vault refinery — the 4-tier
  markdown curation pipeline that keeps the shared fleet vault
  (github.com/haris-admin/alexandria) clean as agents push into it 4+ times a
  day. Use when running the refinery queue, adding a note to Alexandria,
  deciding what tier/frontmatter a note gets, deduping report exhaust, evicting
  cron output to alexandria-ops, or building weekly rollups. Companion to
  knowledge-base-maintenance (that skill is the ChromaDB/mempalace side; this is
  the markdown-vault side).
version: 1.0.0
author: Pluto
tags: [alexandria, knowledge-base, refinery, markdown, obsidian, dedup, curation, fleet-ops]
---

# Alexandria Refinery

> *Alexandria is a refinery, not a dumpster — find the diamonds in the dirt.*

`github.com/haris-admin/alexandria` is the fleet's shared knowledge vault (Markdown-first,
Obsidian-compatible). Many agents drain notes, research, and cron output into it. Without a
lifecycle it bloats — as of 2026-09-08 it held ~3,860 `.md` / 56 MB in `vault/`, **89% disposable
cron exhaust**, 1,288 byte-identical duplicate report files, ~550 empty shells, near-zero
frontmatter, single facts re-typed across 13+ files.

The fix is a **4-tier refinery** with an enforced frontmatter contract, TTL + rollups on exhaust,
and a hand-curated Map-of-Content layer. Authority: `alexandria/vault/decisions/knowledge-architecture-2026-09-08.md`.
The live task list is `alexandria/vault/_refinery/QUEUE.md`.

## When to Use

- Running / resuming the refinery queue (`alexandria/vault/_refinery/QUEUE.md`)
- Deciding where an incoming note lands (which tier, which folder, what frontmatter)
- Deduping or auditing `alexandria/vault/` (markdown — not the ChromaDB palace)
- Migrating cron output to `alexandria-ops`, or building weekly rollup digests
- Patching `alexandria_sync.py` for slug-normalisation / frontmatter stamping / tiered routing
- Onboarding a new agent that will write to Alexandria (point it at `knowledge-vault-write-contract.md`)

## The 4 tiers

| Tier | Contents | Lifecycle | RAG-indexed |
|---|---|---|---|
| 0 Ephemeral | cron / monitor / test output | evicted to `alexandria-ops`; 14–90 d TTL there | no |
| 1 Raw / Intake | agent queue drains, research digests, weekly rollups | 90-day TTL → promote or `_archive/` | low priority |
| 2 Refined / Log | `chambers/` signal-logs, `refined/keep/` diamond layer | curated, deduped, swept on cadence | **primary corpus** |
| 3 Canonical | `canonical/decisions/` (ADRs), `canonical/reference/`, `00-maps/` | one doc per topic, human-reviewed, **agents never overwrite** | highest authority |

Full folder layout + the frontmatter JSON-Schema: [references/tier-and-frontmatter-contract.md](./references/tier-and-frontmatter-contract.md).

## Step-by-Step Procedure

### 1. Preparation
1. `cd ~/.hermes/alexandria` (or your clone), `git pull`.
2. Read `vault/_refinery/QUEUE.md` top-to-bottom. Pick the highest-priority unchecked task whose
   preconditions are met. `[ ]` todo · `[~]` in progress · `[x]` done · `[!]` blocked.
3. Read `vault/_refinery/progress-log.md` tail for where the last batch stopped.

### 2. Core execution — work in bounded batches
A batch = **one job folder, one chamber, or ≤200 files**. Never attempt the whole vault in one
pass — cost must scale with new-work, not vault size.

- **Routing an incoming note** (no LLM needed for the common case): land it verbatim → run the
  deterministic normalizer (add frontmatter, sha256 body hash, drop empty/transient shells, infer
  `type` from source, infer `domain[]` from `vault/_refinery/routing-table.md` keyword table) →
  the weekly distill pass promotes durable claims to Tier 2.
- **Dedup:** exact first — only delete where `(path-family, title, sha256 body)` is identical and
  there are ≥2 copies; keep the earliest, union the provenance. Then near-dup (MinHash/LSH →
  embedding cosine) — **write a report and get human confirmation before merging near-dups.**
  (Same safe-dedup rule as `knowledge-base-maintenance`.)
- **Cron exhaust:** it does not belong in the knowledge vault. Evict to
  `github.com/haris-admin/alexandria-ops` (see `alexandria/vault/_refinery/alexandria-ops-integration.md`).
  Keep only `vault/reports/_rollups/<job-slug>/YYYY-Www.md` weekly digests in Alexandria.
- **Chamber consolidation / canonical facts:** a fact appearing in ≥3 chambers gets **one**
  canonical entry in `canonical/reference/` and `↗` links from the chambers (keep only the
  chamber-specific implication inline).

### 3. Verification & close-out (per batch)
1. Secrets scan (PAT / AWS / key / JWT patterns) over the diff. Key *names* fine, values never.
2. `python3 vault/_refinery/` schema check if present; confirm no file lost knowledge (archived, not deleted).
3. Commit: `chore(alexandria): refinery — <task> (<n> files)`. Tick the `QUEUE.md` box. Append a
   `progress-log.md` block: `ran / counts (before→after) / decisions / follow-ups`.
4. `git pull --rebase && git push`.
5. Stop when the queue is drained or a task needs a human decision — record it under **NEEDS HARIS**.

## Best Practices & Guidelines

- **Archive, never hard-delete.** Anything uncertain → `alexandria/_archive/` (git-tracked,
  recoverable, RAG-excluded). Only true noise (empty shells, build artifacts, sha256-verified exact
  dups with a surviving copy) is deleted.
- **Conflict order: canonical authority → recency → evidence weight.** Never edit a `canonical: true`
  doc or rewrite another agent's signal — append a new entry with `supersedes:` + `contradiction: true`.
- **Windows-safe filenames only** — no colons, emoji, parens, trailing spaces, variation selectors.
  This is why `slugify_job()` exists; skipping it caused 37 duplicate report-folder pairs and
  Windows checkout failures.
- **The single writer pushes.** `alexandria` and `alexandria-ops` are both written by the WSL sync
  host. Read-only clones everywhere else — make knowledge changes in the local MemPalace store; the
  next sync brings them here.
- **Don't point RAG at `alexandria-ops` or `_archive/`.** Retrieval uses Tier 2/3 only.
- Freshness-sampling pitfall from `knowledge-base-maintenance` applies: histogram *all* dates, don't
  sample the head — an actively-fed chamber looks stale if you only read its oldest entries.

## Reference

- `alexandria/vault/decisions/knowledge-architecture-2026-09-08.md` — the ADR (why + full design)
- `alexandria/vault/_refinery/QUEUE.md` — live task list (P1–P8)
- `alexandria/vault/_refinery/alexandria-ops-integration.md` — the ops-repo operating instructions
- `alexandria/vault/_refinery/frontmatter.schema.json` — the enforced contract
- `alexandria/vault/_refinery/routing-table.md` — keyword → domain
- rule: `knowledge-vault-write-contract.md` — the blocking write rules for every agent
- skill: `knowledge-base-maintenance` — the ChromaDB/mempalace counterpart
