# Queue & backlog verification (background worker with no read API)

Use when you must answer "is any work queued / was this picked up / why not?" for a worker whose only
interface is a claim endpoint (often POST-only, `204` = nothing to do). The worker's silence and its
log both conflate several states, so the answer comes from the store the queue lives in.

## Order of checks (cheapest discriminator first)

1. **Queue depth by state.** `select state, count(*) from <jobs_table> group by state`. Exactly one
   state is claimable (`PENDING`); anything `IN_PROGRESS` is a live or leaked claim (a lease that
   expired with nobody watching is invisible to a claim-only consumer — it is never offered again).
2. **Every job, newest first**, with attempts, worker run id, error code and created/lease/completed
   timestamps. This is the history the API cannot show you.
3. **Items that produced NO job**: `left join` the producing table (cases, orders, documents) to the
   jobs table on the origin key and select where the job count is zero. This single query is what
   separates "queued and handled" from "never enqueued".
4. **The producer's enqueue CONDITION**, read in source: `if <prerequisite>:` guards are the usual
   answer. A row that exists with that prerequisite NULL means no work item was ever created — report
   the missing prerequisite, not a consumer failure. Check for a second guarded path (a legacy/fallback
   branch usually requires the same prerequisite, so it is not a fallback at all).
5. **Schema/migration drift** — see below.
6. **The audit/event ledger in the window** (`action_code`, `outcome`, `actor_id`, `occurred_at`):
   rows for the API's no-work path prove it was reachable at that time; their ABSENCE proves it was not.
   Cheapest way to separate "service down" from "worker refused" from "nothing polled".

## Schema drift: a DB behind the migration head reads as a broken feature

Compare `select version_num from <alembic|migration_version table>` against the migration files present
in the tree. A store sitting behind head (observed: staging on `016_case_lifecycle_states` while the
tree carried `017_intake_integrity`, `018_case_drafts`, `019_intake_idempotency`) is missing exactly
the columns and tables the current code expects — an absent column, an empty exceptions table — which
presents as "the feature does not work" when the real finding is "this environment was never
migrated". Two corollaries:

- A row that EXISTS while lacking a column the current model requires is evidence the process that
  wrote it is older than the working tree — do not reason about its behaviour from the current source.
- An expected-but-EMPTY table (exception rows, contact-attempt rows) is a finding in itself: the path
  that writes it is not running here.

## Probe recipe (relational, throwaway, read-only)

Write a temporary script next to the app's env file, run it with the interpreter that has the driver
(usually the app's own venv — the agent runtime's python often lacks psycopg2), then delete it:

```python
import pathlib, psycopg2
ENV = pathlib.Path(__file__).with_name(".env")
url = [l.split("=", 1)[1].strip().strip('"').strip("'").replace("+psycopg2", "")
       for l in ENV.read_text(errors="replace").splitlines()
       if l.strip().startswith("DATABASE_URL=")][0]
con = psycopg2.connect(url)
con.set_session(readonly=True, autocommit=True)   # a probe must not be able to write
```

Traps that cost real time:

- **Wrap EVERY query in try/except + `con.rollback()`** and print the failure. Guessed column names
  are normal (`cases` had no `merchant_name`, `transactions` had no `merchant_id`) and one bad guess
  must not hide the rest of the answer.
- **Pass `None`, never `()`**, as params: psycopg2 interpolates whenever args is not None, so a
  literal `%` in a `LIKE` pattern raises `IndexError: tuple index out of range`.
- **Take "when" from the store's clock**, rendering local time in the query
  (`at time zone '<zone>'`) — a WSL shell clock can be days off, and the whole finding is often a
  timestamp comparison.
- **Resolve which store you are actually reading.** The app's env file decides it (a staged
cloud
  database vs a local container), so a case created against another environment is simply not in the
  table — say so rather than concluding it was never created.
- **Delete the script afterwards** — it lives in a repo other lanes are editing.

## Reporting rules

- Report the CAUSE, not a verdict on the consumer: empty queue / prerequisite NULL / crons paused /
  worker refusing to start / store behind migration head. "Zero jobs" alone is not a finding.
- Name the store you read (which env file, which host) and keep only the fields the report needs.
  A probe can see personal data (names, identity, amounts, free text); a report must not.
- When the consumer is paused or stalled on a config gate, say that explicitly — a user asking "was my
  work picked up" needs to know the difference between "no work existed" and "work existed and the
  worker was off".
