# Robust Cron Script Patterns

## SSM Tunnel
- **Script location**: `~/.hermes/scripts/start_tapease_tunnel.sh` — NEVER `/tmp/` (tmpfs cleaned between runs)
- **PID file**: `/tmp/ssm_tunnel.pid`. ALWAYS check `os.path.exists()` before reading. Write in try/except.
- **Tunnel startup**: Use `subprocess.Popen([script], stdout=DEVNULL, stderr=DEVNULL)` with `time.sleep(4)` to let tunnel establish
- **Tunnel cleanup**: Kill PID and delete PID + temp files after script completes. Wrap kill in try/except.

## Empty Results
- `\copy` produces NO file when query returns 0 rows
- Guard ALL three file accesses with try/except OSError:
  1. Reading CSV for parsing: `open(CSV_PATH)`
  2. Checking file size: `os.path.getsize(CSV_PATH)`
  3. Attaching CSV to email: `open(CSV_PATH, "rb")`
- When csv_raw is empty string, `csv.DictReader(io.StringIO(""))` returns empty list — works fine

## Cron Delivery
- Cron jobs use `no_agent: true` for pure script execution
- `deliver: "origin"` makes output appear in the user's chat — required for visibility
- `deliver: "local"` saves to files in `.hermes/cron/output/` — user never sees it
- Scripts send their OWN emails via internal SMTP code; cron delivery is for transcript visibility

## Window Computation (UTC)
- **ALWAYS** pre-compute UTC in Python — NEVER use `AT TIME ZONE` in SQL
- Pattern:
  ```python
  aest_tz = timezone(timedelta(hours=10))
  lower = datetime.strptime(f"{date} 09:00:00", "%Y-%m-%d %H:%M:%S").replace(tzinfo=aest_tz)
  upper = datetime.strptime(f"{date} 21:00:00", "%Y-%m-%d %H:%M:%S").replace(tzinfo=aest_tz)
  LOWER_UTC = lower.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
  UPPER_UTC = upper.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
  ```
- Use in SQL: `WHERE col >= '{LOWER_UTC} UTC' AND col <= '{UPPER_UTC} UTC'`
