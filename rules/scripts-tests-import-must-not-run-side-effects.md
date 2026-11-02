# A script that tests import must not do work on import

Applies to every Python or Node script that a test loads to check its functions.

## Why this exists

**3 Nov 2026, handledispute.** A test imported the video build script to test its secret loader. The script ended with a bare `main()`, so importing it started a three-minute ffmpeg build and the test run hung.

## Core Directives

1. End every script with `if __name__ == "__main__": main()` (or the Node equivalent).
2. Keep import time free of network calls, file writes, subprocesses and secret reads.
3. Put the loader under test behind small functions (`read_secret`, `read_env_files`, `load_env`) so a test can stub the boundary.
4. If a test run hangs, check what the imported module does at import time before blaming the test.

## Verification

`python -c "import path.to.script"` returns instantly and prints nothing.
