---
name: wsl-windows-interop
description: Use when driving Windows apps or browsers from WSL.
version: 1.0.0
author: mercury
license: MIT
metadata:
  hermes:
    tags: [WSL, Windows, interop, PowerShell, browser]
    related_skills: [web-data-acquisition, windows-update-wsl, hermes-runtime-maintenance]
---

# WSL ↔ Windows interop

Driving the Windows host from inside WSL: launching GUI apps the user can actually see, invoking
PowerShell from bash without quoting damage, and reaching Windows-local services.

## When to Use

- The user says "open a browser", "open it on my machine", or "I can't see it" after you showed a
  browser screenshot.
- A page needs the user to sign in or interact, so an agent-side browser cannot finish the job.
- You need a Windows window's title, to bring an app to the front, or to launch Chrome/Edge deliberately.
- You need to reach a service bound on the Windows host from inside WSL.

## The rule that matters most: the browser tools are NOT the user's browser

The `browser_*` tools drive a **remote browser on the agent's side**. It renders, screenshots and reads
pages correctly — but it is not a window on the user's machine, so they cannot see it or type into it.

When the user says *"open a browser"*, *"I can't see it on the machine"*, or is expected to sign in,
launch a real window on the Windows host instead. The tell is a screenshot the user says they cannot
see: that is not a rendering problem, it is the wrong browser.

## Launch a real window on the host

```bash
# default browser
powershell.exe -NoProfile -Command "Start-Process 'https://example.com'"

# explicit Chrome, new window (so it does not hide in an existing tab)
powershell.exe -NoProfile -Command "Start-Process 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe' -ArgumentList '--new-window','https://example.com'"

# cmd fallback — the empty "" is the window title and is required
cmd.exe /c start "" "https://example.com"
```

**Verify, do not assume.** The window title also tells you *what actually loaded* — useful when a
portal URL redirects to something else:

```bash
# an installed Store / MSIX app has no exe on PATH — launch it by its AUMID
powershell.exe -NoProfile -Command "Start-Process 'shell:AppsFolder\Files_1y0xx7n9077q4!App'"
# derive the PackageFamilyName first; the app's display name is not the package name
powershell.exe -NoProfile -Command "Get-AppxPackage -Name '*Files*' | Select-Object Name,Version,PackageFamilyName | Format-List"
```

A finished launch prints nothing, so never read silence as failure. A Store app that seems not to have
started has frequently opened a release-notes or what's-new window instead — query the process title
before concluding it did not run.

```bash
powershell.exe -NoProfile -Command "Get-Process chrome -ErrorAction SilentlyContinue | Select-Object -ExpandProperty MainWindowTitle"
```

Bring it to the front — windows routinely open behind others:

```bash
powershell.exe -NoProfile -Command "(New-Object -ComObject WScript.Shell).AppActivate('Sign in - Google Accounts - Google Chrome')"
# prints True / False
```

`AppActivate` takes the **exact** window title, so read it from the process query first.

## PowerShell from bash — the quoting rules that bite

- **Never put `$_` inside a bash double-quoted PowerShell command.** Bash expands it first, so
  `Where-Object {$_.MainWindowTitle -ne ''}` becomes `Where-Object {/home/habib/.local/bin/env -ne ''}`
  and PowerShell throws *"not recognized as the name of a cmdlet"* **once per pipeline item** — a wall of
  identical errors that reads like a broken host. Use a form needing no `$_`
  (`Select-Object -ExpandProperty X`, `Get-Process X | Format-List`), or write a `.ps1` to a
  Windows-visible path and run it with `-File`.
- **Single quotes inside the double-quoted command** for paths and URLs:
  `powershell.exe -NoProfile -Command "Start-Process 'C:\path\app.exe'"`. Backslashes survive as-is;
  do not escape them a second time.
- **`cmd.exe` started from a WSL cwd warns `UNC paths are not supported`** and falls back to the Windows
directory. Harmless; the command still runs.
- **`wsl.exe` answers in UTF-16, so anything derived from its output arrives corrupted.**
  `wsl.exe -l -q` captured through bash gives `U\0b\0u\0n\0t\0u\0`, and the UNC path built from that
  name then fails `Test-Path` with *Illegal characters in path* — which reads exactly like the share
  being unreachable when it is perfectly fine. Set `WSL_UTF8=1` for the call, or pipe through
  `iconv -f UTF-16LE -t UTF-8 | tr -d '\r'`, and only then build the path
  (`\\wsl.localhost\<distro>\home\<user>`). Confirming that share resolves is the cheap way to prove a
  Windows-side tool can actually browse WSL files before you recommend it.
- **Pipe output through `| tr -d '\r'`** before comparing or parsing it — every PowerShell line otherwise
  carries a trailing CR that breaks exact matching.
- **Never route PowerShell through `cmd.exe /c`.** `cmd.exe /c "powershell -NoProfile -Command \"...\""`
  collapses the inner quotes, and PowerShell then *echoes the command text back* instead of executing it —
  the "output" is your own command, which reads like a successful run and silently hides the missing result.
  Call `powershell.exe -NoProfile -Command "<script>"` directly as argv (there is no shell in between to
  mangle quotes), or write a `.ps1` to a Windows-visible path and run it with `-File`.

