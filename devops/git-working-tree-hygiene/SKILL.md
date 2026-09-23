---
name: git-working-tree-hygiene
description: "Use when git status lies: CRLF churn and stray markers."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows, wsl]
metadata:
  hermes:
    tags: [git, crlf, line-endings, conflict-markers, repo-hygiene, wsl, concurrent-agents]
    related_skills: [merge-reconciler, coding-agent-delegation, git-sync]
---

# Git Working-Tree Hygiene

`git status` lies in two directions in this environment: it reports changes nobody made, and
it hides corruption that is already committed. Both waste a session if you act on the
reported state instead of verifying it first. This skill is the diagnosis order.

## When to Use

- `git status` shows files you did not touch (especially "every file in the repo")
- A repo lives on `/mnt/c/...` and is also opened or edited from the Windows side
- You are about to commit where other agents (Codex, Claude, sibling worktrees) may be writing
- You find `<<<<<<<` / `>>>>>>>` in a file and there is no merge in progress

## Rule 1 — Prove a diff is real before acting on it

A whole-tree diff that appeared without an edit is line-ending churn, not work. Confirm in
one command before touching anything:

```bash
git diff --stat                        # e.g. 142 files, hundreds of +- each
git diff --stat -w                     # whitespace-insensitive — EMPTY means nothing changed
git diff --stat --ignore-cr-at-eol     # EOL-only check — empty = pure CRLF churn
```

Mechanism: a repo checked out on Windows (or touched by a Windows-side tool) writes CRLF into
the working tree while the index stores LF, so Linux-side git sees every file as modified.
The content is identical — `-w` collapsing to zero files proves it.

Then clear it without losing anything:

```bash
git restore .        # rewrites from the index; content-identical, nothing lost
git status --short   # must be clean
```

### A tree can be BOTH churn and real work — separate them before restoring

`git restore .` is only safe when the diff is *pure* churn (`-w` collapses to nothing). A working tree
routinely carries CRLF noise **plus a handful of genuine edits from another agent** — then `-w` does
not collapse, and a blanket `git restore .` **destroys that real work.** One fleet repo showed 382
changed files of which only **11** carried an in-flight observability change; the other 371 were pure
churn. Never restore a tree you have not measured:

```bash
git diff --stat | tail -1                        # e.g. 382 files changed, 64k insertions
git diff --ignore-all-space --stat | tail -1     # e.g.  11 files changed  <- the REAL edits
git diff --ignore-all-space --name-only          # the keep-list: read it, it is someone's work
```

The delta between the two counts is the churn. Restore only the churn side:

```bash
git diff --name-only                     | sort > /tmp/all.txt
git diff --ignore-all-space --name-only  | sort > /tmp/real.txt
comm -23 /tmp/all.txt /tmp/real.txt > /tmp/churn.txt
xargs -a /tmp/churn.txt git restore --          # clears the noise, keeps the real edits
```

Notes that make this reliable:

- `--ignore-all-space` is the discriminator to reach for first; `-w` is the same family, but the
  two-stat comparison is what tells you *how much* of the diff is real rather than merely *whether*
  any of it is.
- Sorting before `comm` is what makes it correct — unsorted input silently mis-diffs the lists.
- The real-edit files are usually another writer's unfinished work: **do not commit them, clean them,
  or "finish" them.** A clean `git status` is not a goal when the tree is legitimately shared.
- **A scheduled writer's uncommitted changes ARE content — read the diff before any targeted restore.**
  In repos whose content is produced by cron jobs and sync drains, `git status` showing a file modified
  usually means *the last scheduled run wrote it and nothing has committed yet*, not stale noise. So the
  scoped-looking `git checkout -- <path>` / `git restore <path>` destroys that run's output: the file
  reverts to HEAD, which predates it. Never restore a path you have not diffed — `git diff -- <path>`
  first, and if it is real content, leave it (or commit it) rather than clearing it.
- **Recovering a discarding mistake:** the writer's own artefacts still hold the text — the scratch
  script the job left in `~/.hermes/cache/scratch/`, its cron output under `~/.hermes/cron/output/<job_id>/`,
  and any state/event log it appended to. Prefer the scratch script: pulling the string literals out with
  `ast.parse` recovers the exact text without executing its write steps. Verify the restored block against
  a second leg (a vector/DB copy of the same event) before re-committing.
- When a delegated coding agent will work in that tree, put this split in its brief: name the
  real-edit paths as off-limits work-in-progress and require an explicit pathspec on every commit, or
  it will sweep them into its own commit message.

When you **add a new file** to a repo whose existing files are CRLF, write it CRLF too. A new
LF file in a CRLF repo shows as whole-file churn in the diff, which buries the actual content
change and makes review harder. Match the neighbours — check one with
`grep -c $'\r' <existing-file>` first. Converting your own new file is safe and needs no
permission; only repo-wide EOL config is a shared-branch change (below).

### Writing a CRLF file without corrupting it

Re-encoding line endings in Python is where this goes wrong. Decoding a CRLF file and splitting on `"\n"`
leaves the `\r` inside every chunk, so joining with `"\r\n"` emits **`\r\r\n`** — double-CR that renders
as stray blank-ish lines and diffs the whole file. Normalise first, then apply the ending once:

```python
b = p.read_bytes()
bom = b.startswith(b"\xef\xbb\xbf")
t = b.decode("utf-8-sig").replace("\r\n", "\n")      # strip existing endings
# ...edit lines here, in LF...
p.write_bytes(("\ufeff" if bom else "").encode()
              + "\n".join(t.split("\n")).replace("\n", "\r\n").encode())
```

