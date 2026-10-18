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