## PowerShell → native exe: JSON arguments do not survive

`--parameters '<json>'` passed from PowerShell to a **native exe** (`aws.exe`, `gh.exe`, any Go/Node CLI)
loses its embedded double quotes: Windows PowerShell 5.1 builds the child argv itself and strips them, so
the child receives `{host:[...]}` and dies with *Invalid JSON: Expecting property name enclosed in double
quotes*. The error quotes the payload, so it reads like a bad argument rather than a quoting layer — and
the natural next move (adding more escapes) is the wrong one.

Remove the quoting layer instead:

- **Prefer file-based input.** `aws ... --cli-input-json file://C:/path/params.json` — forward slashes in
the URL, backslashes in the filesystem path. Build the object with `ConvertTo-Json -Depth 5`, write it to
`$env:TEMP`, derive the URL as `'file://' + ($tmp -replace '\\','/')`, and delete it in `finally`. It is
self-contained, so there is no companion file to drift or go stale.
- Only then consider `--%` (stop-parsing) or hand-escaped `\"`; both are fragile across PowerShell versions.
- The same shape works for any CLI taking `--cli-input-json`, `--input`, or `@file`. Reach for it whenever
the argument is JSON.

This is a **different layer** from the bash `$_` rule above: bash damages the command before PowerShell
sees it; this damages the argv after PowerShell has parsed it. A JSON argument can fail with neither a
network nor a credentials problem behind it.

## A `.ps1` is read as ANSI — keep it ASCII

PowerShell 5.1 decodes a `.ps1` as the ANSI code page unless it carries a UTF-8 BOM, so a non-ASCII
character (em dash, curly quote, glyph) is a **parse error**, not a cosmetic issue. The parser then
reports the character's byte and quotes garbled text, which looks like a mangled string rather than an
encoding fault. Write `.ps1` files ASCII-only and use plain hyphens in comments.

## Running a Windows-only tool from a WSL cron

When the tool exists only on Windows (a Windows-PATH binary, or a plugin WSL lacks), the whole job must
run Windows-side. Cron runs in WSL, so put a thin `.sh` wrapper in `~/.hermes/scripts/` and let it exec
PowerShell:

```bash
#!/usr/bin/env bash
set -uo pipefail
PS1_WSL='/mnt/c/Users/<user>/hermes-scripts/<name>.ps1'
PWSH='/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe'
[ -f "$PS1_WSL" ] || { echo "FAILED: script not found at $PS1_WSL"; exit 1; }
exec "$PWSH" -NoProfile -ExecutionPolicy Bypass -File 'C:\Users\<user>\hermes-scripts\<name>.ps1'
```

- `exec` so the script's own `exit 1` reaches cron as the job's exit code; cron alerts on non-zero.
- Pass `-File` the **Windows** path (`C:\...`) and test existence with the **/mnt/c** path.
- `-ExecutionPolicy Bypass` is needed for any script written from WSL.
- Verify the Windows prerequisites with a `.ps1` probe file, never `-Command` (bash eats `$`):
  `foreach ($b in 'aws','psql','x') { $c = Get-Command $b -EA SilentlyContinue; if ($c) { $c.Source } else { "$b MISSING" } }`.
- **Run it once by hand before scheduling, and read the printed text, not just the exit code.** A wrapper
  can exit 0 while the inner script printed `FAILED: ...` if the failure path sets the code after a
  pipeline; the first run is the only cheap moment to catch that.
- Output read back from Python needs `errors='replace'` (or a redirect to a file first): PowerShell emits
  ANSI/UTF-16 bytes and a strict utf-8 decode raises `UnicodeDecodeError` on bytes like `0x83`.

Worked example of the whole shape — Windows-side tunnel + read-only SQL report + teardown:
`references/ssm-port-forward-sql.md`. Its load-bearing rule: a forwarded port is visible only on the
machine that opened the tunnel, so the tunnel and the client must be on the same side.

## Windows-host package management (npm CLIs, winget)

Windows npm pins `prefix` to `C:\Program Files\nodejs`, so `npm i -g <pkg>` run from WSL dies with
**EPERM** (`mkdir ...\node_modules\@scope`). The already-installed shims usually live in
`%APPDATA%\npm`, which *is* on PATH — so the fix is a per-install prefix, never elevation:

```bash
# unelevated global install that PATH actually picks up
npm i -g --prefix "$env:APPDATA\npm" <pkg>@latest            # via powershell.exe
& "$env:APPDATA\npm\<cmd>.cmd" --version                     # verify the shim, not the package dir
```

- Writing `prefix=` into `~/.npmrc` does **not** win here: the global config at
  `C:\Program Files\nodejs\etc\npmrc` keeps reporting itself, so `npm config get prefix` still answers
  Program Files and `npm ls -g` goes **blind to user-prefix packages** (reports empty). Probe versions
  with the CLI itself (`<cmd> --version`) or `(Get-Command <cmd>).Source` instead of `npm ls -g`.
