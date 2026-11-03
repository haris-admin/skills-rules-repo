# Ship scripts to a server as files, never as quoted strings (all agents, all repos)

Applies to anything installed on a remote box over SSM, SSH or user-data: backup scripts, systemd units, cron jobs, health checks.

## Why this exists

**3 Nov 2026 (ChargeRail):** the nightly backup was installed by pushing a shell command through `printf` inside an SSM command. The nested quotes were lost, so the installed `backup.sh` ran `pg_dump` as the wrong user and failed every night. Nobody knew until the new alert check reported `backup_failed` a day later. A manual run had passed, because the manual path used a different quoting layer.

## Rules

1. Keep the script as a real file in the repo (`infra/scripts/box-*.sh`), `bash -n` it, ship it with a checksum-verified upload, and `chmod`. Never build it with `printf` or `echo` of a long quoted string.
2. Use `set -euo pipefail` and an explicit non-empty check on the output (`test -s`), so a half-failed pipe fails loudly.
3. Test the installed copy through the same path the scheduler uses (`systemctl start <unit>`), not only by running the repo copy by hand. Confirm `systemctl is-failed` is clear afterwards.
4. Do not call a backup done until a restore from it has been tested once.
5. Add a freshness alert (newest backup older than 26 hours) so a silent failure shows within a day.
