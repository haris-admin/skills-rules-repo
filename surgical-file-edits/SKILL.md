---
name: surgical-file-edits
description: "Use when editing an existing file in place."
version: 1.0.0
author: Pluto
license: MIT
category: software-development
metadata:
  hermes:
    tags: [editing, patch, write_file, refactor, verification]
    related_skills: [fleet-skill-governance, git-working-tree-hygiene]
---

# Surgical File Edits

Editing a file that already exists — a pipeline script, a config, a long document — is a different job from
writing a new one. Most of the content must survive untouched, something else may execute the file, and a
bad edit can look fine in the diff while breaking the structure underneath.

## When to Use

- Changing an existing script, config or doc where the surrounding content must be preserved
- Any edit to a file a pipeline **runs** (a mangled edit passes review and breaks the job later)
- After a patch whose `old_string` spanned a function or section boundary

## Procedure

1. **Read the WHOLE file first.** `write_file` refuses to overwrite a file the session has not fully read,
   and a partial read pushes you into blind patching — which is how files get mangled. Read to the end, or
   read with a limit that provably covers it.
2. **One targeted patch per structural change.** Keep `old_string` short and contiguous. A patch spanning a
   function boundary can match fuzzily across it and strand the old body under the new definition.
3. **Check every patch's return value.** No diff, or `success: false`, means nothing changed — and a
   "successful" patch can still have produced invalid structure. Print each result inside a batch script so
   a no-op cannot pass as done. For a batch of literal replacements, print **OK/MISS per replacement and
   assert the count changed** before writing — one silent MISS in a list of ten is the failure mode that
   leaves a document half-updated and self-consistent-looking.
4. **Validate after editing**: `ast.parse` for Python, the tool's lint for config/doc formats. Then run the
   script's cheap path (CLI smoke, `--dry-run`, a one-record pass) when something consumes it — a
   syntactically valid edit can still break an output contract.
5. **If the structure is broken, stop patching.** Duplicated body, orphaned statements, or a definition
   whose tail now contains another function's opening lines. Re-read the file in full and rewrite it with
   `write_file`, then re-validate and re-run. Repeated local patches on a damaged region compound damage.
6. **Commit with an explicit pathspec** (`git add -- <paths>`) so an unrelated dirty index does not ride
   along in the commit.

## Pitfalls

- **A batch cell that raises before your edits run leaves the file untouched while looking like partial
  success.** In an `execute_code`/scripted batch, ONE syntax error — an unbalanced quote, a `$?` or a
  `$(...)` inside a triple-quoted shell blob — aborts the whole cell, so no patch is applied at all. Apply
  dependent edits in separate calls rather than stacking them, and print each write's result.
- **Nested quoting is the most common cause of that abort.** Build shell snippets from concatenated plain
  strings, or write the snippet to a file and execute that, instead of embedding command substitution
  inside a triple-quoted block. The same oversized or deeply-quoted inline payload can be refused by the
  terminal's command parser outright: when a shell step needs more than a couple of statements, write it to
  a script file and run that file.
- **Line endings silently break multi-line anchors.** A CRLF file contains literal `\r\n`, so an anchor
  written with `\n` can never match it — and a script that aborts on the first missing anchor writes
  NOTHING while printing nothing, which reads as success. Normalise for matching, restore on write:
  `t = raw.decode('utf-8').replace('\r\n', '\n')`, apply `\n`-joined anchors, then
  `t.replace('\n', '\r\n')` before `write_bytes` when the original held CRLF. Match the ending the folder
  already uses: flipping a whole file's endings turns a one-line edit into a whole-file rewrite in the
  diff.
- **A single file can be internally MIXED, so "is this file CRLF?" is the wrong question.** Count all
  three separately — `raw.count(b'\r\n')`, `raw.count(b'\r') - crlf`, `raw.count(b'\n') - crlf` — and
  normalise to the dominant convention before editing. A file with 40 CRLF lines and 40 bare-CR lines
  passes a naive `if raw.count(b'\r')` check and still produces unreadable diffs on every later edit.
- **Typographic quotes break literal anchors with no error.** Prose and auto-formatted documents mix
  straight `'` `"` with curly `’` `“` `”` (U+2019/U+201C/U+201D). An anchor copied from rendered output
  silently matches nothing. Anchor on a distinctive ASCII-only prefix and match the rest with a regex
  (`re.search(r"- \*\*30 Sep 2026\*\* — sponsor page.{0,220}", s)`), which also tolerates the wording
  drift that follows a hand-edited line.
- **Rewriting a file to "fix" a mangled patch is only safe after a full read** — otherwise the rewrite is
  based on a partial picture and silently drops the tail. Keep the flow: full read → single rewrite →
  validate → execute.
- **A partial read is not a read for write purposes.** Re-reading a fragment tells you nothing about
  whether the tail still exists; check the line count, not just the region you edited.

## Verification

- **Re-read the target, or grep for the new text, before reporting the edit done.** A script that exits
  early on a missing anchor prints nothing; absence of output is not success, and neither is a batch
  cell's `status: success` when its own stdout is empty.
- The patch reports success AND the file's syntax check passes.
- For a pipeline script: run it (or its dry-run) and confirm the same output contract as before the edit.
- `git diff --stat` shows only the files you intended, with no unexplained deletions.