Verify by counting the two forms separately — `b.count(b"\r\n")` and `b.count(b"\n") - b.count(b"\r\n")`
together **hide** `\r\r\n`, because the doubled CR is not itself a `\n`. Count `b"\r\r"` and require zero,
and confirm the pre-existing line count is unchanged (only your insertion differs). Preserve a BOM if the
file had one, and never let a whole-file rewrite re-normalise lines you did not touch.

**Size a change with `-w`, never with the raw diff.** On CRLF files `git diff --stat` can report every line
as changed while `git diff -w --numstat` shows the true edit (+3/-2, say). The raw number is not evidence of
corruption and the `-w` number is not evidence of cleanliness — check both, then confirm the content itself.

**Do not "fix" this by committing.** Committing CRLF churn buries real history and creates a
conflict for every other branch. Clear the state.

**Do not add `.gitattributes` or change line-ending config unprompted.** The durable fix
(`* text=auto eol=lf`) is a change to a shared branch: propose it and apply it only if the
user wants it. Clearing the working tree is the fix that needs no permission. If the user
declines, the churn will recur on the next Windows-side checkout — state that as a residual
risk once, and do not re-litigate it every session.

## Rule 2 — Scope every commit to named paths

Never `git add -A` / `git add .` when:
- sibling agents write in the same checkout (their uncommitted work gets swept into your commit)
- the tree carries CRLF churn (Rule 1) — `-A` commits all of it
- the repo holds a large harvest or generated tree you did not author

```bash
git add <path1> <path2> && git commit -m "..."
```

If a tool already staged things you did not intend, `git restore --staged <path>` rather than
resetting the whole tree.

## Rule 3 — Committed conflict markers (no merge in progress)

A bad merge can commit literal markers that every later branch inherits. Establish the blast
radius before resolving anything:

```bash
git grep -l -e '^<<<<<<<' -e '^>>>>>>>' -e '^=======$' HEAD
git grep -l -e '^<<<<<<<' -e '^>>>>>>>' origin/dev origin/main   # and any peer branch
```

- **Anchor the patterns (`^<<<<<<<`).** Unanchored searches also match the word inside prose
  and documentation *about* merges, producing phantom hits that cost a pass to chase.
- **Fix the branch you own; report the others.** Corruption propagates across refs, so fixing
  only yours leaves the rest broken — but merging your fix forward carries it cleanly provided
  the other ref has not touched those files since (`git diff --stat <ref>...HEAD -- <paths>`).
- **A dangling `>>>>>>>` with no matching `<<<<<<<` / `=======` means a botched merge already
  dropped a side.** Nothing is recoverable from the marker, so delete exactly that line and
  nothing else — never invent a resolution or "restore" content that was never there. Verify
  the surrounding entry is intact and not duplicated elsewhere in the file.
- On a documentation artefact the two sides are often complementary rather than competing (one
  side holds title/status/tags, the other the body): resolve as a union in a sane section
  order. That class is distinct from a real design collision.
- **Prove no fact was dropped by a union resolution.** Extract identifier-like tokens from the
  pre-resolution version (SHAs, run/build ids, event ids, regex literals, file paths) and
  confirm each survives. Expect a few false "missing" hits coming from the marker lines you
  deliberately deleted — inspect those individually instead of accepting the raw count.

For markers left by a *halted* merge (a real `MERGE_HEAD` present), use the `merge-reconciler`
skill instead — that is arbitration between two intents, not hygiene.

## Rule 4 — Know which repo, branch, and account you are acting on

- Confirm `git rev-parse --abbrev-ref HEAD` and the remote URL **before** any push, reset, or
  restore. Several repos of the same project coexist (shared checkout plus per-agent
  worktrees), and the one you are standing in is not necessarily the one you mean.
- **Identify the release branch from evidence, not assumption.** A repo's default branch, its
  working branch, and the branch the deployer actually builds are three different facts — and
  CI passing proves none of them. A pipeline that only tests and builds says nothing about what
  is live. Settle it with `git symbolic-ref refs/remotes/origin/HEAD`, then take an artefact
  that exists on only one branch and fetch it from the live system: 404 vs 200 decides.
- **A shallow clone makes history lie.** `git rev-list --count <ref>` on a shallow clone returns
  a tiny meaningless number (few grafts), which reads as "this branch is nearly empty". Check
  for `.git/shallow` before drawing any conclusion from a commit count; compare two refs you
  both have (`git rev-list --count A..B`) or use `git merge-base`.
- **Before merging a working branch into the release branch, list what else would ship.** A
  working branch accumulates other agents' commits, so the merge publishes all of them.
  `git log --oneline origin/<release>..<working>` shows exactly what goes out — state it before
  releasing, so one agent does not silently publish another's unfinished work.
- When a sibling agent is mid-operation a git command can fail on the index lock. Wait and
  retry rather than forcing — the other writer's commit is usually seconds away.
- Do not `git reset --hard` in a shared checkout to clear churn; `git restore <paths>` is
  scoped and reversible.

## Verification

- `git diff -w` is empty for anything you decided was churn.
- `git status --short` is clean, or shows only the paths you intentionally changed.
- A repository-wide anchored marker grep returns zero files for the patterns you were asked to clear.
- The commit contains exactly the intended paths (`git show --stat HEAD`).
