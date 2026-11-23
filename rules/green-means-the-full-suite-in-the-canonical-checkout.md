# Green means the full suite in the canonical checkout

A targeted test run does not prove a change is safe, and a failure an agent reports from a worktree is not proof of a defect until it is reproduced where the project really runs.

**Scope:** every agent that lands or reviews a change, especially when subagents work in separate git worktrees.

## Why this exists

Tap-Ease POS, 18 Nov 2026. A change to the Clover result log passed every targeted test, and a 427-test Android run over 16 related classes was green. It broke `NoRawSecretsInLogsTest` (C44-R2-a forbids the field the new C88 requirement needs), and that conflict reached `dev` because nobody ran the whole suite. Separately, parallel agents reported "pre-existing failures" (five version-endpoint tests, one tokens test, five `BundledLocationAssetSourceTest` tests). The version and tokens failures were worktree artifacts: the new worktree had no gitignored `backend/.env`. The same agent reports, taken at face value, would have sent the reviewer after phantom defects.

---

## Core Directives

1. **Before landing, run the whole suite of each side you touched** (backend and Android), not the classes you edited. A new requirement can contradict an old requirement's passing test, and only the full run shows it.
2. **A conflict between a new requirement and an old test goes to the owner as a structured question**: which governs. Amend the old requirement and its test together, in one commit, and record the question and answer verbatim. Never weaken the old test alone.
3. **Reproduce every agent-reported failure in the canonical checkout before believing or dismissing it.** Check what a worktree lacks first: gitignored `.env`, generated assets, `local.properties`.
4. **"Fails without my change" is not "pre-existing".** Stash the change in the same worktree and in the canonical checkout, and compare both. If only the worktree fails, the cause is the worktree.
5. **Read the summary line and the exit code from the log**, not a background notification, and name the tree and the database the run used.
6. **When the cause of a failure is not found, say so.** List it as open with where it passes and where it fails, and do not label it "pre-existing" or "unrelated".

---

## Patterns to Follow

```text
Targeted green on the changed classes
-> full backend suite on a fresh scratch database in the canonical checkout (exit=0)
-> full Android suite (count tests and failures)
-> any failure: reproduce in the canonical checkout, then compare with the base commit
```

## Patterns to Avoid

- Landing on the strength of "the related classes pass".
- Copying an agent's "5 failures, all pre-existing" into a report without a canonical-checkout rerun.
- Editing the old test to match the new behaviour without asking which requirement governs.
