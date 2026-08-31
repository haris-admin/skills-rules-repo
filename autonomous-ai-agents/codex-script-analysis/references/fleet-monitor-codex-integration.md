# Fleet Monitor → Codex Diagnosis Integration

Wired July 2026 into `amlhive_prod_monitor.py` (lines ~1548+).

## How It Works

When the fleet monitor detects >15 P1 alerts or any P0 alerts, it:

1. Sends the email alert (always — exit code is independent)
2. Pipes the raw monitoring data dict to Codex CLI via `codex_report.py`
3. Codex analyzes the data and writes a diagnosis to `~/.hermes/reviews/fleet_diagnoses.log`
4. Exits with code 1 (cron marks as failed)

```
Raw monitoring data (dict)
  → codex_report.generate_report(data, "☁️ AmLHive Fleet Monitor")
  → subprocess.run(["codex", "exec", "--skip-git-repo-check", prompt])
  → Codex returns formatted analysis
  → Appended to ~/.hermes/reviews/fleet_diagnoses.log
```

## Code in `amlhive_prod_monitor.py`

```python
# At end of main(), after send_email(report):
if should_exit_1:
    try:
        from codex_report import generate_report
        diagnosis = generate_report(data, "☁️ AmLHive Fleet Monitor")
        log_dir = Path.home() / ".hermes" / "reviews"
        log_dir.mkdir(exist_ok=True)
        with open(log_dir / "fleet_diagnoses.log", "a") as f:
            f.write(f"\n[{datetime.now(AEST).strftime('%Y-%m-%d %H:%M:%S')}] "
                    f"AMLHive Fleet FAILURE:\n{diagnosis}\n{'─'*60}\n")
    except Exception:
        pass  # Don't fail the script if Codex diagnoses fails
```

## Exit Code Threshold History

| Date | Threshold | Reason |
|------|-----------|--------|
| Pre-Jul 2026 | >2 P1 | Original — too sensitive |
| Early Jul | >10 P1 | Raised for Sentry ProgrammingError noise |
| Jul 23 2026 | >15 P1 | Still hitting 10-14 events on routine churn |

## RDS Password Drift Detection

When the daily business report (cron `3ebed4e59ee3`) fails with:
```
FATAL: password authentication failed for user "amlhive"
```

**Root cause:** The RDS master password was changed but the Secrets Manager secret (`amlhive/prod/rds`) was NOT updated. Rotation is disabled on this secret.

**Fix:**
1. Verify the secret: `aws secretsmanager get-secret-value --secret-id amlhive/prod/rds`
2. Compare password against actual RDS (via `aws rds describe-db-instances --db-instance-identifier amlhive-prod`)
3. Reset RDS password: `aws rds modify-db-instance --db-instance-identifier amlhive-prod --master-user-password NEWPW`
4. Update secret: `aws secretsmanager put-secret-value --secret-id amlhive/prod/rds --secret-string '{"password":"NEWPW",...}'`

**Prevention:** Enable automatic rotation on the secret (`aws secretsmanager rotate-secret`). Or document that both RDS and Secrets Manager must be updated together.
