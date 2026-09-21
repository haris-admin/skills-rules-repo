# Diagnosing periodic Lambda duration spikes on `tapease-clover-sync-production`

Worked methodology from a real investigation (2026-09-20/21, `portal_backend_lambda_eventbridge`)
that found and fixed a genuine root cause — reusable for any future duration anomaly on this
function or a similarly-structured one.

## Step 1: confirm the pattern is real via the Duration metric

```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda --metric-name Duration \
  --dimensions Name=FunctionName,Value=tapease-clover-sync-production \
  --start-time <ISO> --end-time <ISO> --period 300 \
  --statistics Average Maximum --region ap-southeast-2 --profile default \
  --query "sort_by(Datapoints, &Timestamp)[].{t:Timestamp, avg:Average, max:Maximum}" --output table
```

Widen to 24h at `--period 900` to see whether spikes are truly periodic/recurring vs. a one-off —
don't conclude "regular pattern" from a short window.

## Step 2: `print()` survives any LOG_LEVEL; `logger.info()` does not

This codebase mixes `print()` (in `app/services/base_transformation.py` and elsewhere — always
visible in CloudWatch regardless of log level) with `logger.info()` (suppressed whenever
`LOG_LEVEL=WARNING`, which is the production default). A large silent gap between Lambda `START`
and the first `print()`-based log line (e.g. `--- Starting Silver Devices Transformation ---`) means
the suppressed phase — usually Bronze sync — is where the time is going, but the per-endpoint detail
inside it is invisible until you raise the log level.

```bash
# Confirm current level
aws lambda get-function-configuration --function-name tapease-clover-sync-production \
  --region ap-southeast-2 --profile default --query "Environment.Variables.LOG_LEVEL"
```

## Step 3: temporarily raise LOG_LEVEL to INFO (get explicit approval first — live prod config change)

```bash
# Save the full current env first -- update-function-configuration REPLACES the whole map
aws lambda get-function-configuration --function-name tapease-clover-sync-production \
  --region ap-southeast-2 --profile default --query "Environment.Variables" --output json > /tmp/env_backup.json

python3 -c "
import json
env = json.load(open('/tmp/env_backup.json'))
env['LOG_LEVEL'] = 'INFO'
json.dump({'Variables': env}, open('/tmp/env_updated.json', 'w'))
"
aws lambda update-function-configuration --function-name tapease-clover-sync-production \
  --environment file:///tmp/env_updated.json --region ap-southeast-2 --profile default
```

Wait for a few cycles (5-min schedule), then pull the raw log window and reconstruct per-endpoint
timing by diffing consecutive `[parallel] Syncing endpoint: X` / `[parallel] Finished endpoint: X`
timestamps (these come from `main.py`'s `run_sync()` and were previously invisible). **Revert to
`WARNING` immediately after capturing enough — don't leave INFO on indefinitely**, using the exact
same two-command pattern with the original saved `/tmp/env_backup.json` (re-wrap it as
`{"Variables": ...}` before passing to `--environment file://`; the raw
`get-function-configuration ... Environment.Variables` output is NOT itself valid input to
`update-function-configuration` — it needs the `Variables` wrapper key).

## Known root cause found this way (fixed v0.8.13)

`sync_employee_shifts_recent()` in `app/sync_service.py` looped over all ~95 merchants
*sequentially* — one synchronous Clover API call per merchant — while every sibling Bronze endpoint
(`sync_endpoint()`) already parallelizes via `ThreadPoolExecutor`. It alone accounted for ~100s of a
~165s baseline cycle and was the exposure point for the periodic spikes (a sequential chain of ~95
synchronous calls accumulates any per-call latency variance linearly; a parallel batch absorbs it).
Fixed by splitting fetch (thread-safe, parallel) from DB write (serial, since SQLAlchemy sessions
aren't thread-safe) — see `2026-09-21_bronze_sync_duration_spikes.md` in that repo's `prod_issues/`
for the full write-up. If spikes recur after this fix, it is **not** this same cause — re-run this
methodology rather than assuming.

## General lesson

Before assuming a duration/latency anomaly is in "the interesting part" of a pipeline (the part with
visible, informative logs), check the parts that are *silent* first — silence usually means
suppressed logging, not zero work happening. A dominant, unparallelized loop hiding behind a
suppressed log level is easy to miss entirely if you only read what's already visible.
