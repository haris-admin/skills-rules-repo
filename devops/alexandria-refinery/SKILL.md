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

**Binding operating contract:** `alexandria/vault/_refinery/PLUTO-OPERATING-RULES.md` sits above the
QUEUE — the revised loop, multi-writer coordination, the per-batch pre-commit checklist, and the
rule that prevents each mistake made so far. Read it before working the QUEUE. The whole-vault
audit that motivated it: `alexandria/vault/_refinery/rationalisation-2026-09-09/`.

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
1. `cd ~/.hermes/alexandria` (or your clone), **`git pull --rebase`** — the sync cron writes 4×/day
   (00:15 / 06:15 / 12:15 / 18:15 AEST) and interactive sessions push too. If you were on a stale
   checkout, re-pull. Never start a batch with uncommitted work in the tree from a previous batch.
2. Read `vault/_refinery/PLUTO-OPERATING-RULES.md`, then `vault/_refinery/QUEUE.md` top-to-bottom.
   Pick the highest-priority unchecked task whose preconditions are met. `[ ]` todo · `[~]` in
   progress · `[x]` done · `[!]` blocked. **If a task's premise has drifted** (file counts wrong,
   a named file is gone, a dependency isn't done), fix the QUEUE entry and flag it under NEEDS
   HARIS before working it.
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
- **Merging or retiring a chamber/domain is not done until its feed can no longer regenerate it.**
  A file merge (`git mv` → `_archive/`) must land in the *same commit* as removing that name from
  `vault/_refinery/routing-table.md` and from the chamber-refresh cron's domain list on the WSL
  host. This is the T5.2 mistake — the file was merged, the vocab wasn't, so the stub regenerates.
- **`expires:` sweep is mandatory every weekly pass.** Past-due entry → compress to a one-line
  durable claim or move the block to `_archive/`. As of 2026-09-09 it had never once run and
  69% of tagged chamber entries were past due.

### 3. Verification & close-out (per batch)
1. Secrets scan (PAT / AWS / key / JWT patterns) over the diff. Key *names* fine, values never.
2. `python3 vault/_refinery/` schema check if present; confirm no file lost knowledge (archived, not deleted).
3. Every new/moved file has contract frontmatter; every merge/retire also changed its feed (above).
4. **Commit + push this batch immediately** — one batch = one commit = one push. Do not accumulate
   uncommitted work across batches; that is how collisions and clobbered hand-edits happen.
   `chore(alexandria): refinery — <task> (<n> files)`. Tick the `QUEUE.md` box. Append a
   `progress-log.md` block: `ran / counts (before→after) / decisions / follow-ups`.
5. `git pull --rebase` (union-merge logs/chambers/appends; take newer for structural files, never
   `--force`) `&& git push`.
6. Stop when the queue is drained or a task needs a human decision — record it under **NEEDS HARIS**.
   Never push past a blocker "to keep moving."

## Best Practices & Guidelines

- **Archive, never hard-delete.** Anything uncertain → `alexandria/_archive/` (git-tracked,
  recoverable, RAG-excluded). Only true noise (empty shells, build artifacts, sha256-verified exact
  dups with a surviving copy) is deleted.
- **Conflict order: canonical authority → recency → evidence weight.** Never edit a `canonical: true`
  doc or rewrite another agent's signal — append a new entry with `supersedes:` + `contradiction: true`.
- **Windows-safe filenames only** — no colons, emoji, parens, trailing spaces, variation selectors.
  This is why `slugify_job()` exists; skipping it caused 37 duplicate report-folder pairs and
  Windows checkout failures.
- **Multi-writer reality.** The design intent is single-writer (the WSL sync host), and read-only
  clones elsewhere should make knowledge changes in the local MemPalace store. But in practice the
  sync cron, Pluto, and interactive sessions all commit to `main` — so: `git pull --rebase` before
  every batch; append never overwrite in chambers/logs/`progress-log.md`; check `git log -1 -- <file>`
  before editing a file another writer touched recently; one batch = one push; never `--force`.
  If Pluto does not yet have confirmed push access to `main`, work on a branch `refinery/<task>`
  and open a PR. Full protocol: `PLUTO-OPERATING-RULES.md` §3.
- **Don't point RAG at `alexandria-ops` or `_archive/`.** Retrieval uses Tier 2/3 only.
- Freshness-sampling pitfall from `knowledge-base-maintenance` applies: histogram *all* dates, don't
  sample the head — an actively-fed chamber looks stale if you only read its oldest entries.

## Reference

- `alexandria/vault/_refinery/PLUTO-OPERATING-RULES.md` — **binding operating contract** (loop, multi-writer, checklist)
- `alexandria/vault/_refinery/rationalisation-2026-09-09/` — whole-vault audit + consolidated plan
- `alexandria/vault/decisions/knowledge-architecture-2026-09-08.md` — the ADR (why + full design)
- `alexandria/vault/_refinery/QUEUE.md` — live task list (P1–P8)
- `alexandria/vault/_refinery/alexandria-ops-integration.md` — the ops-repo operating instructions
- `alexandria/vault/_refinery/frontmatter.schema.json` — the enforced contract
- `alexandria/vault/_refinery/routing-table.md` — keyword → domain
- rule: `knowledge-vault-write-contract.md` — the blocking write rules for every agent
- skill: `knowledge-base-maintenance` — the ChromaDB/mempalace counterpart
