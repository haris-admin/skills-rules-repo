# Isolated Production Release Recipe

How to ship an approved fix to production without dragging along unreleased or held work on the integration branch, and how to hand production commands to a human safely. Applies to every agent preparing or running a production release when the integration branch is ahead of what is deployed.

**Scope:** release engineering with a shared checkout, a separate production-deploying human, and a CI deploy workflow (worked example: AMLHive backend and frontend releases, 1 and 6 Oct 2026).

---

## Why this exists

The integration branch (`dev`) was 150+ commits past the last deploy and carried unreleased migrations and held changes. A deploy runs migrations against the production database, so releasing the branch tip would have applied them all. The recipe below shipped only the approved code. Separate failures in the same weeks (a long wrapped command that split and half-ran a `terraform apply`; a verify script that grepped a log that never captured the output; macOS `sed -i` silently editing nothing; a second dispatch cancelling the first deploy) are folded in.

## Core Directives

1. **Base the release on the last deployed commit,** read from the deploy workflow's runs (`gh run list ... --json headSha,conclusion`), never a tag and never the branch tip.
2. **Cut the release branch in a separate git worktree** from that commit, not in the shared checkout: `git worktree add <abs path> -b release/<slug> <last-deployed-sha>`.
3. **Cherry-pick only approved code and tests.** Drop docs and anything the releasing authority did not name.
4. **Bump the version with a Python string replace.** On macOS `sed -i` without a backup suffix silently edits nothing. Check every manifest matches before and after.
5. **Run the release isolation check against the worktree** with `--repo <worktree>` and require a PASS (no unnamed migrations, no held paths).
6. **Pin the commit SHA in every production script.** A later commit must not change what ships.
7. **Deploy exactly once.** A second dispatch cancels the first when the workflow uses `cancel-in-progress`. Check the run list before re-running.
8. **Verify migration state directly, not from the workflow log.** The log does not capture the remote command's output, so grepping it proves nothing. Run a read-only check in the live container (for AMLHive, through SSM: `docker exec amlhive-app-1 python -m app.core.schema_contract`) and compare to the expected head.
9. **Hand commands to a human as short per-step scripts.** One script per step at an absolute path, header `set -euo pipefail`, run as `!<path>` with the `!` as the very first character, one short line per message. A long one-liner wrapped by the terminal splits into several commands.
10. **Explicit cloud and CLI identity in every script.** `AWS_PROFILE=<named profile>` on every `aws` and `terraform` command (a bare command can hit another company's account and return 403); `GH_TOKEN=$(gh auth token --user <org account>)` for `gh` when several accounts are logged in.
11. **Lock discipline.** `terraform -lock=false` only when the state lock table does not exist and you are the sole operator, stated in the script header.
12. **Read the real result after each step** (git, run view, cloud CLI) before sending the next script.
13. **Cherry-pick the fix back** to the integration branch so its eventual release does not ship the bug again.

---

## Patterns to Follow

```bash
git worktree add /abs/path/rel-slug -b release/slug <last-deployed-sha>
python3 scripts/check_release_isolation.py --repo /abs/path/rel-slug --base <last-deployed-sha> --head <release-sha>
# step scripts: /abs/path/step1-push.sh (SHA pinned), then the human types: !/abs/path/step1-push.sh
```

## Patterns to Avoid

- Pushing and deploying the branch tip because "it is only a small fix".
- `sed -i` for version bumps on macOS; a verify step that greps the deploy log for remote command output.
- One long pasted command for the human; dispatching the deploy twice.
- Shipping an isolated unit whose tests still pin a roster that includes a held item (6 Oct 2026, second release): a contract test asserted a fixed list of 20 scheduled-job names, and a second test required a held job in a name set, so the unit failed 10 tests the moment the held job was left out. The deploy gate ran only the smoke subset, so nothing would have stopped it, which is why it must be checked by hand.

## Building the unit from mixed commits (added 6 Oct 2026)

- When source commits mix code, tests and docs, take only the approved paths with `git show <sha> -- <paths> | git -C <worktree> apply --index --3way`, not a whole cherry-pick, and take the final accepted test files from the accepted commit with `git show <sha>:<path>`.
- Compare the SHA-256 of every test and source file in the unit with the values the independent review recorded. A mismatch means the unit is not what was reviewed.
- Run the unit's tests on the reduced roster before shipping: remove the held item's registration in a scratch copy and confirm the unit's own tests pass there, and that the previous versions of any roster-pinning test fail there (proving the revision was needed).
- Run the deploy workflow's own gate command locally (for example the smoke subset), the migration lint, and lint on the changed paths, using the main environment's interpreter with the worktree as the working directory; never read or copy `.env` files into the worktree.
- Give each unit a version above every other prepared unit, so tags do not collide, and keep all five version files in sync.

---

## Verification & Guardrails

- The release summary contains the isolation check's `RESULT` line, the pinned SHA, the run id and the direct migration check output.
- Related: `rules/release-image-from-clean-export.md`, `rules/terraform-prod-apply-safety.md`, `rules/aws-profile-and-secret-recovery.md`, `rules/github-cli-multi-account-scope.md`, `rules/deploy-state-needs-independent-reads.md`, `skills/incremental-version-bumping`.
