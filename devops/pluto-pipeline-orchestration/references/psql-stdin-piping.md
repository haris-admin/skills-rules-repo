# Psql Stdin Piping — Avoid ARG_MAX on Large Data

Discovered July 4, 2026 while fixing the podcast ingestion cron's persistent exit-code-1 error.

## Problem

Passing SQL to `psql` via the `-c` flag embeds the query in the command-line arguments. When the SQL contains large data (e.g., a full podcast transcript in a dollar-quoted INSERT), the total `argv` size can exceed the OS ARG_MAX limit (~128KB on Linux). Result: `[Errno 7] Argument list too long: 'psql'`.

## Symptom Signature

```
CRITICAL: ... failed: [Errno 7] Argument list too long: 'psql'
```

The script succeeds for small/payload records, then crashes on the first large one. Looks like a timeout or partial success — but it's an OS-level argument ceiling.

## Fix

Pipe SQL via stdin instead of `-c`:

```python
# BEFORE (ARG_MAX limit):
def run_sql(sql):
    result = subprocess.run(
        ['psql', '-h', host, '-p', port, '-U', user, '-d', db, '-c', sql],
        capture_output=True, text=True, timeout=20, env=env
    )
    return result.returncode == 0, result.stdout, result.stderr

# AFTER (no limit — stdin piping):
def run_sql(sql):
    result = subprocess.run(
        ['psql', '-h', host, '-p', port, '-U', user, '-d', db, '--no-psqlrc'],
        input=sql, capture_output=True, text=True, timeout=20, env=env
    )
    return result.returncode == 0, result.stdout, result.stderr
```

## Flags to Keep

- `--no-psqlrc` — skip startup file (faster, cleaner)
- Do NOT add `-q` or `-t` unless you've verified output parsing won't break. `-t` strips headers/footers which can silently corrupt row-count-based parsers that skip `[2:-1]` lines.

## Cross-Script Applicability

Any `no_agent` Python script that uses `psql -c` with variable-length data should use stdin piping:
- `podcast_ingestor.py` — ✅ Fixed July 4, 2026
- `podcast_insight_extractor.py` — candidate
- `competitor_intel.py` — candidate
- Any future script inserting large text blobs into Supabase

## Verification

```bash
# Test the fix with a live connection:
python3 -c "
import subprocess, os
env = os.environ.copy()
env['PGPASSWORD'] = '<password>'
env['PGSSLMODE'] = 'require'
sql = 'SELECT COUNT(*) FROM podcast_kb.episodes;'
r = subprocess.run(
    ['psql', '-h', 'aws-1-ap-southeast-2.pooler.supabase.com', 
     '-p', '6543', '-U', 'postgres.vyqagemgwxfscppkfswq', '-d', 'postgres', '--no-psqlrc'],
    input=sql, capture_output=True, text=True, timeout=20, env=env
)
print(f'exit={r.returncode} out={r.stdout[:100]}')
"
# Should show: exit=0 out= count\n-------\n   NNN
```
