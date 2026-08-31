---
name: terraform-safety
description: Rigorous safeguards for Terraform infrastructure changes to prevent accidental destruction, drift, or state file leaks.
---

# Terraform Production Apply Safety

## Rules
1. **Plan First**: Always review the full output of `terraform plan` before applying.
2. **Targeted Applies**: Use `-target` carefully; verify full state consistency regularly.
3. **No Secret Leaks**: Never commit `.tfvars` containing secrets or output unmasked credentials into logs.
4. **Zero-Downtime Changes**: Guard against `destroy and then create replacement` on live databases, persistent disks, or routing records.

