# Robust Cron Job Patterns (Pluto Operations)

## Credential Management — Never Hardcode
**Always read credentials from .env at runtime.** Hardcoded passwords expire and break silently.

Pattern:
```python
_APP_PW = ""
for _p in ["/mnt/c/Users/habib/.hermes/.env", str(Path.home() / ".hermes" / ".env")]:
    try:
        with open(_p) as _f:
            for _line in _f:
                if "KEY_NAME" in _line and "=" in _line and not _line.startswith("#"):
                    _APP_PW = _line.split("=", 1)[1].strip()
                    break
    except: pass
```

## Exit Codes and Cron Failure Reporting
Cron reports a job as "failed" when the script exits non-zero. This is **by design** for alerting:
- `exit(0)` = all clear, no issues
- `exit(1)` = problems detected (warnings or P0/P1 alerts)

If a script exits code 1 because it FOUND issues, the cron system will report it as "provider authentication error" which is misleading. Document this for the user.

Better pattern: only exit non-zero for truly critical failures (like unreachable API). For detected issues that were handled (email sent, report generated), exit 0 and let the email content speak.

## Infrastructure Churn — Instance Recycling
EC2 instances get recycled periodically, changing instance IDs. The fleet monitor breaks every time.

**Short-term fix:** Update hardcoded instance IDs in `amlhive_prod_monitor.py` and `amlhive_daily_report.py`.

**Permanent fix:** Use tag-based auto-discovery:
```python
def discover_instance(tag_value):
    r = subprocess.run([
        "aws","ec2","describe-instances",
        "--filters",f"Name=tag:Name,Values={tag_value}",
        "--query","Reservations[*].Instances[?State.Name=='running'].[InstanceId]",
        "--region","ap-southeast-2","--output","json"
    ], capture_output=True, text=True, timeout=15)
    instances = json.loads(r.stdout)
    return instances[0][0][0] if instances and instances[0] and instances[0][0] else None
```

## Alert Escalation Pattern
Use the `alert_email.py` helper to send URGENT RED HTML emails:
```python
from alert_email import send_alert
send_alert("Subject", "Plain text body", "<p><b>HTML body</b></p>")
```

Sends to: hhsiddiqui@gmail.com, shoaib@amlhive.com.au, tech@amlhive.com.au

## Schedule Design
- **Hourly jobs** (`0 * * * *` or `30 * * * *`): light, deterministic checks
- **Daily jobs** (`0 9 * * 1-5`): comprehensive health checks
- **Weekly jobs** (`30 10 * * 2`): analytical/review work
- **Monthly jobs** (`0 11 1-7 * 1`): strategic reviews
- **No-agent scripts** for pure data-collection/verification
- **Agent-driven cron** for analytical work that needs reasoning

## Common Pitfalls
1. **DB values might be UPPERCASE** — always check schema before writing WHERE clauses
2. **Instance IDs change on recycle** — prefer tag-based discovery when possible
3. **Gmail app passwords expire** — read from .env, never hardcode
4. **SMTP passwords can change** — read from .env at runtime
5. **psql -At output is pipe-separated on one line** — parsing must handle this
