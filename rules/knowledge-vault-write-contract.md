# Knowledge-vault write contract — Alexandria (all agents)

Applies whenever any agent (Claude, Codex, Gemini/Antigravity, Hermes/Pluto/Mercury/Gumby) writes
to the shared fleet knowledge vault **`github.com/haris-admin/alexandria`** — directly, through
`alexandria_sync.py`, or by draining a local MemPalace queue that ends up there.

Authority: `alexandria/vault/decisions/knowledge-architecture-2026-09-08.md` (ACCEPTED 2026-09-08).
Operating procedure: skill `alexandria-refinery` + `alexandria/vault/_refinery/PLUTO-OPERATING-RULES.md`
(the binding loop + multi-writer coordination + per-batch checklist). This card is the blocking subset.

## Why this exists

By 2026-09-08 the vault had grown to ~3,860 `.md` / 56 MB with **89% disposable cron exhaust**,
1,288 byte-identical duplicate report files (a folder-rename bug), ~550 empty `[]`/`[SILENT]`
shells, near-zero frontmatter, and single facts ("1 July 2026 supercycle", "Tranche 2", "CPS 230")
re-typed across 9–13 files each. The vault is a refinery, not a dumpster — these rules keep the
signal-to-noise ratio from collapsing again as push volume grows.

## The hard rules

1. **Cron / monitor / test output does not go in `alexandria`.** It goes to
   `github.com/haris-admin/alexandria-ops`. Only weekly rollup digests
   (`vault/reports/_rollups/<job-slug>/YYYY-Www.md`) belong back in the knowledge vault. If you are
   adding a scheduled job that writes a report, wire its output to `alexandria-ops` from the start
   (see `alexandria/vault/_refinery/alexandria-ops-integration.md`) — do not add a new
   `vault/reports/<job>/` folder.

2. **Every non-mirror file carries frontmatter** matching
   `alexandria/vault/_refinery/frontmatter.schema.json`. Minimum: `id` (`YYYYMMDD-kebab-slug`,
   stable, never reused), `title`, `tier`, `type`, `domain[]`, `source`, `created`, `updated`.
   Plus `status` for tier `canonical`/`refined`; `expires` for tier `raw`/`ephemeral`; `confidence`
   for type `signal`/`intel`/`research`; `source_url` when the source is external. A file with no
   frontmatter is not a valid vault entry.

3. **Windows-safe filenames and folder names — no exceptions.** No spaces, colons, emoji,
   parentheses, trailing spaces, or Unicode variation selectors, anywhere in a path. Windows git
   cannot check out a colon or a trailing space and this has already caused phantom-deletion
   incidents. Job folders must be slug-normalised (`slugify_job()` in `alexandria_sync.py`) —
   `🪐 CoS Follow-up Check (9:30 AM + 2:30 PM)` and `CoS Follow-up Check (930 AM + 230 PM)` must
   resolve to the **same** slug, or you get a duplicate-folder pair.

4. **Archive, never hard-delete knowledge.** Stale, superseded, or orphaned material moves to
   `alexandria/_archive/` (git-tracked, recoverable, excluded from RAG and the Obsidian vault).
   The only things deleted outright: empty shells (`[]` / `[SILENT]` / `None` / < 120 chars of
   non-boilerplate), build artifacts, and exact duplicates — where **exact** means
   `(path-family, title, sha256 of body)` is identical and a copy survives. Never delete on title
   similarity alone (generic titles are a labelling problem, not a duplication proof — see
   `knowledge-base-maintenance`).

5. **Append, don't edit — and never overwrite another agent's entry or a `canonical: true` doc.**
   Chamber entries are appended under a `### YYYY-MM-DD` heading, newest at the bottom. On a
   conflict, resolution order is **canonical authority → recency → evidence weight**; you record
   the disagreement by appending a new entry with `supersedes:` and `contradiction: true`, which
   surfaces in the review queue — you do not silently rewrite what another agent wrote.

6. **Cite, don't bloat.** A short entry with a `source_url` beats long prose. A fact that already
   exists in a chamber or `canonical/reference/` gets a `↗` link, not a re-statement. A fact
   appearing in ≥3 chambers must be promoted to one `canonical/reference/` entry.

7. **Same guardrails as everywhere else.** No secrets (PAT / AWS / key / JWT values — names are
   fine). No PII, no AML client records — Australian data boundary, aggregate/summarise only. No
   history rewrites, no force-push. Full secret scan before every commit — cron output sometimes
   echoes env.

8. **Single-writer by design; coordinate for real.** The intent is that only the WSL sync host
   pushes `alexandria` / `alexandria-ops`, and everywhere else the repo is read-only knowledge —
   make the change in the local MemPalace store and let the next sync carry it in. In practice the
   sync cron, Pluto, and interactive sessions do all commit to `main`, so whenever you *do* write
   directly: `git pull --rebase` before every batch; **append, never overwrite** another writer's
   entry; check `git log -1 -- <file>` before editing a file touched recently; one batch = one
   commit = one push (never accumulate); never `--force`; and if you conflict on a log/chamber,
   keep **both** sides. Full protocol: `alexandria/vault/_refinery/PLUTO-OPERATING-RULES.md` §3.

9. **A merge/retire is not done until its feed changes too.** Merging a chamber (`git mv` →
   `_archive/`) must land in the same commit as removing that name from `_refinery/routing-table.md`
   and the chamber-refresh cron's domain list — otherwise the next sync regenerates the stub.

## Tier placement (where a new note lands)

| Tier | Folder | For |
|---|---|---|
| ephemeral | *(alexandria-ops)* | cron/monitor/test runs |
| raw | `vault/inputs/YYYY/MM/` | agent queue drains, research digests, rollups |
| refined | `vault/chambers/`, `vault/refined/<section>/keep/` | curated, deduped, sourced knowledge |
| canonical | `vault/canonical/decisions/`, `vault/canonical/reference/`, `vault/00-maps/` | one doc per topic; human-reviewed; agents never overwrite |

If you are not sure which tier: land it in `raw` with an `expires` date and let the weekly refinery
pass promote it. Do not put unverified material straight into `chambers/` or `canonical/`.

## Check-in checklist (blocking, for any write to Alexandria)

- [ ] Not cron exhaust — or if it is, it went to `alexandria-ops`, not `vault/reports/<job>/`
- [ ] Frontmatter present and schema-valid (`id`, `tier`, `type`, `domain`, `source`, dates + the
      conditionally-required fields)
- [ ] Filename and every path segment are Windows-safe (no `: ( ) 🪐` / trailing space)
- [ ] Nothing hard-deleted that carried knowledge — uncertain material moved to `_archive/`
- [ ] No `canonical: true` doc or another agent's entry was overwritten; conflicts appended with
      `supersedes:` + `contradiction: true`
- [ ] Facts linked (`↗`), not re-typed; ≥3-chamber facts promoted to `canonical/reference/`
- [ ] Secret scan clean; no PII / client records
- [ ] `git pull --rebase` done at batch start; one batch = one commit = one push (no accumulated
      uncommitted work); log/chamber conflicts resolved by keeping both sides
- [ ] If a chamber/domain was merged or retired: `routing-table.md` vocab **and** the refresh cron
      were changed in the same commit (else it regenerates)
- [ ] Change made via the single-writer path (sync host) where possible; if writing directly,
      coordination rules in `PLUTO-OPERATING-RULES.md` §3 followed
