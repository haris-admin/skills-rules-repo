# GitHub OIDC trust must match the real subject; free plans gate by manual run

Check the repository's OIDC subject customisation before writing an AWS role trust, and gate production with a manual run when the plan has no environment reviewers.

**Scope:** GitHub Actions deploying to AWS (or any cloud) with OIDC, on personal accounts or free plans.

---

## Core Directives

1. **Read the subject**: `gh api repos/<owner>/<repo>/actions/oidc/customization/sub`. When `use_immutable_subject` is true the token subject is `repo:<owner>@<id>/<repo>@<id>:environment:<env>`; a name-based `repo:<owner>/<repo>:...` trust fails with `Not authorized to perform sts:AssumeRoleWithWebIdentity`.
2. **Match exactly**: use `StringEquals` on the full subject, never a wildcard; the immutable form also blocks a deleted and recreated repository of the same name.
3. **Free plan, private repo**: environment required reviewers return HTTP 422. Make the deploy workflow `workflow_dispatch` only (a push does not deploy), keep the `production` environment (the trust needs it), run only from `main`, and let the owner's click be the approval.
4. **Failing before deploy is safe**: a trust mismatch fails at the credentials step before any deploy action; confirm production is unchanged and fix the trust with a saved Terraform plan the owner applies.

## Why this exists

**6 Nov 2026 (HandleDispute):** the setup script failed on required reviewers (HTTP 422), the owner chose manual runs, and the first deploy failed at the AWS login because the repository used immutable subject claims.
