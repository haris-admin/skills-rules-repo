# Sentry Debug & Investigation Notes (July 2026)

## Token Scope Limitation

The `SENTRY_AUTH_TOKEN` has only `project:read` scope. It cannot:
- List issues via `/issues/` (HTTP 403)
- Get issue details

It CAN:
- Get project info via `/projects/{org}/{project}/`
- Get stats via `/stats/?stat=received`
- **Get event details via `/events/`** ← the workaround

## ⚠️ CRITICAL: Time Window Trap (Jul 8, 2026 Fix)

### The `/events/` endpoint defaults to 14+ days

Calling `/events/?full=true&limit=10` with **no `statsPeriod` parameter** returns events from the **last 14+ days** by Sentry API default. This means every 4x daily monitor run fetches and reports the **same old errors** regardless of when they occurred.

**Always pass `&statsPeriod=10h`** to scope the query to the last N hours:

```
/events/?full=true&limit=10&statsPeriod=10h
```

Valid formats: `10h`, `24h`, `7d`, `14d`, or `start=ISO&end=ISO` timestamps.

### The `/stats/` endpoint resolution matters

```python
# WRONG — 24h window for 6-hourly cron runs:
stats = http_get(".../stats/?stat=received&resolution=1d")
event_count = int(stats[0][1])  # single bucket, stale across 4 runs

# CORRECT — 10h window matching CloudWatch lookback:
since_ts = int((NOW.timestamp() - 10 * 3600))
stats = http_get(".../stats/?stat=received&resolution=1h&since={since_ts}")
event_count = sum(int(b[1]) for b in stats if len(b) >= 2)
```

Key points:
- `resolution=1d` = one bucket per day (24h window) — too coarse for 6-hourly runs
- `resolution=1h` + `since={epoch}` = precise hourly buckets within the window
- Always **sum the buckets**, don't just take `stats[0][1]` — with `resolution=1h` you get up to 10 buckets

### The Hidden-Timestamp Bug

The Sentry API returns `dateCreated` on each event but many scripts capture it and **never display it** in the output. If you're already fetching it:

```python
date = evt.get("dateCreated", "")[:16]
```

**Print it.** Without timestamps in the output, the user has no way to distinguish between a 5-minute-old crash and a 5-day-old stale event that keeps being re-reported:

```python
lines.append(f"      🔴 [ERROR] {title} ({count}x) — {first_seen}")
```

## The Count Discrepancy Trap

The `/stats/` endpoint can report a misleadingly low count while `/events/` returns many events. This happens because:
- `/stats/` with `resolution=1d` bucket boundaries can exclude recent events
- The aggregation window doesn't align with the actual lookback

**Always fetch actual events** via `/events/` for accurate alerting, not just stats.

## CRITICAL: Legacy Monitor Sentry False-Alert Bug (Jul 9, 2026)

**Signal:** The legacy `pluto_fleet_monitor.py` (cron job `a0b1f0f642af`) produces 30+ Sentry alerts per cycle — ProgrammingError x96, Brevo failures, Google Maps errors, TypeErrors, Vercel module errors — but NONE of these exist when queried directly via the Sentry `/events/` API with a 48h window.

**Root cause:** Two compounding bugs in `pluto_fleet_monitor.py`:

1. **`/issues/` endpoint returns HTTP 403 then silent fallback.** The legacy monitor calls the `/issues/` endpoint which requires `event:read` scope. The token has only `project:read`. The script silently catches the 403 and falls back to... nothing useful — but the code path that renders "alert counts" does NOT fall back; it continues displaying whatever data it parsed before the 403.

2. **Lifetime aggregate counts displayed as windowed data.** The issue objects returned by Sentry (when the endpoint works) have a `count` field that represents the **total events in the issue group's lifetime**, NOT events in the queried window. The legacy monitor displayed this lifetime count as if it were a 24h snapshot, making it look like 96 ProgrammingErrors occurred today when they actually happened over days or weeks.

**How to verify against the live API:**
```bash
# Get actual events in the last 48h — this is the source of truth
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://sentry.io/api/0/projects/amlhive-pty-ltd/python-fastapi/events/?full=true&limit=50&statsPeriod=48h"
```

**Fix applied in amlhive_prod_monitor.py:** Uses only the `/events/` endpoint with `statsPeriod=10h`, never `/issues/`. Each event's `dateCreated` timestamp is displayed. Zero events returned = zero reported.

**Recommended:** Disable the legacy monitor cron jobs. It cannot produce correct Sentry data with the current token scope. The new monitor covers all the same checks.

## SSM Container Audit Pattern

When you need to verify what image is actually running on the backend EC2:

1. **Set up the right AWS creds** — the shell default may point at TapEase (707843605914), not AML Hive (560205084533):
   ```bash
   grep -E 'AWS_ACCESS_KEY_ID_AMLHIVE|AWS_SECRET_ACCESS_KEY_AMLHIVE' /mnt/c/Users/habib/.hermes/.env
   export AWS_ACCESS_KEY_ID=...
   export AWS_SECRET_ACCESS_KEY=...
   export AWS_DEFAULT_REGION=ap-southeast-2
   aws sts get-caller-identity  # Verify Account: 560205084533
   ```

2. **Send SSM command** to check container creation time and image tag:
   ```bash
   CMD_ID=$(aws ssm send-command --instance-ids i-0abe6a7923fa0dec2 \
     --document-name AWS-RunShellScript \
     --parameters '{"commands":["docker inspect amlhive-app-1 --format '"'"'{{.Created}}|{{.State.StartedAt}}|{{.Config.Image}}'"'"'"]}' \
     --output json --query 'Command.CommandId' --output text)
   sleep 8
   aws ssm list-command-invocations --command-id "$CMD_ID" \
     --details --query 'CommandInvocations[0].CommandPlugins[0].Output' --output text
   ```

3. **Interpret results:**
   - Container Created time vs deploy time → was the container restarted after the fix?
   - Image tag (`:latest` vs sha-pinned) → is it using the expected build?
   - Compare `docker images --digests` output to ECR registry to verify which images are local

## Known Real Error Signatures (July 2026)

| Error | Source | Impact | Since |
|-------|--------|--------|-------|
| `UndefinedColumnError: column clients.identity_edited_at does not exist` | ARQ cron job | 20+ hourly failures, DB schema mismatch | 06 Jul |
| `BrevoIpBlockedError: IP not in Authorised IPs` | Brevo email service | Signup emails blocked | 07 Jul |
| `InvalidTextRepresentationError: audit_action_type_enum` | PATCH /api/v1/clients | HTTP 500 | 06 Jul |
| `Failed to decrypt PII: Invalid token` | PII encryption module | Data retrieval failures | 05 Jul |
| `HTTPException: Blog post temporarily unavailable` | R2 bucket | Blog missing | 05 Jul |
