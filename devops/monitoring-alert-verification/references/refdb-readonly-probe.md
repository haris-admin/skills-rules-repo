# Read-only reference-store probe (AMLHive production)

Use when you need to establish the TRUTH about a reference-data sync — or any serving
SQLite store — before believing, or escalating, a monitor alert.

Reads are safe. Writes are not: a write connection can contend with the sync's
`BEGIN IMMEDIATE` lock and stall production. Always open `mode=ro`.

## Step 1 — resolve the instance and the container

Discover by Name tag and **confirm the container exists** before probing. Never hardcode an
instance ID (instances get replaced) and never assume a container name from memory:

```bash
docker ps --format '{{.Names}}|{{.Image}}|{{.Status}}'
```

The backend is the t3.medium running `amlhive-api-1`; the frontend is a separate t3.small. If
a tag-filter query hands you an instance whose only container is the frontend, you resolved
the wrong host — re-list **all** running instances with their Name tags and pick by the
containers actually present, not by the filter alone.

## Step 2 — probe durable state (over SSM)

`aws ssm send-command --document-name AWS-RunShellScript` is asynchronous: poll
`aws ssm get-command-invocation` and read `StandardOutputContent`.

```bash
# schema, FTS column, row counts
docker exec amlhive-api-1 python3 -c 'import sqlite3; c=sqlite3.connect("file:/data/ref.db?mode=ro", uri=True); print("user_version", c.execute("PRAGMA user_version").fetchone()); print("companies_cols", [r[1] for r in c.execute("PRAGMA table_info(companies)")]); print("counts", list(c.execute("SELECT (SELECT count(*) FROM companies), (SELECT count(*) FROM business_names)")))'

# per-dataset sync state
docker exec amlhive-api-1 python3 -c 'import sqlite3; c=sqlite3.connect("file:/data/ref.db?mode=ro", uri=True); print(list(c.execute("SELECT dataset, source_record_count, last_checked_at, last_synced_at, sync_status FROM sync_state")))'

# sync history, newest first
docker exec amlhive-api-1 python3 -c 'import sqlite3; c=sqlite3.connect("file:/data/ref.db?mode=ro", uri=True); [print(r) for r in c.execute("SELECT * FROM sync_log ORDER BY rowid DESC LIMIT 6")]'
```

Credentials: `AWS_ACCESS_KEY_ID_AMLHIVE` / `AWS_SECRET_ACCESS_KEY_AMLHIVE` from the Windows
`.env`, region `ap-southeast-2`.

## Step 3 — read the output as a timeline, not a status

The load-bearing comparison is **durable timestamp vs alert time**:

- Serving counts matching the upstream counts = the data landed.
- `last_synced_at` LATER than the alert's run time = the job finished after the checker gave
  up → the alert was a false negative; fix the checker.
- A state row stuck in a recovery/error status with no fingerprint = no successful sync
  recorded → that one is real.

## Expected healthy shape

- `user_version` 1 (the v2 FTS rebuild is a separately gated migration), `fts_rowid` present
  on `companies`.
- `sync_state` rows idle, with `last_synced_at` ≈ `last_checked_at`.
- `companies_fts` / `business_names_fts` present plus the `fts_rowid` index.
- Legacy dataset names (`companies`, `business_names`) in `sync_log` are historical rows;
  current names are `asic-companies` / `asic-business-names`.
