# Profile .env & Invocation Checklist (2026-08-22)

Third failure mode discovered when engaging Mercury fleet agents for real work:
hand-created profiles fail on first `chat` because they have no `.env`.

## The failure

```
hermes -p sol chat -q "..."
...
No usable credentials found for provider 'deepseek'. Set DEEPSEEK_API_KEY.
Goodbye!
```

## Root cause

`write_file` directory trees (`profiles/<name>/SOUL.md`, `AGENT.md`,
`config.yaml`, `memories/`, `skills/`) do NOT copy the root `.env`. Hermes
profiles do not inherit the parent `.env` automatically — each profile needs
its own copy with provider keys.

## The fix (BEFORE first run of any hand-created profile)

```bash
# Windows MSI install (Mercury):
for d in sol vulcan aurora lumen vigil caduceus; do
  cp /mnt/c/Users/<user>/AppData/Local/hermes/.env \
     /mnt/c/Users/<user>/AppData/Local/hermes/profiles/$d/.env
done
# WSL equivalent: cp ~/.hermes/.env ~/.hermes/profiles/<name>/.env
```

26KB class file; all synced provider keys ride along (DEEPSEEK, OPENROUTER,
OPENAI, TELEGRAM, HONCHO, SMTP, R2, SENTRY...). Copy values by NAME only,
never print.

## Also verified (full invocation checklist)

1. Use `powershell.exe -NoProfile -Command "cd C:\Users\<user>\AppData\Local\hermes\hermes-agent; .\venv\Scripts\python.exe hermes -p <name> chat -q \"<task>\"" 2>&1`
2. Must be `.\\venv\\Scripts\\python.exe` (has `concurrent_log_handler`), NOT bare `python hermes`
3. Must go through PowerShell so HERMES_HOME resolves to the Windows profile store
4. Run `background=true` + `notify_on_complete=true`; pull full output with `process(action='log', offset=...)`
5. Verify with `.\venv\Scripts\python.exe hermes profile list` and `hermes -p <name> skills list` before the real task