- winget-installed tools upgrade unelevated:
  `winget upgrade --id <id> --accept-source-agreements --accept-package-agreements --disable-interactivity`.
- **winget also installs MSIX/AppX GUI apps unelevated from WSL**, printing `Successfully verified
  installer hash` before install. Judge the result with `winget list --id <Vendor.Package>` (the honest
  check) rather than the exit code, then `Get-AppxPackage` for the AUMID needed to launch it. A trial
  install stays reversible: record the matching `winget uninstall --id <Vendor.Package>` as you go, and
  do not flip a default association (file handler, shell integration) until the user has lived with the
  trial and asked for it.
- A CLI can be installed more than once per machine (native installer in `%USERPROFILE%\.local\bin`, npm
  in `%APPDATA%\npm`, winget package dir). Resolve *which* one PATH hits before declaring a version —
  updating the wrong copy leaves the old binary in front.

## Reaching a Windows-local service from WSL

`127.0.0.1` inside WSL is WSL, not Windows. For a service bound on the host (a DevTools port, a local
API), use the host IP:

```bash
cat /etc/resolv.conf | grep nameserver | awk '{print $2}' | head -1
```

Then `curl http://<host-ip>:<port>/...`. Connection refused means the service is not listening — not
that the address is wrong.

`/etc/resolv.conf` is not always the reliable answer: enumerating from the Windows side returns the real
candidates, and several of them are link-local noise to ignore.

```bash
powershell.exe -NoProfile -Command \
  "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '127.*' } | Select-Object -ExpandProperty IPAddress) -join ','"
# typical: 172.27.0.1,169.254.x.x...,192.168.x.x  -> the RFC1918 one is the host; 169.254.* is APIPA, never the answer
```

**A service must also be bound to a non-loopback address**, or the host IP cannot reach it however
correct that IP is. Steer by the listener, not by assumption: `ss -lntp`, `docker port <container>` and
`docker inspect --format '{{json .NetworkSettings.Ports}}'` show the real bind before you start
searching for the right address.

**Chrome's DevTools port is the case where this flag does not help.** Even launched with
`--remote-debugging-address=0.0.0.0`, the debugging endpoint stayed unreachable from WSL on every
host IP while answering instantly from Windows. Do not burn calls hunting an address: run the CDP
calls **on the Windows side** with PowerShell (`System.Net.WebSockets.ClientWebSocket`) and let that
script write its result to a file under `/mnt/c/...`, then read the file from WSL. Full recipe:
`references/cdp-authenticated-app-read.md`.

## Chrome specifics

- **One instance per profile.** You cannot attach `--remote-debugging-port` to an already-running Chrome
  reusing the same user-data dir; the new process hands off to the existing one and the port never opens.
  Reading a signed-in page over CDP therefore needs the browser **closed first** — ask before doing it.
- **If the user must sign in, launch the window and let them.** Never type their password; use the vault
  tools when a session genuinely needs credentials in an automated browser.
- **Detect a dead session from the target list, before attempting any read.** After launching, fetch
  `curl -s http://localhost:9222/json` and read the page targets' `title`/`url`. A target whose URL is
  `accounts.google.com/v3/signin/...` (or titled `Sign in`) means the profile has LOST its session — a
  Chrome major-version update clears it, not just a profile swap. Report "sign-in needed" and stop; do
  not retry the read, and do not treat the sign-in page as page content.
- **Ask for share-link access instead of a browser session when the goal is scheduled/repeatable.**
  A CDP-attached session is a fragile dependency for a cron: it expires silently and the job then reads a
  sign-in page as if it were data. A viewable link (Sheets/Docs "anyone with the link can view") keeps the
  fetch headless and unauthenticated forever. Prefer it for anything that must run unattended.
- **Launch GUI apps with several flags through a `.ps1` run with `-File`, not an inline `-Command`.**
  Long inline `Start-Process` argument lists are where the bash/PowerShell quoting layers and WSL interop
  both fail; a script file removes the quoting entirely and gives you a place to verify afterwards.
- **Reading data out of a signed-in web app has its own shape:** navigate the authenticated tab to the
  app's export endpoint and read the file it downloads, rather than scraping the DOM — Sheets renders
  cells to canvas and its tab ids are obfuscated, so DOM reads return nothing. Recipe and dead ends:
  `references/cdp-authenticated-app-read.md`.
- **Opening a signed-in page is usually unnecessary.** Check whether the same content has a public
  canonical URL before asking for a login — see `web-data-acquisition`'s login-gate rule.

## Screenshots you can attach to a reply

Screenshots from the vision tool land on disk even when the tool does not print a path:

```bash
find ~/.hermes/cache/screenshots -name '*.png' -newermt '-10 minutes'
```

Attach the newest one with `MEDIA:<path>` when the user needs to see agent-side state (for example, to
show what a gated page looks like before deciding to authenticate).

## Related

- `web-data-acquisition` — the login-gate-is-an-artefact-of-the-URL rule, which usually removes the need
  to open anything at all.
- `windows-update-wsl` — other host-side PowerShell automation.
- `hermes-runtime-maintenance` — the WSL-side Hermes runtime this drives.
