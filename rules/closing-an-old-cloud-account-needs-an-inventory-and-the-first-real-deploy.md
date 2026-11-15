# Closing an old cloud account: inventory shared infrastructure, copy what exists only there, repoint, run one real deploy, then delete (all agents, all repos)

Applies when a product moves to its own cloud account and the old resources are to be removed.

## Why this exists
**14 to 15 Nov 2026, HandleDispute (OpenSpec 77):** the product moved to its own AWS account. The owner then ordered the old resources deleted. Deleting only the product's own resources was safe; deleting the shared host would stop another product (ChargeRail) that ran on the same host and public address, which the owner confirmed in writing before it went. Three secrets existed only in the old account (a Cloudflare DNS token, an ABN lookup key, an agent key), and two scripts still read from the old account. The GitHub deploy workflow pointed at the old account until its variables were repointed; the first run there passed its gates and exposed a race between the parallel frontend and backend jobs.

## Rules
1. Inventory first, read only: instances, volumes, buckets, repositories, IAM, secrets, parameters. Mark what is shared with another product and keep it until its owner has moved or approved in writing.
2. Compare the old and new secret and parameter names. Copy anything that exists only in the old account with a script that never prints a value, then repoint every tool that reads from the old account (tests first) before deleting.
3. Repoint the deploy pipeline (OIDC role, repository variables from the new stack's outputs, check for environment-level overrides) and run one real deploy from the new pipeline before the old account is touched, so a failure does not meet a missing rollback.
4. A targeted `terraform plan -destroy` with a saved plan; the owner applies it. A versioned bucket is emptied of all versions first, a container repository with images needs a forced delete and `terraform state rm`.
5. Record the owner's decision verbatim, then update the agent instructions: say there is no rollback, what was kept, and what the other product now has to do.
6. Parallel deploy jobs that depend on each other race; make the dependent job wait, or expect a re-run of only the failed job.
7. The auto mode classifier blocks pushes to `main` and force-style cleanups from the agent shell; give the owner a short `~/` script and ask for its output.
