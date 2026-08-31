# Cross-Fleet Monitoring Pattern

## Architecture

```
Hermes Cron (WSL) ──no_agent script──→ Bridge (Windows port 18796) ──PowerShell──→ AWS API
     │                                       │
     │ stdout captures result                │ POST /tapease/monitor
     │                                       │ returns JSON
     ▼                                       ▼
Telegram delivery                     AWS CloudWatch + EC2 + S3
(to user)
```

This pattern monitors AWS infrastructure (TapEase fleet) by chaining through three layers:
1. **Hermes cron job** (WSL) — schedules and delivers output
2. **Research Bridge** (Windows) — runs PowerShell scripts natively
3. **AWS** — CloudWatch, EC2 SSM, S3 OTEL logs

## Why Not Direct WSL→AWS?

The PowerShell scripts use:
- Windows-specific `.env` file (`C:\Users\habib\.openclaw\.env`) with AWS credentials
- `C:\Program Files\Amazon\AWSCLIV2\aws.exe` — the AWS CLI v2 on Windows
- SSM agent on EC2 instances (Windows-native PowerShell remoting)
- Windows file paths for log downloads

Running these from WSL would require duplicating credentials and paths. The bridge avoids this by executing the scripts in their native Windows environment.

## Adding a New Cross-Fleet Monitor

### 1. Write the PowerShell Script

Place it at `C:\Users\habib\.openclaw\workspace\scripts\system\<name>.ps1`

**Requirements:**
- Accept parameters (lookback_hours, target name, etc.)
- Write output to `stdout` (this gets captured by the bridge's execPromise)
- Save reports to `reports/monitor/<name>/` for permanent record
- Handle errors gracefully (no uncaught exceptions)
- **Use UTF-8 BOM encoding** if the script contains Unicode characters

### 2. Add Bridge Endpoint

Edit `/mnt/c/Code/gitlab/n8n-habibi-integration/bridge/research_bridge.js`:

```javascript
app.post('/my-new-monitor', async (req, res) => {
    const { param1, callback_url } = req.body;
    console.log(`📊 Starting new monitor: ${param1}`);
    res.json({ status: 'started' });
    const cmd = `powershell.exe -ExecutionPolicy Bypass -File "${path.join(WORKSPACE, 'scripts', 'system', 'my-new-monitor.ps1')}" -Param1 ${param1}`;
    runCommand(cmd, callback_url, { param1 });
});
```

For a **sync endpoint** (blocks until completion, returns result): use `execPromise` from the bridge, then `res.json(result)`.

### 3. Create Hermes Cron Job

```bash
# no_agent runner script that POSTs to bridge and formats output
cronjob action=create \
  name="🔵 My Monitor — 6AM" \
  schedule="0 6 * * *" \
  no_agent=true \
  script="my_monitor_runner.py" \
  deliver=origin
```

The runner script should:
1. `curl -s -X POST http://localhost:18796/my-endpoint -H "Content-Type: application/json" -d '{"param": "value"}'`
2. Parse the JSON response
3. Format as a readable summary
4. Print to stdout (→ Telegram delivery)
5. Exit 0 (always — see cron orchestration pitfalls about exit codes)

### 4. Update Cron Schedules

Add the new cron to the TapEase monitoring table in `pluto-pipeline-orchestration`.

## Existing Cross-Fleet Monitors

| Monitor | Bridge Endpoint | PowerShell Script | Cron Jobs | What It Checks |
|---|---|---|---|---|
| TapEase Lambda | `POST /cloudwatch-monitor` | `scripts/system/lambda_monitor_unified.ps1` | 4x daily (5AM, 11AM, 5PM, 11PM via sync monitor) | Lambda invocations, Clover sync, CloudWatch log groups |
| TapEase EC2 | `POST /ec2-backend-monitor` | `scripts/system/ec2_backend_monitor_unified.ps1` | 4x daily (5AM, 11AM, 5PM, 11PM via sync monitor) | SSM heartbeats, S3 OTEL logs, instance health |

### TapEase Monitor Schedule (AEST)

| Time | Job ID | Cron Expression | Runner Script |
|---|---|---|---|
| 5:00 AM | `dbd3cb1b5bd3` | `0 5 * * *` | `tapease_prod_monitor.py` |
| 11:00 AM | `582bd225ddd1` | `0 11 * * *` | `tapease_prod_monitor.py` |
| 5:00 PM | `1086e6405da1` | `0 17 * * *` | `tapease_prod_monitor.py` |
| 11:00 PM | `be81c61778a8` | `0 23 * * *` | `tapease_prod_monitor.py` |

All run as Hermes cron jobs with `no_agent: true`, `deliver: origin` (Telegram), and `script: tapease_prod_monitor.py` (direct AWS CLI + SSM, replaced bridge-based runner Jul 8, 2026).

### Runner Script

`/home/habib/.hermes/scripts/tapease_prod_monitor.py`

The runner:
1. Calls `POST /tapease/monitor` on the bridge (sync — waits for both Lambda + EC2 results)
2. Formats the JSON response into a readable summary
3. Attempts email delivery to TapEase stakeholders

**Email Recipients (when SMTP credentials are configured):**
- `shoaib.habib@a2square.com.au` (TapEase)
- `admin@harishabib.au`
- `hhsiddiqui@gmail.com`
- `habibshoaib841@gmail.com`

Email requires `SMTP_USERNAME` and `SMTP_PASSWORD` in `C:\Users\habib\.openclaw\.env`. If password is `***`, email is skipped and Telegram delivery is the only channel.

## Pitfalls

- **Bridge must be running** before any cron fires. If the bridge is down, all cross-fleet monitors fail silently (the Hermes cron still reports `ok` because `no_agent` scripts exit 0 even when curl returns an error). **Mitigation:** Check bridge health first in the runner script.
- **PowerShell encoding** — Always save `.ps1` files with UTF-8 BOM. Without it, Unicode chars (—, ✅, ❌) in string literals cause parser errors (`Unexpected token 'Lambda'`).
- **Script timeout** — The bridge's `execPromise` has a 300s timeout. PowerShell scripts that query AWS APIs can take 60s+. If the monitor needs more time, increase the timeout in the bridge JS.
- **Email delivery** — The runner script can send email via Purelymail SMTP, but only if `SMTP_PASSWORD` is set (not `***`). Telegram delivery via cron stdout is the primary channel.
