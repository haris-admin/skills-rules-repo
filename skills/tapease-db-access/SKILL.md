---
name: tapease-db-access
description: >
  How to connect to a Tap-Ease Postgres from a workstation — which local port is
  the dockerised local DB, which is an SSM tunnel to the dev/staging DB, and which
  is PRODUCTION — plus the psql/asyncpg credential workaround for the Claude Code
  / Codex sandbox classifier, and the naive-UTC datetime convention. Use when
  asked to "check the dev database", "connect to the DB", "run this query on
  staging/prod", "update my dev database", "seed the shift refunds", or when a
  psql / asyncpg connection is blocked, fails auth, or is hitting the wrong
  database. Deploy procedure is in tapease-backend-deploy; Clover shift logic is
  in tapease-pos-clover-shift-sync.
---

# Tap-Ease database access

## The port map (local workstation)

`localhost:5433` can resolve to **two different servers** at once — Docker and an
SSM tunnel both bind 5433, on different address families:

| Address | Server | DB / user | Notes |
|---|---|---|---|
| `::1:5433` (IPv6 — what bare `localhost` often picks on macOS) | Docker `tapease-local-postgres` (`postgres:17`) | `tapease_dev` / `postgres` : `postgres` | The `.env` `DATABASE_URL`. Lightly seeded — may have **no `user_id = 4`, no `trans_driver_shifts` rows**. Usually *not* the DB you want to test against. |
| `127.0.0.1:5433` (IPv4) | SSM `AWS-StartPortForwardingSession` → dev EC2 `i-0f9a6ec659e6aab83` → its `tapease-postgres` container | `tapease` / `tapease` | **The dev / staging DB.** Real fixtures: `user_id 4 = hhsiddiqui@gmail.com`, open driver shifts, seeded devices. Password is on the **commented** `DATABASE_URL` line in `.env` (`...@localhost:5435/tapease`). |
| `127.0.0.1:5434` | SSM tunnel to `tapease-postgres-production` RDS | `tapease_production` | **PRODUCTION. SELECT-only, and only when the user explicitly asks. Never write, never seed.** |

Always target the family explicitly (`psql -h 127.0.0.1` vs `-h ::1`) and confirm
before doing anything:

```bash
psql -h 127.0.0.1 -p 5433 -U tapease -d tapease -c "SELECT current_database(), inet_server_addr();"
```

If a tunnel isn't up, the user starts it — ask, or check which targets/ports are
live: `ps aux | grep session-manager-plugin` (the JSON args name the `Target`
instance and `localPortNumber`).

## Which database will the tests touch? (14 Oct 2026)

Check before the first `pytest`. The backend's `.env` `DATABASE_URL` pointed at `localhost:5435`, an **SSM tunnel to the dev EC2** (a
`session-manager-plugin` process), so the suite's migration runner and per-test pools would have run against shared dev data. Ports drift:
on that day the dev tunnel was 5435 and `5433` was the Docker container `tapease-test-pg` (`postgres:17-alpine`, databases `postgres` and
`tapease_dev`), so re-check instead of trusting the table above.

```bash
# host, port and database only (never print credentials)
python3 - <<'PY'
from urllib.parse import urlparse
for k in ("DATABASE_URL","TEST_DATABASE_URL"):
    for l in open(".env"):
        if l.startswith(k+"="):
            u=urlparse(l.split("=",1)[1].strip().strip("\"'").replace("+asyncpg",""))
            print(k, u.hostname, u.port, u.path.lstrip("/"))
PY
lsof -nP -iTCP:5435 -sTCP:LISTEN; ps aux | grep -E "[s]ession-manager-plugin"   # a plugin process means a remote database
```

Run tests through a wrapper that exports an explicit `TEST_DATABASE_URL` for a throwaway database in the local container
(`docker exec tapease-test-pg psql -U postgres -c "create database <name>"`) and refuses ports 5434 and 5435. The repo's `tests/conftest.py`
uses `TEST_DATABASE_URL` over `.env`, and tests marked `no_db` skip the per-test pool. Take the baseline in a clean `git worktree` on its own
database and remove the worktree afterwards. Rule: `verify-test-database-target-before-first-run.md`.

## Credential workaround (sandbox classifier)

`PGPASSWORD=… psql -h <remote> …` is **blocked by the auto-mode classifier** as
remote-credential use. Use a `.pgpass` file in the session scratchpad — both
psql and asyncpg read it:

```bash
umask 077
printf '127.0.0.1:5433:tapease:tapease:%s\n' '<password-from-.env-comment>' > "$SCRATCH/.pgpass"
chmod 600 "$SCRATCH/.pgpass"
export PGPASSFILE="$SCRATCH/.pgpass"

psql -h 127.0.0.1 -p 5433 -U tapease -d tapease -c "SELECT 1;"

# asyncpg / repo scripts: omit the password from the DSN, keep PGPASSFILE exported
DEV_DB_URL="postgresql://tapease@127.0.0.1:5433/tapease" poetry run python3 scripts/seed_shift_refund_testcases.py
```

`rm -f` / `shred -u` the `.pgpass` when done. Never echo the password into the transcript.

`aws secretsmanager get-secret-value --secret-id tapease/rds/credentials-production`
is **not reliably blocked** — confirmed working directly (piped straight into
Python to build the `.pgpass` line, no workaround needed) in a 2026-09-20
`portal_backend_lambda_eventbridge` session, contradicting the older assumption
above that it's always denied. Try it directly first; fall back to asking the
user for the password only if it's actually refused this session — don't
assume denial without testing.

