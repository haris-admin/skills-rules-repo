# Expected Test Suite Timings on WSL

Measured durations for the AMLHive/Tapease suites on WSL, both on the NTFS-mounted repo (`/mnt/c/`) and on native ext4 (`~/code/`), used to set runner timeouts and to sanity-check whether a run is abnormally slow.

## Measured (WSL, Repo on NTFS /mnt/c)

| Suite | Est. Duration | Notes |
|-------|--------------|-------|
| Backend pytest (full suite, ~5000 tests) | **10-11 min** (NTFS) — **~14 min** (ext4) | Suite takes 888s (~15 min) on WSL even on native ext4. macOS M-series completes in 302s. WSL CPU is slower — not just filesystem. |
| Backend health tests (13 tests) | **17s** | First test fails (SSL), rest pass fast |
| Playwright (10+ spec files) | ~3-5 min | Includes dev server start via webServer config |
| Playwright (single small file) | ~30-60s | With workers=1, retries=0 |
| Jest (any project on WSL) | **30-60 min** | TS compilation on /mnt/c = ~35s-per-file. With 95 files: 55 min. **Avoid in daily cron** |
| Jest (single test file) | ~35s | Still dominated by TS compilation, not test execution |
| Browser install (first run) | ~2-3 min | Downloads ~300MB Chromium. Subsequent runs are instant (cache) |

## Measured (WSL, Repo on Native ext4 ~/code/) — 3-4x Speedup

Repo residing on native ext4 (e.g. `~/code/amlhive1/`) instead of NTFS (`/mnt/c/`) gives near-native Linux I/O performance:

| Suite | NTFS (/mnt/c) | Native ext4 (~/code/) | Speedup |
|-------|---------------|----------------------|---------|
| Backend health tests (13 tests) | 17s | **5s** | 3.4x |
| Backend full pytest (~5000 tests) | NTFS: 600s+ (timeout) | **~893s** (888-893s measured) | ~1x (WSL CPU, not FS, is the bottleneck) |
| Frontend Vitest (native ext4) | **~30-60s** (estimated) | **~30-60s** | Same (depends on npm/node, not FS) |
| Playwright E2E (webServer auto-start) | ~3-5 min | ~3-5 min | Server start dominates, not FS |
| Jest (any project on WSL) | **30-60 min** | ~30-60 min | TS compilation not worth it on WSL — **use Vitest instead** |

**Tip:** Keep the repo on both mount points. Use `/mnt/c/...` for IDE editing (VS Code/WSL extension), `~/code/...` for running tests/cron jobs. Copy with: `rsync -a /mnt/c/Code/github/amlhive-tech/amlhive1/ ~/code/amlhive1/`
