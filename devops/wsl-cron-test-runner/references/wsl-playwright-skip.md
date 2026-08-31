# WSL Playwright Browsers — No-Sudo Install (Aug 2026)

**OUTDATED (pre-Aug-2026): this reference previously said Playwright can't run on WSL and recommended skipping. ALL THREE browsers (Chromium, Firefox, WebKit) now run on WSL without sudo.** See the "WSL Chromium — NO-SUDO Local Deps Fix" section in SKILL.md for the full recipe. Keep this file only for the historical skip-pattern warning: never blind-skip WSL E2E — install the browsers instead.

## Detection (for the guard, not the skip)

Use `/proc/sys/fs/binfmt_misc/WSLInterop` to detect WSL at runtime — but instead of skipping, run with the local deps:

```python
from pathlib import Path
LOCAL_CHROMIUM_LIBS = "/home/habib/.local/chromium-deps/root/usr/lib/x86_64-linux-gnu"

if not Path(LOCAL_CHROMIUM_LIBS + "/libnspr4.so").exists():
    print("   ⚪ Skipped — Chromium deps not installed (run the one-time setup)")
    results["playwright"] = {"passed": 0, "failed": 0}
else:
    _e2e_env = dict(os.environ)
    _e2e_env["LD_LIBRARY_PATH"] = LOCAL_CHROMIUM_LIBS + ":" + _e2e_env.get("LD_LIBRARY_PATH", "")
    _e2e_env["PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS"] = "1"  # REQUIRED
    r = run_test(["npm", "run", "test:e2e", ...], FRONTEND, timeout=1800, env=_e2e_env)
```

## Why "Playwright can't run on WSL" was wrong

- The `--with-deps` flag needs sudo, but `apt download` + `dpkg-deb -x` into a user-local prefix needs NO sudo — all 212 WebKit system packages downloaded and extracted this way (0 failures).
- `PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1` bypasses Playwright's system-path `ldd` validation, letting it launch browsers from the local prefix.
- WebKit's `pw_run.sh` + `MiniBrowser` wrapper scripts OVERWRITE LD_LIBRARY_PATH — patch both to append the local prefix (`${MYDIR}/lib:${MYDIR}/sys/lib:<local-prefix>`).
- WebKit needs `libwoff2dec` (`apt download libwoff1`); `libjxl.so.0.8` + `libbacktrace.so.0` come from the WebKit bundle's own `sys/lib/`.
- The old 343-failure cascade was an auth-setup failure (`[auth-setup]` failing → all dependent tests fail at 1ms), NOT a browser-missing problem.

## Verification

```bash
# Chromium
$CHROME --headless --no-sandbox --disable-gpu --dump-dom "data:text/html,<h1>OK</h1>"
# Firefox — note: binary is firefox-1522/firefox/firefox-bin (top-level 'firefox' is a directory!)
# WebKit — passes via Playwright with the env var; shows "Skipping host requirements validation logic"
```
