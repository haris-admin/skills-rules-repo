# Watcher Cron Agent Path Fix (May 26, 2026)

## Problem
The Mempalace Inbox Watcher cron agent (job `5678a363ce3b`) repeatedly searched non-existent paths:
- `/home/habib/.hermes/mempalace/inputs/` (doesn't exist)
- `/home/habib/.hermes/data/mempalace-inputs/` (doesn't exist)
- `/home/habib/.hermes/inputs/` (doesn't exist)
- `/home/habib/.mempalace/inputs/` (doesn't exist)

Correct path: `/home/habib/.hermes/mempalace-inputs/` (23 files, all processed as of May 26).

## Fixed Cron Prompt
```
Run the mempalace-inputs watcher to process any new research files.

CRITICAL: The correct directory is /home/habib/.hermes/mempalace-inputs/ (it EXISTS with .md files). Do NOT search for /mempalace/, /mempalace/inputs/, /data/mempalace-inputs/, or any other variation.

Steps:
1. Run: cd /home/habib/.hermes && /home/habib/.hermes/venv/bin/python3 /home/habib/.hermes/scripts/mempalace_watcher.py
2. If there are pending files (listed by the watcher), process them through the feeder: /home/habib/.hermes/venv/bin/python3 /home/habib/.hermes/scripts/pluto_mempalace_feeder.py --file <filename>
3. If no pending files, do nothing else. Report "No new files to process."

Important: the watcher script handles its own state tracking. Just run it and follow its output.
```

## Verification
```bash
~/hermes/venv/bin/python3 ~/.hermes/scripts/mempalace_watcher.py --status
```

## DEEPSEEK_API_KEY Expiry Pattern (May 22-24, 2026)
When the DeepSeek API key becomes invalid:
1. ALL cron jobs using deepseek provider fail with `last_status: error`
2. Error log: `HTTP 401: Authentication Fails, Your api key: ****d876 is invalid`
3. Mempalace watcher (every 5 min) racks up hundreds of failures
4. After key fix: check all cron jobs — error status from outage window self-heals on next scheduled run

Investigation: `cronjob list` → grep errors.log for `401.*invalid` → trace timestamps → fix key.
