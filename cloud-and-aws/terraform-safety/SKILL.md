---
name: terraform-safety
description: Rigorous safeguards for Terraform infrastructure changes to prevent accidental destruction, drift, or state file leaks. Use before running terraform apply/destroy, reviewing a terraform plan, or targeting a resource with -target, especially one touching a live database, persistent disk, or DNS/routing record.
---

# Terraform Production Apply Safety

## Rules
1. **Plan First**: Always review the full output of `terraform plan` before applying.
2. **Targeted Applies**: Use `-target` carefully; verify full state consistency regularly.
3. **No Secret Leaks**: Never commit `.tfvars` containing secrets or output unmasked credentials into logs.
4. **Zero-Downtime Changes**: Guard against `destroy and then create replacement` on live databases, persistent disks, or routing records.

## Agent-written stacks

When an agent writes a small stack: write `terraform test` tests with `mock_provider` first (watch them fail, then implement; use
`override_during = plan` for computed values), validate guards such as a forbidden role list, plan from a scratch copy without the backend,
and let a person apply (hand over a one-line command with short symlinks). Generated secret values land in state, so use
`prevent_destroy`, a placeholder with `ignore_changes` for values a person owns, and names-only outputs. Verify afterwards with
`simulate-principal-policy` and a no-change plan. Full detail: `rules/terraform-prod-apply-safety.md` (Agent-written stacks) and
`rules/one-secret-one-audience.md`.

## Lessons from the handledispute VPC build (1 Nov 2026)

* Review the saved plan, then apply that exact plan file. Re-plan if anything changed.
* `allowed_account_ids` and default tags in the provider block; commit `.terraform.lock.hcl`; ignore tfstate and `*.tfplan`.
* Private subnet egress through a NAT instance needs swap and at least t3.micro; use `user_data_replace_on_change` and make the dependent instance wait for the network.
* Access via SSM Session Manager only (no SSH, no key pairs). Separate IAM roles per tier; the backend role reads only its own `/<app>/prod/*` parameters.
* Related rule: `rules/static-export-and-production-image-gotchas.md`.

## Lessons from the HandleDispute move to its own AWS account (14 Nov 2026)

* Resize an instance type in place with a saved plan that shows `1 to change, 0 to destroy`; a replace or destroy means stop.
* Reboot a new host once after its first deploy: a container created on a deleted staging network does not start again (`rules/a-new-host-is-proven-by-a-reboot-and-a-real-send.md`).
* SES in the sandbox authorises the recipient identity and the default configuration set as well as the sender; scope to account and region, pin `ses:FromAddress`, and test with one real send.
* The cutover order and the checks that must pass before DNS changes: `rules/an-account-cutover-freezes-first-and-compares-every-table.md`.

## Lessons from closing the old account (15 Nov 2026)

* Deleting with a saved targeted destroy plan worked; a versioned S3 bucket must be emptied of every version first, and an ECR repository with images needs a forced delete followed by `terraform state rm`.
* A shared host and public address are not yours to delete until the other product has moved; list shared resources first (`rules/closing-an-old-cloud-account-needs-an-inventory-and-the-first-real-deploy.md`).
* Copy secrets that exist only in the old account before the delete, and repoint the tools that read them.
* Do not test a container with `docker ps | grep -q` under pipefail (`rules/a-pipe-into-grep-q-under-pipefail-is-a-race.md`).
* Terraform state kept locally for a stack is gone in practice after the apply: record the removal in the repository docs.

