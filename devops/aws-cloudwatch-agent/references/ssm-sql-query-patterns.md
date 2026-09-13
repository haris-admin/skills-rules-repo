# SSM SQL Query Patterns (via send-command)

When running database queries through SSM send-command (e.g., psql on backend EC2 to query a private RDS), SSM's 3000-char response truncation means you must batch queries and use base64 encoding for SQL files.

## Contents
- [Base64 SQL File Pattern](#base64-sql-file-pattern)
- [Parse Labeled Multi-Query Output](#parse-labeled-multi-query-output)
- [SSM Port Forwarding (Preferred for Database Access)](#ssm-port-forwarding-preferred-for-database-access)
- [Pitfall: PostgreSQL `AT TIME ZONE` Works Backwards on Strings](#pitfall-postgresql-at-time-zone-works-backwards-on-strings)
- [Pitfall: RDS username — NEVER hardcode `-U <name>`, read it from the secret](#pitfall-rds-username-never-hardcode--u-name-read-it-from-the-secret)
- [Pitfall: JSON quoting of SQL with newlines](#pitfall-json-quoting-of-sql-with-newlines)
- [Pitfall: Dollar-format Double-Division Bug](#pitfall-dollar-format-double-division-bug)

## Base64 SQL File Pattern

```python
import base64

sql = """
SELECT '###LABEL1' as lbl,
  (SELECT COUNT(*) FROM table1) as col1,
  (SELECT COUNT(*) FROM table2) as col2;
SELECT '###LABEL2' as lbl,
  (SELECT COUNT(*) FROM table3) as col3;
"""
encoded = base64.b64encode(sql.encode()).decode()
ssm(f"echo '{encoded}' | base64 -d > /tmp/query.sql", timeout_sec=15)
output = ssm(f"psql -h {rds_host} -U {user} -d {db} -At -f /tmp/query.sql", timeout_sec=90)
```

## Parse Labeled Multi-Query Output

Each SELECT in a psql batch outputs one line. Use `###` prefix for labels:

```python
for line in output.strip().split("\n"):
    if not line.startswith("###"): continue
    parts = line[3:].split("|")
    label, values = parts[0], parts[1:]
```

## SSM Port Forwarding (Preferred for Database Access)

SSM `send-command` truncates output at ~3000 characters. For database queries returning lots of data (full CSV exports, large result sets), use **SSM port forwarding** instead:

```bash
aws ssm start-session --region ap-southeast-2 --target i-XXXX \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters '{"host":["my-db.rds.amazonaws.com"],"portNumber":["5432"],"localPortNumber":["5434"]}'
```

Then `psql -h localhost -p 5434 ...` locally. Requires `session-manager-plugin` (`sudo dpkg -i` the Ubuntu `.deb` from the S3 bucket).

**Python lifecycle pattern:** Start `subprocess.Popen` in background, write PID to `/tmp/ssm_tunnel.pid`, `os.kill(pid, SIGTERM)` on cleanup. The tunnel connects THROUGH the EC2 to reach the RDS — EC2 must be running with SSM Agent online.

## Pitfall: PostgreSQL `AT TIME ZONE` Works Backwards on Strings

**Do NOT do this** (the string is implicitly cast to `timestamptz` (UTC), not `timestamp`):

```sql
-- WRONG — interprets '09:00' as UTC, converts TO Sydney time (19:00)
WHERE performed_at >= ('2026-07-14 09:00:00' AT TIME ZONE 'Australia/Sydney')
```

This shifts the window by 10 hours: PostgreSQL casts the bare string to `timestamptz` (UTC), then `AT TIME ZONE` converts that UTC timestamptz TO local Sydney time — the reverse of what you intended.

**CORRECT — compute UTC equivalents in Python:**

```python
from datetime import datetime, timezone, timedelta
aest = timezone(timedelta(hours=10))
lower = datetime.strptime("2026-07-14 09:00:00", "%Y-%m-%d %H:%M:%S").replace(tzinfo=aest)
upper = datetime.strptime("2026-07-14 21:00:00", "%Y-%m-%d %H:%M:%S").replace(tzinfo=aest)
lower_utc = lower.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
upper_utc = upper.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
```

Then use UTC strings in SQL:

```sql
-- CORRECT — unambiguous UTC comparison
WHERE performed_at >= '2026-07-13 23:00:00 UTC'
  AND performed_at < '2026-07-14 11:00:00 UTC'
```

**Rule of thumb:** Never rely on `AT TIME ZONE` with bare string literals. Convert in application code, use UTC strings in SQL.

## Pitfall: RDS username — NEVER hardcode `-U <name>`, read it from the secret

(Aug 2026)

**The `amlhive/prod/rds` secret's `username` is NOT `amlhive`** — it's a 16-char name containing "amlhive". Hardcoding `-U amlhive` produces:

```
FATAL: password authentication failed for user "amlhive"
```

even with the **CORRECT** password — the password is fine, it's being presented under the wrong username. This bit `amlhive_daily_report.py` (fixed Aug 2026 with `fetch_creds()` returning `(username, password)`).

**Pattern for any SSM→psql script:**
```python
# From Secrets Manager secret (amlhive/prod/rds):
u = s.get("username") or s.get("Username") or "amlhive"
p = s.get("password") or s.get("Password")
# use -U {u} in the psql command, NEVER a hardcoded user
ssm(f'PGSSLMODE=require PGPASSWORD="{p}" psql -h {host} -U {u} -d amlhive -At -c "{sql}"')
```

**Secret lookup order:** try `amlhive/prod/rds` FIRST (live in account 560205084533), then `amlhive/prod/rds-admin`, and `tapease/rds/credentials-production` LAST or not at all (it does NOT exist in the AMLHive account — it's a Tapease-account secret). Signature of the correct live secret: `username(len=16)`, `password(len=44)`.

## Pitfall: JSON quoting of SQL with newlines

`json.dumps(sql)` for SSM `--parameters` interprets `\n` as escapes. Use single-line SQL or write to a file via base64 (above). The base64 approach is safest — no quoting issues.

## Pitfall: Dollar-format Double-Division Bug

When converting cents to dollars for display, use a single conversion function and ALWAYS pass raw cents:

```python
def doll(cents):
    return f"${int(cents)/100:,.2f}"

# ✅ CORRECT: pass raw cents
sur_display = doll(t_sur)  # t_sur = 30000 cents → "$300.00"

# ❌ WRONG: pre-converted to dollars, then divided again
sur_display = doll(t_sur / 100.0)  # "$3.00" instead of "$300.00"
```

**Rule:** Track the unit of every numeric variable. If a variable name doesn't encode its unit (`t_sur` = cents, `sur_d` = dollars), you will accidentally double-divide. Name convention: `_d` suffix for dollars, raw is cents. The `doll()` function ALWAYS expects cents. Never pass a dollar-denominated value to a cents-to-dollars formatter.
