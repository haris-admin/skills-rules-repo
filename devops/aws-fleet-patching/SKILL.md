---
name: aws-fleet-patching
description: Use when patching the AWS EC2 fleet via SSM.
---

# AWS fleet patching (Amazon Linux 2023, via SSM)

Two accounts, two credential pairs, all instances are **Amazon Linux 2023** with the SSM agent online — so
patching is uniform and needs **no SSH and no bastion hop**. Credentials: `AWS_ACCESS_KEY_ID_AMLHIVE` /
`_TAPEASE` in `/mnt/c/Users/habib/.hermes/.env` (never print them). Run from `~/.hermes` with boto3.

## Inventory (verified live 2026-09-24)

> AMLHive instances are replaced routinely by Terraform applies. Re-verify with
> `aws ec2 describe-instances` under AMLHive creds before patching — never trust this table alone.

| Account | Instance | Name |
|---|---|---|
| AMLHive `560205084533` | `i-0232cf7f25b75cc5c` | amlhive-prod-backend (t3.medium) |
| AMLHive | `i-065791e30de129c81` | amlhive-prod-frontend (t3.small) |
| TapEase `707843605914` | `i-062b8ef5437ea6e2f` | tapease-backend-production |
| TapEase | `i-0aca7e109d0f6e773` | tapease-frontend-production |
| TapEase | `i-0f9a6ec659e6aab83` | tapease-dev-instance |
| TapEase | `i-06c24009b7ad32725` | tapease-bastion-production |
| TapEase | `i-0c9a14c400f1e7cdc` | tapease-nat-instance-production |

RDS (`amlhive-prod`, `tapease-postgres-production`) is **not** patched this way — AWS maintains the engine in
the maintenance window; only set auto minor version upgrade + a window that avoids the 03:45 payout sweep and
the 05:00 fleet monitor.

## The two commands that matter

**Audit (read-only, always safe to run first):**
```bash
dnf -q makecache 2>&1 | tail -3; echo rc=$?
dnf check-update 2>&1 | tail -6; echo rc=$?      # rc=100 means updates ARE pending
uname -r; rpm -q --last kernel | head -2
```
**Install:**
```bash
dnf upgrade -y --releasever=<YYYY.MM.DD from the check-update output>
dnf install -y dnf-automatic
```

## PITFALLS (each one cost real time)

- **A `dnf check-update | wc -l` with `2>/dev/null` reports 0 updates on a box that is 9 months behind.** The
  count regex misses AL2023's release-upgrade banner, and a *failed* metadata refresh also yields an empty
  list — so the read looks like a clean machine. AL2023 signals pending work with
  `dnf upgrade --releasever=2023.12.20260918`, not with a plain package list. **Always capture stderr and the
  exit code**; `rc=100` from `check-update` is the real "updates available" signal.
- **AL2023 moves quarters by `--releasever`.** `dnf upgrade -y` alone stays on the current release stream.
  Instances were found on `2023.9.20251208` and `2023.10.20260325` while the repos offered
  `2023.12.20260918` (Sep 2026) — 6–9 months of unapplied updates, invisible because nobody ran a check.
- **`needs-restarting` is not present** on a stock AL2023 box (it lives in `dnf-utils`) → reboot-needed
  checks return `unknown`. Compare `uname -r` against `rpm -q --last kernel` instead.
- **`rpm -q kernel` prints "package kernel is not installed"** — AL2023 uses versioned kernel packages and has
  no `kernel` meta-package. That message is noise, not a broken box.
- **Never patch the NAT instance in the same batch as the rest.** It is the egress path for every other
  instance in that VPC: rebooting it while the others are still pulling packages will fail their downloads
  mid-upgrade. Patch NAT **last**, alone, after everything else reports healthy.
- **Reboots need a health check between instances** — these run production: verify the app responds (the
  fleet-monitor scripts already know how) before moving to the next box. Order: dev → frontend → backend →
  bastion → NAT.
- **TapEase frontend carries a NodeSource repo** (`nodejs.aarch64 2:24.21.0-1nodesource`) — a major Node bump
  can break a Next.js build. Check the app after patching it, and confirm the Node version the app expects.

## Running it

Console (sanctioned, gives compliance reporting): **Systems Manager → Run Command → `AWS-RunPatchBaseline`**,
Operation `Scan` first (never installs), then `Install`, Target = the instance tags, reboot option
`RebootIfNeeded`. CLI equivalent: `send_command` with `DocumentName='AWS-RunPatchBaseline'` and
`Parameters={'Operation':['Scan']}`.

For a one-off shell fix: `send_command(InstanceIds=[...], DocumentName='AWS-RunShellScript',
Parameters={'commands':[...]})`, then poll `get_command_invocation` until a terminal status, and read
`CommandPlugins[0].Output` — the SSM invocation status alone does not tell you what happened.

Recurring: `dnf-automatic` (install + `apply_updates = yes`, `upgrade_type = security`, timer enabled) for
security-only, or an SSM Maintenance Window for full control with a patch baseline and reboot policy.

## Verification, never assumption

After patching, re-run the audit commands and confirm the releasever has advanced (e.g. to
`2023.12.20260918`) and `check-update` no longer returns pending work. A successful `send_command` call is not
proof the box is patched — read the per-instance output.
