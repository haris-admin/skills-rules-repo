# Deployed-vs-local code parity (all agents)

Applies before writing "done"/"fixed" in any OpenSpec completion log or prod-issue doc for a
change that touches a Lambda, worker, or any artifact deployed separately from the main
app/backend release pipeline.

## Why this exists

issue-178 (22 Jul 2026): the RDS backup Lambda's `lambda_function.py` **already contained** the
correct fix for the C317 role split (`PGOPTIONS` bypass + `--enable-row-security`) — it had been
written, and per C317's own completion log, proven against a disposable Postgres 17 instance. But
the first scheduled backup after the cutover failed anyway, because the *deployed* Lambda was
running an older version. The gap wasn't the code — it was that nothing in the rollout checklist
confirmed the deployed artifact matched the repo before the cutover that changed its runtime
assumptions went live.

This is a distinct failure mode from a normal deploy: the main backend app has a single, obvious
deploy pipeline (`deploy-backend-aws.yml`) that people remember to run. Lambdas, one-off scripts,
and anything with its own Terraform-managed `archive_file`/`zip_file` are easy to edit locally,
test locally, and simply forget to actually redeploy — especially when the edit happened in an
earlier session or a different part of the same large change.

**Correction, 22 Jul 2026 (issue-185 session):** "the main pipeline is obvious and gets run" is
not actually safe to assume either. Both `deploy-backend-aws.yml` and `deploy-frontend-aws.yml`
are `workflow_dispatch`-only — auto-deploy-on-push is deliberately off during the AWS migration
(see the comment at the top of either workflow file). Commits accumulate on `dev` until someone
manually triggers a deploy; in one session this session found **22 backend commits** sitting on
`dev`, committed and pushed, genuinely undeployed. A prod-issue doc that says "Fixed and deployed"
for the main app needs the same evidence discipline as a Lambda, just via a different check.

### Checking whether `dev`/HEAD is actually running in prod (main app, not Lambda)

```bash
# Last SHA that actually completed a successful deploy:
gh run list --workflow=deploy-backend-aws.yml --limit 5 \
  --json databaseId,status,conclusion,headSha,createdAt
# (swap in deploy-frontend-aws.yml for the frontend)

# Is that SHA an ancestor of current HEAD, and how far behind is it?
git merge-base --is-ancestor <last-deployed-sha> HEAD && echo "ancestor: yes"
git log --oneline <last-deployed-sha>..HEAD | wc -l
```

If the count is non-zero, everything in that range — however many commits, however many sessions
ago — is committed and pushed but **not running in production**. Don't infer "committed to dev"
means "live" from a doc's own status line; check the actual last successful `gh run` SHA against
current HEAD before writing `Fixed and deployed`.

## Rules

1. **"Tests pass locally" and "the code is correct" are not evidence the fix is live.** For any
   artifact with its own deploy path (Lambda `zip_file`, a cron script copied to an instance, a
   Terraform-managed binary), the completion log needs evidence the *deployed* version matches —
   a `source_code_hash` diff, a version/build-id comparison, or a manual invoke against the real
   environment — not just "tests: 5 passed."
2. **Before a cutover that changes a shared runtime assumption** (which DB role connects, which
   secret is read, which token format is expected), enumerate every artifact that assumption
   touches (see `privilege-change-blast-radius-audit.md`) and confirm each one's *deployed* state,
   not just its repo state.
3. **A clean, scoped `terraform plan` showing only a `source_code_hash` change is the tell.** If
   `terraform plan -target=<lambda>` shows the code hash differs from what's applied, that is
   direct proof of exactly this gap — don't dismiss it as "just a hash," redeploy and verify.
4. **Verify with a real invocation after redeploying**, not just a clean `terraform apply`. A
   successful apply only proves the new code was uploaded, not that it actually works against
   live data/credentials (`aws lambda invoke` and check the real result, same as issue-178's
   manual backup run that confirmed an actual 8.85 MB dump succeeded).

## Related

- [issue-178](../../backend/prod_issues/issue-178-rds-backup-lambda-stale-deploy-missing-rls-bypass.md)
- [C317](../../openspec/changes/317-issue-153-rls-role-split/) — D317.05 already specified the fix;
  this rule exists because specifying and testing it wasn't enough on its own
