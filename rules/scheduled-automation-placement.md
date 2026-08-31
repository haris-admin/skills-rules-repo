# Scheduled/automated task placement: GitHub Actions vs. Pluto (all agents)

Applies whenever proposing new recurring or scheduled automation in this repo — a lint check, a
test suite, a security scan, a metrics report, a monitoring probe, or anything else meant to run
without a human triggering it each time.

## Why this exists

C411 (13 Aug 2026, Pluto's daily/weekly quality-and-review loop) nearly duplicated
`scheduled-audit.yml`'s already-correct, already-scheduled backend-unit/RLS-integration/frontend
test execution onto a second, independently-built pipeline on Pluto's WSL/Docker machine, before
the duplication was caught mid-design. `scheduled-audit.yml` already carries a hard-won fix
(issue-185/C134/C135's non-superuser RLS role — a Postgres superuser silently bypasses RLS, so
every `-m integration` assertion run against one is decoration, not evidence) that a second,
independent implementation would have had to re-derive from scratch, in a second place, with no
guarantee it gets the same fix right the first time. Generalise the reasoning here so a future
proposal starts from the right split instead of re-deriving it under time pressure.

## The checklist

1. **Read `.github/workflows/*.yml` in full before proposing new automation** — specifically check
   for an existing `on: schedule:` cron, not just `workflow_dispatch`. `scheduled-audit.yml`
   (Tue/Fri 04:00 UTC) already covers backend unit + RLS-integration + frontend tests unattended.
   Assuming "nothing runs this automatically" without actually reading the workflow files is the
   exact mistake this doc exists to prevent.
2. **GitHub Actions owns execution that needs an ephemeral service container** (Postgres, Redis, or
   similar). This is what its `services:` key is built for. Reproducing that elsewhere means
   reproducing every correctness fix already baked into the existing workflow, starting with the
   RLS-superuser-bypass trap above.
3. **Pluto (or any other agent-run cadence) owns judgment, LLM calls, and read-only file/dependency/
   secret scanning** — things that don't need a disposable database, and that benefit from an agent
   that can triage a finding's severity and draft a `prod_issues/` entry rather than just exit
   nonzero into a log nobody reads until asked.
4. **An agent reads a CI run's result; it does not re-run the CI job.** Use `gh run list
   --workflow=<file> --limit 1 --json conclusion,headSha,createdAt` (the same mechanism Pluto's
   existing hourly backend-version check already uses against the "Deploy Backend to EC2 (AWS)"
   workflow) rather than re-executing `pytest`/`npm test` on a second machine. Two independent
   implementations of the same test suite is a maintenance and correctness liability, not
   redundancy-as-safety — they will eventually disagree, and nothing says which one is right.
5. **Moving a rule marked 🔒 blocking (e.g. the Lighthouse performance gate) from a synchronous
   pre-merge/scheduled gate to an async report is a material weakening of the guarantee, not a
   neutral relocation.** It changes "we know before it ships" to "we'll find out within some window
   after it shipped." This needs its own explicit, dated human decision — never silently
   reinterpreted as "just moving where it runs." If the destination doesn't actually replace the
   guarantee (e.g. it monitors a live URL instead of gating a pending PR), say so explicitly rather
   than implying equivalence.
6. **Spread heavy/from-scratch scans across different days and times, clear of existing crons.** A
   full whole-repo secret/dependency/IaC scan can plausibly run past the gap between two nearby
   scheduled slots. Check the destination's existing cadence table (e.g.
   `docs/pluto_agent_instructions.md`'s Operating Cadence table) for collisions before picking a
   time — don't just pick a round number and assume it's clear.

## Open cases tracked under this pattern

| Change | What moved | Where it landed |
|---|---|---|
| C411 | Code review, dependency/secret/IaC security scan, DORA delivery metrics, live-URL Lighthouse monitoring | Pluto (new judgment/analysis tasks) — test execution stayed on `scheduled-audit.yml`, not duplicated |
| CRAP score (23 Aug 2026) | Weekly Python change-risk scan (`scripts/crap_score.py`) | Pluto Monday 10:30 Australia/Sydney — advisory log only; pytest/coverage regeneration stays off Pluto (`scheduled-audit.yml` remains the test runner) |
| C464 | Ref-DB SQLite optimization & change detection | Detection stays server-side (Pluto-triggered); `optimize_ref_db` → ARQ cron (Sun 04:30 Sydney); `prod-ref-sync-age-probe` → GitHub Actions |

Add a row here whenever this pattern applies to a new proposal, so the next reader doesn't have to
re-derive the split from scratch.
