# Full-corpus redundancy audit recipe (proven 2026-09-08)

When the owner reports "2,000+ files pending" in alexandria or asks to review/dedupe the vault:

## Step 0 — Rule out phantom deletions BEFORE hunting real redundancy

A huge "pending/deleted" count on the Windows git client while WSL `git status` is
clean is a **folder-name artifact**, not missing files (Windows cannot open dirs
whose names contain colons/emoji/trailing spaces; every file inside shows as
`D`). Diagnose with the WINDOWS git client, not WSL:

```
cmd.exe /c "git status --short"   # from the clone dir; compare to WSL git status
```

If Windows shows `R` (renames) after a sanitize pass, the artifact is fixed. Only
pursue real dedupe once both views agree on the true change set.

## Step 1 — Deterministic dedupe BEFORE any model review

Content-hash in Python (size-bucket first to skip hashing unique-size files,
then sha256 within same-size groups). Expect large mirror corpora to be ~50%
byte-duplicate:

- openclaw github mirror: 55.7% dup (1,489 files / 4.8 MB) — reports re-filed
  into every subsequent day's dated subfolder (`reports/2026MMDD/`), up to 10
  copies of one file
- gitlab openclaw vs github openclaw: 99% redundant (1,892/1,914)
- remaining library sections: 546 dup families / 1,176 files / 5.2 MB
- curated vault (vault/refined): much lower — 4-5 exact pairs across sections

Noise-class catalog (safe exclusions for future harvests — but NEVER prune
library/ in place; only add boilerplate dirs to sync EXCLUDE_DIRS):
`reports/2026*/**` dated re-files, `reports/comet-*` + `reports/research-*` name
variants, `backups/**`/`archives/**` rename copies, `memory/dreaming/{deep,rem}`
sleep-cycle stubs (60 tiny files collapse to 11 unique contents), empty 0-byte
files, `.pytest_cache/**`. `skills/` trees are usually duplicate-free.

## Step 2 — Fan out bounded section audits to cheap-model subagents

Split by section (~2-7K files each, one agent per section), each agent AUDIT-ONLY
(no edits), writing a structured report. Give each agent the known noise-class
catalog so it verifies/quantifies rather than rediscovering. Report must include:
clusters, files audited, recommended exclusions.

Cross-section dedupe of curated gems: hash full content AND provenance-stripped
content (a file differing only in its `<!-- provenance -->` header is a dup of
the other). Pick ONE canonical section per knowledge domain (dedicated habibi/
section outranks obsidian keep or haris-admin copies) and delete non-canonical
copies only after exact-equality verification.

## Step 3 — Salvage subagent timeouts from the live transcript

Auditors at 600s may time out BEFORE writing their report file (distinct from
the earlier pattern where files were written and only the summary delivery
lagged). The completed analysis is in the live transcript:
`~/.hermes/cache/delegation/live/<deleg>/task-*.log` — pull the final analysis
commands + outputs and write the report yourself. Do NOT re-dispatch blindly.

## Step 4 — Rescue unique files before dropping a redundant mirror

Same repo under github AND gitlab org-split: compare relative-path sets, copy
the smaller side's not-identical files into the canonical side, verify nothing
unique was lost, then delete the redundant mirror. Rescued 15 genuinely-unique
gitlab openclaw files into the github canonical this way.

## Step 5 — Deliver

Secret-scan the staged tree, commit with scoped `git add` (own tree only),
push, verify via `git rev-parse HEAD` == `origin/main`. Sibling sessions may
commit to vault/reports concurrently — pull --rebase before push and scope your
git add to your lane (vault/refined vs vault/reports).