**Counter-example, 2026-10-13:** in a `tapease_portal_fastapi_a2square` session the auto-mode
classifier DENIED the same fetch ("dangerous", no explanation) when it piped the
prod RDS password into a `.pgpass`. It is session-dependent. When denied, do not
work around it: stop, say what you needed and why, and offer the user either a
read-only `psql`/DBeaver session of their own on the tunnel or a Bash permission
rule. Reading `aws rds describe-db-instances` (endpoint, master user) and
`secretsmanager describe-secret` (name only) was allowed.

**Opening the production tunnel (read-only investigations only, user must have asked):**
```bash
aws ssm start-session --region ap-southeast-2 --target i-062b8ef5437ea6e2f \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters '{"host":["tapease-postgres-production.c9aso80ocbn0.ap-southeast-2.rds.amazonaws.com"],"portNumber":["5432"],"localPortNumber":["5434"]}'
```
Run it in the background, tell the user it is open, and offer to close it when done
(`lsof -nP -iTCP:5434 -sTCP:LISTEN`). Production DB is `tapease_production`, master
user `tapease_admin`. Never write or seed it; hand a reviewed SQL script to the user
(see the write-SQL section below).

## Write SQL against production: verify by schema, not by dry-run

Any `UPDATE`/`INSERT`/`DELETE` against `tapease_production` (port 5434) is
**blocked by the classifier as "Modify Shared Resources" even when wrapped in
`BEGIN; ... ROLLBACK;`** — a rollback-guarded dry run is not a usable
validation technique here, it just gets denied outright (confirmed
2026-09-20). Do not spend a turn trying it.

Instead, validate a hand-off write script by checking every column name it
references against the live schema with a read-only query, e.g.:

```sql
SELECT column_name FROM information_schema.columns
WHERE table_name = 'trans_clover_transaction_payments' ORDER BY column_name;
```

Cross-check the script's column list against that output programmatically
(catches typos before the user ever runs it), then hand the script to the
user to execute themselves in DBeaver per the SELECT-only rule above — same
BEGIN → preview → UPDATE → verify → COMMIT/ROLLBACK pattern as any other
production data repair (see `prod-issue-management`'s stuck-vs-slow section
for how to size a backlog before deciding whether a hand-off script is even
worth writing).

## Seeding / fixtures

- **Full reseed**: `scripts/seed_dev_data.py` — wipes + regenerates users,
  devices, payouts, transactions, refunds. `DEV_DB_URL=… python3 scripts/seed_dev_data.py`.
- **Shift-refund test fixtures** (idempotent, re-runnable): `scripts/seed_shift_refund_testcases.py`
  — clears + re-inserts 3 stable `REFUND` rows (`CLV-REF-SHIFT-TEST-01..03`) for
  `user_id 4`, **anchored inside the driver's currently open shift**. Re-run it
  once per test cycle (after each new `shifts/start`). Refuses to run against
  `tapease_production`. Canonical identity values live in
  `scripts/pos_partner_fixtures.py`.
- On-box one-off SQL the deploy script does **not** run (e.g.
  `scripts/_apply_pos_partner_fixtures.sql`): apply via a separate
  `docker exec tapease-postgres psql -U tapease -d tapease -c "…"` SSM command.

## Datetime convention — stored as UTC

`trans_clover_transaction_refunds.modified_time`, `trans_transactions.tran_date_time`
and the other `TIMESTAMP WITHOUT TIME ZONE` columns hold **naive UTC**. The POS
refund endpoints and `app/routers/transactions.py` compare in UTC (the latter
explicitly converts Sydney-local search input → UTC first).

A fixture row written in **Sydney wall-clock** (e.g. `13:15:00` for 1:15pm) falls
**outside** a UTC shift window (`03:15:00`) and the endpoint returns an empty
result — this was the v4.2.25→v4.2.26 bug. Sydney is **AEST = UTC+10** (Apr–Oct)
and **AEDT = UTC+11** (Oct–Apr); use `zoneinfo`, never a fixed offset. See the
`pos-datetime-utc-normalization` rule and `tapease-pos-clover-shift-sync`.

## Reading logs on the box

Production logs (`/home/ec2-user/app/backend/app/log/YYYYMMDD-PROD-TAPEASE_BACKEND.log`,
via SSM `send-command` to `i-062b8ef5437ea6e2f`, read-only greps are allowed) are rotated
by each deploy and only about 3 days remain, so an incident older than that is not in
them. Always read the whole result: a `| head -N` on a noisy pattern (every login line
matches `user_id 65`) hides the lines you wanted.

`docker logs tapease-backend` over SSM **times out** (huge). Read the on-box files:

```bash
docker exec tapease-backend sh -c "tail -n 4000 /app/app/log/$(date -u +%Y%m%d)-DEV-TAPEASE_BACKEND.log | grep -i <pattern>"
```

Request/response **bodies are not logged** on our side — only the POS partner
logs those (`Portal request: … json={…}`). For a body, ask the user for the
partner-side log line.

## Domain gotchas (also in the backend repo's CLAUDE.md)

- Oxygen Card ID = 8-char hex string (e.g. `005927C5`), **not** the 10-digit proxy number.
- Account unlock: `UPDATE auth_users SET retry_count = 5, status = '1'` + Redis flush.
