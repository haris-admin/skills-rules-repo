---
name: windows-update-wsl
description: "Use when managing Windows Updates from WSL/Hermes cron."
---

# Windows Update from WSL

## When to Use
- Scheduling/managing Windows Update checks+installs from Hermes (WSL host).
- Auditing why the weekly Windows update cron behaves a certain way.

## Working Setup (verified Aug 2026)
- **Cron:** `c4f4696d9717` — "🪟 Weekly Windows Update Check (Mon 2AM)" — `no_agent`, script `windows_update_weekly.sh`, deliver to daily_status_v2.
- **Scripts:**
  - `~/.hermes/scripts/windows_update_weekly.sh` — WSL wrapper (wslpath + powershell.exe -File)
  - `~/.hermes/scripts/windows_update_weekly.ps1` — scan + trigger + report; supports `-DryRun` switch
- **User:** habib is in Administrators group but NOT elevated from WSL (`IsAdmin: False`). PSWindowsUpdate module NOT installed.

## Mechanism (works non-elevated)
1. **Scan:** COM API — `New-Object -ComObject Microsoft.Update.Session` → `CreateUpdateSearcher().Search('IsInstalled=0')`. Works fine from WSL→powershell.exe, no admin.
2. **Trigger install:** `UsoClient StartInstall` (signals Update Orchestrator, same path as Settings button). Exit 0 = queued.
3. **Reboot pending:** check `HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired` (+ non-Auto variant).
4. **UsoClient StartScan** also works (harmless rescan).

## Pitfalls (all hit in real runs)
- **Encoding:** PowerShell 5.1 via WSL chokes on non-ASCII (em-dash `—`) inside .ps1 → `Unexpected token` parse errors. Keep .ps1 strictly ASCII (use `-` not `—`).
- **Env vars DON'T cross WSL→Windows:** `WU_DRY_RUN=1 script.sh` is invisible to powershell.exe — the trigger block ran on a "dry run". Use a script ARG (`-DryRun` switch) instead of env vars.
- **Elevation:** `schtasks /create /rl highest` → Access denied from WSL. Can't register elevated scheduled tasks non-interactively. Don't try COM `.Install()` directly — ResultCode 4 (Failed) without elevation; UsoClient is the right path.
- **wslpath:** use `wslpath -w` to convert the script path (fallback to raw path).
- **Watchdog pattern:** no_agent cron delivers stdout; empty output = silent. The script always prints a report (6 pending updates etc.), so it pings every Mon 2AM — by design (Haris asked for a visible check).

## Manual Trigger
```bash
/home/habib/.hermes/scripts/windows_update_weekly.sh          # real run (triggers install)
/home/habib/.hermes/scripts/windows_update_weekly.sh --dry-run # scan + report only
```

## Note
Installing updates may require a Windows reboot, which kills the WSL session/gateway briefly. Warn Haris before triggering installs during a session.
