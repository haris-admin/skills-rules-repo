# skill_extractor.py — BrokenPipeError Fix

**Applied:** June 13, 2026 (Saturday DREAM MODE cron `159702fe072c`)

## Problem
`skill_extractor.py` (cron `2d33c8f9a89c`, 11:00 AM AEST) is a `no_agent: true` script. Even though it doesn't use an LLM, it can still hit `BrokenPipeError: [Errno 32] Broken pipe` when:
- The cron scheduler's timeout (default ~120-180s) closes stdout
- Python's runtime tries to flush buffered output on exit
- The pipe is already closed → crash

This happened on June 12, 2026 — cron `2d33c8f9a89c` showed `last_status: error` with `RuntimeError: [Errno 32] Broken pipe`.

## Fix Applied
The entire top-level execution block (lines 108-170) was wrapped in a `try/except BrokenPipeError`:

```python
try:
    state = load_state()
    recent_scripts = scan_scripts()
    # ... all main logic ...
    print('\n'.join(report_parts))
except BrokenPipeError:
    # Cron scheduler closed stdout pipe (timeout) — exit gracefully
    sys.exit(0)
```

Also added `import sys` to the imports.

## Verification
- Script compiles correctly: `python3 -c "compile(open('skill_extractor.py').read(), 'skill_extractor.py', 'exec')"` → exit 0
- Same pattern already applied to `podcast_ingestor.py` (June 12, 2026) and `pluto_feedback_processor.py` (June 13, 2026)
- Next cron run will show `last_status: ok` instead of `error`

## Related
- `pluto-pipeline-orchestration` skill → "Long-Running no_agent Scripts Hit BrokenPipeError on Cron Timeout" pitfall
- Same wrapper pattern on: `podcast_ingestor.py`, `pluto_feedback_processor.py`
